import io
import base64
from django.db.models import Model as DjangoModel

from matplotlib.axes import Axes
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from learning.models import Assessment, QuestionPoolHasQuestion, UserAssessment
from learning.repositories import MirtDesignDataRepository

# plt.switch_backend("agg")

CHART_RATIO = 16, 9
DPI = 120


class BaseDataExtractor:

    def __init__(self, obj: DjangoModel):
        pass

    def _get_subplots(self) -> tuple[Figure, Axes]:
        fig, ax = plt.subplots(figsize=CHART_RATIO)

        ax.yaxis.grid(color="gray", linestyle="dashed")
        ax.set_axisbelow(True)

        return fig, ax

    def _fig_to_base64(self, fig: Figure) -> str:
        with io.BytesIO() as buffer:
            fig.savefig(buffer, format="png", dpi=DPI, bbox_inches="tight")
            buffer.seek(0)
            plt.close(fig)
            return base64.b64encode(buffer.getvalue()).decode("utf-8")


class AssessmentResultDataExtractor(BaseDataExtractor):

    def __init__(self, obj: Assessment):
        self.assessment = obj
        self.mirt_design_data = MirtDesignDataRepository.designs_by_assessment(
            self.assessment.id
        )

    def __items_design_data(self) -> dict:
        if not hasattr(self, "items_data"):
            self.items_data = {}
            for mdd in self.mirt_design_data:
                for i, ih in enumerate(mdd.item_history):
                    self.items_data.setdefault(
                        ih,
                        {
                            "total_time": 0,
                            "total_answer": 0,
                            "total": 0,
                        },
                    )
                    self.items_data[ih]["total_time"] += mdd.item_time_history[i]
                    self.items_data[ih]["total_answer"] += mdd.response_history[i]
                    self.items_data[ih]["total"] += 1

            for k, v in self.items_data.items():
                self.items_data[k]["avg_time"] = v["total_time"] / v["total"]
                self.items_data[k]["avg_answer"] = v["total_answer"] / v["total"]

        return self.items_data

    def questions_data(self) -> list:
        question_pool_qs = QuestionPoolHasQuestion.objects.select_related(
            "question"
        ).filter(pool_id=self.assessment.pool_id)
        design_data = self.__items_design_data()
        return [
            {
                "id": item.question_id,
                "statement": f"{item.question.statement[:30]}...",
                "index": item.order,
                **design_data[item.order],
            }
            for item in question_pool_qs
        ]

    def students_data(self) -> list:
        return [
            {
                "id": mdd.user_assessment.user.id,
                "user_assessment_uuid": mdd.user_assessment.uuid,
                "name": mdd.user_assessment.user.name,
                "email": mdd.user_assessment.user.email,
                "score": mdd.score,
                "completion_time": mdd.user_assessment.completion_time,
                "last_theta": mdd.last_theta,
                "last_standard_error": mdd.last_standard_error,
                "completion_date": mdd.user_assessment.finished.strftime(
                    "%d/%m/%y - %H:%M:%S"
                ),
            }
            for mdd in self.mirt_design_data
            if mdd.user_assessment
        ]

    def average_correct_answer_per_question_chart(self) -> str:
        fig, ax = self._get_subplots()

        x_axis = []
        y_axis = []
        for k, v in sorted(self.__items_design_data().items(), key=lambda x: x[0]):
            x_axis.append(str(k))
            y_axis.append(v["avg_answer"])

        bars = ax.bar(x_axis, y_axis, color="#00ffaa", edgecolor="black", hatch="\\")

        for bar in bars:
            ax.annotate(
                f"{bar.get_height():.2f}",
                xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
            )

        ax.set_xlabel("Questões")
        ax.set_ylabel("Acerto")
        ax.set_title("Média de resposta correta em cada questão")

        return self._fig_to_base64(fig)

    def average_time_per_question_chart(self) -> str:
        fig, ax = self._get_subplots()

        x_axis = []
        y_axis = []
        for k, v in sorted(self.__items_design_data().items(), key=lambda x: x[0]):
            x_axis.append(str(k))
            y_axis.append(v["avg_time"])

        bars = ax.bar(x_axis, y_axis, color="#00AAFF", edgecolor="black", hatch="\\")

        for bar in bars:
            ax.annotate(
                f"{bar.get_height():.1f}",
                xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
            )

        ax.set_xlabel("Questões")
        ax.set_ylabel("Tempo (s)")
        ax.set_title("Tempo médio de resposta em cada questão")

        return self._fig_to_base64(fig)


class AssessmentStudentDetailDataExtractor(BaseDataExtractor):

    def __init__(self, obj: UserAssessment):
        self.user_assessment = obj
        self.mirt_design_data = MirtDesignDataRepository.design_by_user_assessment(
            self.user_assessment.id
        )

    def __plot_chart(self, y_axis: str, ylabel: str, title: str, color: str, precision: int = 1) -> str:
        fig, ax = self._get_subplots()

        x_axis = [str(i) for i in self.mirt_design_data.item_history]

        ax.plot(
            x_axis,
            y_axis,
            marker="o",
            linestyle="-",
            color=f"{color}88",
            label="Histórico",
        )

        ax.scatter(x_axis, y_axis, color=color, zorder=3)

        for i, v in enumerate(y_axis):
            ax.annotate(
                f"{v:.{precision}f}",
                xy=(x_axis[i], y_axis[i]),
                textcoords="offset points",
                xytext=(0, 5),
                ha="center",
            )

        ax.set_xlabel("Questões")
        ax.set_ylabel(ylabel)
        ax.set_title(title)

        return self._fig_to_base64(fig)

    def time_history_chart(self) -> str:
        return self.__plot_chart(
            self.mirt_design_data.item_time_history,
            "Tempo (s)",
            "Histórico de Tempo por Questão",
            "#00AAFF",
        )

    def response_history_chart(self) -> str:
        return self.__plot_chart(
            self.mirt_design_data.response_history,
            "Acerto",
            "Histórico de Acerto por Questão",
            "#00FFAA",
            precision=0
        )

    def theta_history_chart(self) -> str:
        return self.__plot_chart(
            self.mirt_design_data.theta_history[1:],
            "theta",
            "Histórico de Theta por Questão",
            "#FFAA00",
            precision=3
        )

    def standard_error_history_chart(self) -> str:
        return self.__plot_chart(
            self.mirt_design_data.standard_error_history[1:],
            "mse",
            "Histórico de Erro Padrão por Questão",
            "#AA00FF",
            precision=3
        )
