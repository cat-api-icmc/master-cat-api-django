import uuid
import arrow
from django.db import models
from django.contrib.auth.models import AbstractUser

from core.models import SoftDeletableModel, TimeStampedModel


class User(AbstractUser, SoftDeletableModel):
    uuid = models.UUIDField("UUID", default=uuid.uuid4, editable=False, db_index=True)

    class Meta:
        db_table = "user"
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"


class StudentUser(User):
    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"
        proxy = True


class UserToken(TimeStampedModel):
    TOKEN_LIFETIME = 60 * 60 * 24 * 7  # 7 days

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)

    class Meta:
        db_table = "user_token"
        verbose_name = "Token"
        verbose_name_plural = "Tokens"

    def save(self, *args, **kwargs):
        self.token = uuid.uuid4()
        super().save(*args, **kwargs)

    def is_valid(self):
        return (
            arrow.get(self.modified).shift(seconds=self.TOKEN_LIFETIME) > arrow.utcnow()
        )


class UserPool(SoftDeletableModel):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
    name = models.CharField("Nome", max_length=255)
    users = models.ManyToManyField(
        User, related_name="pools", through="UserPoolHasUser"
    )
    assessments = models.ManyToManyField(
        "learning.Assessment", related_name="pools", through="UserPoolHasAssessment"
    )

    class Meta:
        db_table = "user_pools"
        verbose_name = "Turma"
        verbose_name_plural = "Turmas"

    def __str__(self) -> str:
        return self.name


class UserPoolHasUser(SoftDeletableModel):
    pool = models.ForeignKey(UserPool, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "user_pool_has_users"
        verbose_name = "Usuário na Turma"
        verbose_name_plural = "Usuários nas Turmas"

    def __str__(self) -> str:
        return f"{self.pool} - {self.user}"


class UserPoolHasAssessment(SoftDeletableModel):
    pool = models.ForeignKey(UserPool, on_delete=models.CASCADE)
    assessment = models.ForeignKey("learning.Assessment", on_delete=models.CASCADE)

    class Meta:
        db_table = "user_pool_has_assessments"
        verbose_name = "Avaliação da Turma"
        verbose_name_plural = "Avaliações das Turmas"

    def __str__(self) -> str:
        return f"{self.pool} - {self.assessment.name}"
