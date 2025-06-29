import io
import base64
import matplotlib.pyplot as plt
from learning.models import Assessment, QuestionPoolHasQuestion
from learning.repositories import MirtDesignDataRepository, AssessmentRepository

plt.switch_backend("agg")

CHART_RATIO = 16, 9
DPI = 120


class AssessmentResultDataExtractor:

    def __init__(self, assessment: Assessment):
        self.assessment = assessment
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
                "completion_date": mdd.user_assessment.finished.strftime('%d/%m/%y - %H:%M:%S')
            }
            for mdd in self.mirt_design_data
            if mdd.user_assessment
        ]

    def average_correct_answer_per_question_chart(self) -> str:
        fig, ax = plt.subplots(figsize=CHART_RATIO)

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

        with io.BytesIO() as buffer:
            plt.savefig(buffer, format="png", dpi=DPI, bbox_inches="tight")
            buffer.seek(0)
            plt.close(fig)
            return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def average_time_per_question_chart(self) -> str:
        fig, ax = plt.subplots(figsize=CHART_RATIO)

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

        with io.BytesIO() as buffer:
            plt.savefig(buffer, format="png", dpi=DPI, bbox_inches="tight")
            buffer.seek(0)
            plt.close(fig)
            return base64.b64encode(buffer.getvalue()).decode("utf-8")
