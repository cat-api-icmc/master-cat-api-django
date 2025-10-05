from typing import List, Union
import uuid
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

from core.models import CKEditorModelMixin, SoftDeletableModel
from user.models import StudentUser
from datetime import timedelta


class AssessmentType(object):
    IRT_4PL = "4PL"
    IRT_3PL = "3PL"
    IRT_2PL = "2PL"
    IRT_1PL = "1PL"
    
    MIRT_4PL = "4PL"
    MIRT_3PL = "3PL"
    MIRT_2PL = "2PL"
    MIRT_1PL = "1PL"

    CDM_DINA = "DINA"
    CDM_DINO = "DINO"
    
    CDM_GDINA = "GDINA"

    CHOICES = (
        (IRT_4PL, "TRI - 4 Parâmetros"),
        (IRT_3PL, "TRI - 3 Parâmetros"),
        (IRT_2PL, "TRI - 2 Parâmetros"),
        (IRT_1PL, "TRI - 1 Parâmetro"),
        (MIRT_4PL, "TRI - 4 Parâmetros Multidimensionais"),
        (MIRT_3PL, "TRI - 3 Parâmetros Multidimensionais"),
        (MIRT_2PL, "TRI - 2 Parâmetros Multidimensionais"),
        (MIRT_1PL, "TRI - 1 Parâmetro Multidimensional"),
        (CDM_DINA, "CDM - DINA"),
        (CDM_DINO, "CDM - DINO"),
        (CDM_GDINA, "CDM - GDINA"),
    )

    @classmethod
    def is_irt(cls, type_: str) -> bool:
        return type_ in (
            cls.IRT_1PL,
            cls.IRT_2PL,
            cls.IRT_3PL,
            cls.IRT_4PL,
            cls.MIRT_1PL,
            cls.MIRT_2PL,
            cls.MIRT_3PL,
            cls.MIRT_4PL,
        )

    @classmethod
    def is_cdm(cls, type_: str) -> bool:
        return type_ in (cls.CDM_DINA, cls.CDM_DINO, cls.CDM_GDINA)


class Question(SoftDeletableModel, CKEditorModelMixin):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
    statement = CKEditor5Field("Enunciado")

    class Meta:
        db_table = "questions"
        verbose_name = "Questão"
        verbose_name_plural = "Questões"

    def __str__(self) -> str:
        return f"{self.pk} - {str(self.statement)[:10]}..."

    def save(self, *args, **kwargs):
        self.handle_ck_editor_fields()
        return super().save(*args, **kwargs)


class IRTParams(models.Model):
    """
    Fields used to store the parameters for the IRT models.
    ...
    """

    irt_difficulty = models.FloatField("Dificuldade", default=0.0)
    irt_discrimination = models.FloatField("Discriminação", default=1.0)
    irt_guess = models.FloatField("Chute", default=0.0)
    irt_upper_asymptote = models.FloatField("Assimptota Superior", default=1.0)
    irt_mparams = models.JSONField("Parâmetros Multidimensionais", default=list)

    class Meta:
        abstract = True


class CDMParams(models.Model):
    """
    Fields used to store the parameters for the CDM model: DINA and DINO
    ...
    """

    cdm_slipping = models.FloatField("Deslize", default=0.0)
    cdm_guessing = models.FloatField("Chute", default=0.0)
    cdm_mparams = models.JSONField("Parâmetros Multidimensionais", default=list)
    cdm_qmatrix = models.JSONField("Valores para a Matriz Q", default=list)

    class Meta:
        abstract = True


class QuestionParams(SoftDeletableModel, IRTParams, CDMParams):
    """
    Merge Class to store CAT metadata about a question.
    ...
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
    model = models.CharField(
        "Modelo",
        max_length=255,
        choices=AssessmentType.CHOICES,
        default=AssessmentType.IRT_3PL,
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="params"
    )

    class Meta:
        db_table = "question_params"
        verbose_name = "Parâmetros de Questão"
        verbose_name_plural = "Parâmetros de Questões"


class Alternative(SoftDeletableModel, CKEditorModelMixin):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
    text = CKEditor5Field("Texto")
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="alternatives"
    )
    is_correct = models.BooleanField("Correta", default=False)

    class Meta:
        db_table = "alternatives"
        verbose_name = "Alternativa"
        verbose_name_plural = "Alternativas"

    def __str__(self) -> str:
        return f"{self.pk} - {str(self.text)[:10]}..."

    def save(self, *args, **kwargs):
        self.handle_ck_editor_fields()
        return super().save(*args, **kwargs)


class QuestionPool(SoftDeletableModel):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
    name = models.CharField("Nome", max_length=255)
    questions = models.ManyToManyField(
        Question, related_name="pools", through="QuestionPoolHasQuestion"
    )
    super_pool = models.BooleanField("É um Super Pool?", default=False)

    class Meta:
        db_table = "question_pools"
        verbose_name = "Banco de Questões"
        verbose_name_plural = "Bancos de Questões"

    def __str__(self) -> str:
        return f"{self.pk} {self.name}"

    def __len__(self) -> int:
        return self.questions.filter(
            questionpoolhasquestion__removed__isnull=True
        ).count()


class QuestionSuperPool(QuestionPool):

    class Meta:
        verbose_name = "Super Banco de Questões"
        verbose_name_plural = "Super Bancos de Questões"
        proxy = True


class QuestionPoolHasQuestion(SoftDeletableModel):
    pool = models.ForeignKey(QuestionPool, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.PositiveIntegerField("Ordem", default=1)

    class Meta:
        db_table = "question_pool_has_questions"
        verbose_name = "Questão no Banco de Questões"
        verbose_name_plural = "Questões nos Bancos de Questões"


class CriteriaTypes(object):
    SEQ = "seq"
    RANDOM = "random"

    MI = "MI"
    MEPV = "MEPV"
    MLWI = "MLWI"
    MPWI = "MPWI"
    MEI = "MEI"

    KL = "KL"
    KLn = "KLn"

    IKLP = "IKLP"
    IKL = "IKL"
    IKLn = "IKLn"
    IKLPn = "IKLPn"

    DRULE = "Drule"
    TRULE = "Trule"
    ARULE = "Arule"
    ERULE = "Erule"
    WRULE = "Wrule"

    DPRULE = "DPrule"
    TPRULE = "TPrule"
    APRULE = "APrule"
    EPRULE = "EPrule"
    WPRULE = "WPrule"

    CHOICES = (
        (SEQ, "Sequencial"),
        (RANDOM, "Aleatório"),
        (MI, "MI - Máxima Informação"),
        (MEPV, "MEPV - Mínima Variância Posterior Esperada"),
        (MLWI, "MLWI - Informação Ponderada de Máxima Verossimilhança"),
        (MPWI, "MPWI - Informação Ponderada Máxima Posterior"),
        (MEI, "MEI - Informação Esperada Máxima"),
        (KL, "KL - Divergência Kullback-Leibler ponto a ponto"),
        (KLn, "KLn - Kullback-Leibler ponto a ponto com um valor delta decrescente"),
        (
            IKLP,
            "IKLP - Critérios de Kullback-Leibler Baseados em Integração com peso de densidade a priori",
        ),
        (IKL, "IKL - Critérios de Kullback-Leibler Baseados em Integração"),
        (IKLn, "IKLn - Versão ponderada com itens raiz-n"),
        (IKLPn, "IKLPn - Versão ponderada com itens raiz-n"),
        (DRULE, "DRULE - Determinante Máximo da Matriz de Informação"),
        (
            TRULE,
            "TRULE - Traço Máximo (potencialmente ponderado) da Matriz de Informação",
        ),
        (
            ARULE,
            "ARULE - Traço Mínimo (potencialmente ponderado) da Matriz de Covariância Assintótica",
        ),
        (ERULE, "ERULE - Valor Mínimo da Matriz de Informação"),
        (WRULE, "WRULE - Critérios de Informação Ponderada"),
        (DPRULE, "DPRULE - Para Drule"),
        (TPRULE, "TPRULE - Para Trule"),
        (APRULE, "APRULE - Para Arule"),
        (EPRULE, "EPRULE - Para Erule"),
        (WPRULE, "WPRULE - Para Wrule"),
    )


class AssessmentConfig(models.Model):
    """
    Fields used to store the configuration of an assessment.
    ...
    """

    type = models.CharField(
        "Tipo",
        max_length=255,
        choices=AssessmentType.CHOICES,
        default=AssessmentType.IRT_3PL,
    )

    # Critério de seleção de itens
    start_item = models.PositiveIntegerField(
        "Item Inicial",
        default=1,
        help_text="Caso o índice seja 0, o primeiro item será escolhido aleatoriamente.",
    )
    criteria = models.CharField(
        "Critério de Seleção",
        max_length=255,
        default=CriteriaTypes.SEQ,
        choices=CriteriaTypes.CHOICES,
    )

    # Critérios de parada
    min_sem = models.CharField(
        "Mínimo de SEM",
        max_length=255,
        default="0.3",
        help_text="Valor mínimo de erro padrão de medida. Esse campo aceita um único valor ou uma lista de valores separados por vírgula (,) em caso de teste multidimensional.",
    )
    delta_thetas = models.CharField(
        "Delta Thetas",
        max_length=255,
        default="0",
        help_text="Valor de diferença entre thetas. Esse campo aceita um único valor ou uma lista de valores separados por vírgula (,) em caso de teste multidimensional. O padrão '0' desabilita este critério de parada.",
    )
    thetas_start = models.CharField(
        "Thetas Iniciais",
        max_length=255,
        default="0",
        help_text="Valor inicial de thetas. Esse campo aceita um único valor ou uma lista de valores separados por vírgula (,) em caso de teste multidimensional.",
    )
    pattern_theta = models.CharField(
        "Padrão de Theta",
        max_length=255,
        default="0",
        help_text="Valor de theta inicial. Esse campo aceita um único valor ou uma lista de valores separados por vírgula (,) em caso de teste multidimensional.",
    )

    min_items = models.PositiveIntegerField("Mínimo de Itens", default=1)
    max_items = models.PositiveIntegerField("Máximo de Itens", default=10)
    max_time = models.PositiveIntegerField(
        "Tempo Máximo",
        default=None,
        null=True,
        blank=True,
        help_text="Tempo máximo em segundos. Deixe em branco para ilimitado",
    )

    class Meta:
        abstract = True

    def __get_number_or_list(self, value: str) -> Union[List[float], float]:
        values = list(map(float, value.split(",")))
        return values if len(values) > 1 else values[0]

    @property
    def min_sem_value(self) -> Union[List[float], float]:
        return self.__get_number_or_list(self.min_sem)

    @property
    def delta_thetas_value(self) -> Union[List[float], float]:
        return self.__get_number_or_list(self.delta_thetas)

    @property
    def thetas_start_value(self) -> Union[List[float], float]:
        return self.__get_number_or_list(self.thetas_start)

    @property
    def pattern_theta_value(self) -> Union[List[float], float]:
        return self.__get_number_or_list(self.pattern_theta)

    @property
    def fixed_question_count(self) -> int:
        return self.min_items if self.min_items == self.max_items else 0

    @property
    def is_irt(self) -> bool:
        return AssessmentType.is_irt(self.type)

    @property
    def is_cdm(self) -> bool:
        return AssessmentType.is_cdm(self.type)


class Assessment(SoftDeletableModel, AssessmentConfig):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
    name = models.CharField("Nome", max_length=255)
    active = models.BooleanField("Ativo", default=True)
    retry = models.BooleanField(
        "Permitir Repetição",
        default=False,
        help_text="Permite que o usuário repita a avaliação caso já tenha finalizado",
    )
    start = models.DateTimeField(
        "Início",
        default=None,
        null=True,
        blank=True,
        help_text="Deixe em branco para iniciar imediatamente",
    )
    finish = models.DateTimeField(
        "Fim",
        default=None,
        null=True,
        blank=True,
        help_text="Deixe em branco para não finalizar",
    )
    pool = models.ForeignKey(
        QuestionPool, on_delete=models.CASCADE, related_name="assessments"
    )

    class Meta:
        db_table = "assessments"
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"

    def __str__(self) -> str:
        return f"{self.pk} {self.name}"

    def __len__(self) -> int:
        return self.pool.questions.filter(
            questionpoolhasquestion__removed__isnull=True
        ).count()


class UserAssessment(SoftDeletableModel):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

    STATUS_CHOICES = (
        (IN_PROGRESS, "Em Progresso"),
        (COMPLETED, "Finalizado"),
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
    user = models.ForeignKey(
        StudentUser, on_delete=models.CASCADE, related_name="assessments"
    )
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="users"
    )
    status = models.CharField(
        "Status", max_length=255, choices=STATUS_CHOICES, default=IN_PROGRESS
    )
    next_index = models.IntegerField("Próximo Índice", default=0)
    design = models.TextField("Design", default=None, null=True, blank=True)
    finished = models.DateTimeField("Finalizado", default=None, null=True, blank=True)

    class Meta:
        db_table = "user_has_assessments"
        verbose_name = "Avaliação do Usuário"
        verbose_name_plural = "Avaliações dos Usuários"

    @property
    def completion_time(self) -> int:
        if self.finished and self.created:
            delta: timedelta = self.finished - self.created
            return int(delta.total_seconds())
        return 0


class MirtDesignData(SoftDeletableModel):
    user_assessment = models.ForeignKey(
        UserAssessment,
        on_delete=models.SET_DEFAULT,
        related_name="design_data",
        default=None,
        null=True,
        blank=True,
    )
    item_history = models.JSONField("Histórico de Itens", default=list)
    response_history = models.JSONField("Histórico de Respostas", default=list)
    theta_history = models.JSONField("Histórico de Theta", default=list)
    standard_error_history = models.JSONField(
        "Histórico de Erro Padrão do Theta", default=list
    )
    item_time_history = models.JSONField("Histórico de Tempo de Resposta", default=list)
    last_answer_time = models.DateTimeField("Última Resposta", default=None, null=True)

    class Meta:
        db_table = "mirt_design_data"
        verbose_name = "Dados de Design MIRT"
        verbose_name_plural = "Dados de Design MIRT"

    def __str__(self) -> str:
        if self.user_assessment:
            return f"{self.pk} | u: {self.user_assessment.user} | a: {self.user_assessment.assessment}"
        return f"{self.pk} - MIRT Design Data"

    def __last(self, iter: list) -> float:
        return iter[-1] if len(iter) else 0.0

    def __len__(self) -> int:
        return len(self.item_history)

    @property
    def score(self) -> float:
        return sum(self.response_history) / len(self.response_history)

    @property
    def last_theta(self) -> float:
        return self.__last(self.theta_history)

    @property
    def last_standard_error(self) -> float:
        return self.__last(self.standard_error_history)

    @property
    def last_item(self) -> int:
        return self.__last(self.item_history)

    @property
    def last_response(self) -> bool:
        return self.__last(self.response_history)

    @property
    def last_item_time(self) -> float:
        return self.__last(self.item_time_history)
