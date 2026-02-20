import io
import base64
from django.db.models import Model as DjangoModel

from matplotlib.axes import Axes
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from learning.models import Assessment, QuestionPoolHasQuestion, UserAssessment
from learning.repositories import MirtDesignDataRepository

plt.switch_backend("agg")

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
        self.items_data = None

    def __items_design_data(self) -> dict:
        if not self.items_data:
            self.items_data = {}
            for mdd in self.mirt_design_data:
                for i, ih in enumerate(mdd.normalized_item_history):
                    self.items_data.setdefault(
                        ih,
                        {
                            "total_time": 0,
                            "total_answer": 0,
                            "total": 0,
                        },
                    )
                    self.items_data[ih]["total_time"] += mdd.item_time_history[i]
                    self.items_data[ih]["total_answer"] += mdd.response_history[ih - 1]
                    self.items_data[ih]["total"] += 1

            for k, v in self.items_data.items():
                self.items_data[k]["avg_time"] = v["total_time"] / v["total"]
                self.items_data[k]["avg_answer"] = v["total_answer"] / v["total"]

        return self.items_data

    def __annotate_bars(self, ax, bars):
        for bar in bars:
            ax.annotate(
                f"{bar.get_height():.2f}",
                xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="white"),
            )

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
                **question_data,
            }
            for item in question_pool_qs
            if (question_data := design_data.get(item.order))
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
                "last_theta": str(mdd.last_theta),
                "last_standard_error": str(mdd.last_standard_error),
                "completion_date": mdd.user_assessment.finished.strftime(
                    "%d/%m/%y - %H:%M:%S"
                ),
            }
            for mdd in self.mirt_design_data
            if mdd.user_assessment
        ]

    def __bar_chart(self, y_field: str, ylabel: str, title: str, color: str) -> str:
        fig, ax = self._get_subplots()
        items_data = self.__items_design_data()

        x_axis = []
        y_axis = []
        for k, v in sorted(items_data.items(), key=lambda x: x[0]):
            x_axis.append(str(k))
            y_axis.append(v[y_field])

        bars = ax.bar(x_axis, y_axis, color=color, edgecolor="black", hatch="\\")

        self.__annotate_bars(ax, bars)

        ax.set_xlabel("Questões")
        ax.set_ylabel(ylabel)
        ax.set_title(title)

        return self._fig_to_base64(fig)

    def average_correct_answer_per_question_chart(self) -> str:
        return self.__bar_chart(
            "avg_answer",
            "Acerto",
            "Média de resposta correta em cada questão",
            "#00ffaa",
        )

    def average_time_per_question_chart(self) -> str:
        return self.__bar_chart(
            "avg_time",
            "Tempo (s)",
            "Tempo médio de resposta em cada questão",
            "#00aaff",
        )


class AssessmentStudentDetailDataExtractor(BaseDataExtractor):

    def __init__(self, obj: UserAssessment):
        self.user_assessment = obj
        self.mirt_design_data = MirtDesignDataRepository.design_by_user_assessment(
            self.user_assessment.id
        )

    def _plot_chart(
        self,
        y_field: str,
        ylabel: str,
        title: str,
        color: str,
        precision: int = 1,
    ) -> str:
        fig, ax = self._get_subplots()

        x_axis = [str(i) for i in self.mirt_design_data.normalized_item_history]
        y_axis = getattr(self.mirt_design_data, y_field, [])

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
                bbox=dict(boxstyle="round,pad=0", fc="white", ec="white"),
            )

        ax.set_xlabel("Questões")
        ax.set_ylabel(ylabel)
        ax.set_title(title)

        return self._fig_to_base64(fig)


class AssessmentStudentDetailIrtDataExtractor(AssessmentStudentDetailDataExtractor):

    def questions_data(self) -> list:
        return [
            {
                "index": "Inicial",
                "response": False,
                "theta": str(self.mirt_design_data.theta_history[0]),
                "mse": str(self.mirt_design_data.standard_error_history[0]),
            }
        ] + [
            {
                "index": ih,
                "response": bool(self.mirt_design_data.response_history[i]),
                "theta": str(self.mirt_design_data.theta_history[i + 1]),
                "mse": str(self.mirt_design_data.standard_error_history[i + 1]),
            }
            for i, ih in enumerate(self.mirt_design_data.normalized_item_history)
        ]
        
    def charts_data(self) -> list:
        chart_functions = [
            self.time_history_chart,
            self.response_history_chart,
            self.theta_history_chart,
            self.standard_error_history_chart,
        ]
        return [(func.__name__, func()) for func in chart_functions]

    def _plot_multi_chart(
        self,
        y_field: str,
        ylabel: str,
        title: str,
        colors: list[str],
    ) -> str:
        y_axis = getattr(self.mirt_design_data, y_field, [])

        if not y_axis:
            return ""

        n_dimensions = len(y_axis[0])

        fig, axes = plt.subplots(
            n_dimensions,
            1,
            figsize=(8, 4 * n_dimensions),
            sharex=True,
        )

        if n_dimensions == 1:
            axes = [axes]

        x_axis = ["Inicial"] + [
            str(i) for i in self.mirt_design_data.normalized_item_history
        ]

        for dim in range(n_dimensions):
            ax = axes[dim]
            dim_values = [theta[dim] for theta in y_axis]
            color = colors[dim % len(colors)]
            ax.plot(
                x_axis,
                dim_values,
                marker="o",
                linestyle="-",
                color=f"{color}88",
                label=f"Dimensão {dim + 1}",
            )

            ax.scatter(x_axis, dim_values, color=color, zorder=3)

            for i, v in enumerate(dim_values):
                ax.annotate(
                    f"{v:.3f}",
                    xy=(x_axis[i], dim_values[i]),
                    textcoords="offset points",
                    xytext=(0, 5),
                    ha="center",
                    bbox=dict(boxstyle="round,pad=0", fc="white", ec="white"),
                )

            ax.set_ylabel(f"{ylabel} {dim + 1}")
            ax.set_title(f"{title} - Dimensão {dim + 1}")
            ax.grid(True)

        axes[-1].set_xlabel("Questões")

        fig.tight_layout()

        return self._fig_to_base64(fig)

    def time_history_chart(self) -> str:
        return self._plot_chart(
            "item_time_history",
            "Tempo (s)",
            "Histórico de Tempo por Questão",
            "#00AAFF",
        )

    def response_history_chart(self) -> str:
        return self._plot_chart(
            "normalized_response_history",
            "Acerto",
            "Histórico de Acerto por Questão",
            "#00FFAA",
            precision=0,
        )

    def theta_history_chart(self) -> str:
        return self._plot_multi_chart(
            "theta_history",
            "theta",
            "Histórico de Theta por Questão",
            ["#ffaa00", "#5500ff", "#00ff99", "#ff0077", "#cc00ff"],
        )

    def standard_error_history_chart(self) -> str:
        return self._plot_multi_chart(
            "standard_error_history",
            "mse",
            "Histórico de Erro Padrão por Questão",
            ["#aa00ff", "#00ff99", "#27c4b0", "#4a8fc5", "#6a5fd8"],
        )


class AssessmentStudentDetailCdmDataExtractor(AssessmentStudentDetailIrtDataExtractor):

    def questions_data(self) -> list:
        return [
            {
                "index": "Inicial",
                "response": False,
                "theta": str(self.mirt_design_data.theta_history[0]),
            }
        ] + [
            {
                "index": ih,
                "response": bool(self.mirt_design_data.response_history[i]),
                "theta": str(self.mirt_design_data.theta_history[i + 1]),
            }
            for i, ih in enumerate(self.mirt_design_data.normalized_item_history)
        ]
        
    def charts_data(self) -> list:
        chart_functions = [
            self.time_history_chart,
            self.response_history_chart,
            self.theta_history_chart,
        ]
        return [(func.__name__, func()) for func in chart_functions]
