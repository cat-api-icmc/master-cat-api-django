import uuid

from django.db import models
from django.db.models.fields.files import ImageFieldFile
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.forms.models import model_to_dict
from django_ckeditor_5.fields import CKEditor5Field

from core.fields import AutoCreatedField, AutoLastModifiedField
from core.managers import SoftDeletableManager, SoftDeletableUserManager


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields.
    ...
    """

    created = AutoCreatedField(_("created"))
    modified = AutoLastModifiedField(_("modified"))

    class Meta:
        abstract = True


class ChangedModel(models.Model):

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(ChangedModel, self).__init__(*args, **kwargs)
        self.__initial = self._dict

    def save_fields(self, **kwargs):
        _keys = kwargs.keys()
        for field in _keys:
            setattr(self, field, kwargs[field])
        self.save(update_fields=_keys)
        return self

    @property
    def diff(self):
        d1 = self.__initial
        d2 = self._dict
        diffs = []

        for k, v in d1.items():
            v1 = v
            v2 = d2[k]
            if v1 != v2:
                if isinstance(v, ImageFieldFile):
                    v1 = str(v1)
                    v2 = str(v2)
                diffs.append((k, (v1, v2)))

        return dict(diffs)

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        return self.diff.keys()

    def get_field_diff(self, field_name):
        """
        Returns a diff for field if it's changed and None otherwise.
        """
        return self.diff.get(field_name, None)

    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in self._meta.fields])

    @property
    def get_admin_url(self):
        from django.urls import reverse
        from django.contrib.contenttypes.models import ContentType

        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse(
            "admin:%s_%s_change" % (content_type.app_label, content_type.model),
            args=(self.id,),
        )


class SoftDeletableModel(ChangedModel, TimeStampedModel):
    """
    An abstract base class model with a ``removed`` field that
    marks entries that are not going to be used anymore, but are
    kept in db for any reason.
    Default manager returns only not-removed entries.
    """

    removed = models.DateTimeField(null=True, default=None, editable=False)

    objects = SoftDeletableManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Saves model and set initial state.
        """
        super(SoftDeletableModel, self).save(*args, **kwargs)
        self.__initial = self._dict

    def delete(self, using=None, soft=True, *args, **kwargs):
        """
        Soft delete object (set its ``removed`` field to now).
        Actually delete object if setting ``soft`` to None.
        """
        if soft:
            self.removed = now()
            self.save(using=using)
        else:
            return super(SoftDeletableModel, self).delete(using=using, *args, **kwargs)


class SoftDeletableUserModel(SoftDeletableModel):

    objects = SoftDeletableUserManager()

    class Meta:
        abstract = True


class CKEditorModelMixin(object):

    def __init__(self, *args, **kwargs):
        super(CKEditorModelMixin, self).__init__(*args, **kwargs)
        self._ck_editor_fields = self.get_ck_editor_fields()

    @classmethod
    def get_ck_editor_fields(cls):
        return [
            field.name
            for field in cls._meta.fields
            if isinstance(field, CKEditor5Field)
        ]

    def convert_images_to_base64(self, field):
        import os
        import base64
        import urllib
        from bs4 import BeautifulSoup
        from pathlib import Path

        content = getattr(self, field)

        soup = BeautifulSoup(content, "html.parser")
        images = soup.find_all("img")

        for img in images:
            img_src = img.get("src")
            if "media/" in img_src:
                img_path = urllib.parse.unquote(os.getcwd() + img_src)
                if img_path and Path(img_path).exists():
                    with open(img_path, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode(
                            "utf-8"
                        )
                        img["src"] = f"data:image;base64,{encoded_string}"
                    os.remove(img_path)

        setattr(self, field, str(soup))

    def handle_ck_editor_fields(self):
        for field in self._ck_editor_fields:
            self.convert_images_to_base64(field)


class UploadQuestions(SoftDeletableModel):
    PROCESSING = "processing"
    FINISHED = "finished"
    ERROR = "error"

    STATUS_CHOICES = (
        (PROCESSING, "Processando"),
        (FINISHED, "Finalizado"),
        (ERROR, "Erro"),
    )

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PROCESSING)
    file = models.FileField(upload_to="upload")
    result = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "upload_questions"
        verbose_name = "Upload Questões"
        verbose_name_plural = "Uploads Questões"
