from django.db import models
from django.db.models.query import QuerySet
from django.utils.timezone import now
from django.contrib.auth.models import UserManager


class SoftDeletableQuerySetMixin(object):
    """
    QuerySet for SoftDeletableModel. Instead of removing instance sets
    its ``removed`` field to now.
    """

    def delete(self):
        """
        Soft delete objects from queryset (set their ``removed``
        field to now)
        """
        self.update(removed=now())


class SoftDeletableQuerySet(SoftDeletableQuerySetMixin, QuerySet):

    def bulk_create(self, objs, batch_size=None):
        from django.db.models.signals import post_save, pre_save

        for obj in objs:
            pre_save.send(self.model, instance=obj)

        res = super(SoftDeletableQuerySet, self).bulk_create(objs, batch_size)

        for obj in objs:
            post_save.send(self.model, instance=obj, created=True)

        return res


class SoftDeletableManagerMixin(object):
    """
    Manager that limits the queryset by default to show only not removed
    instances of model.
    """

    _queryset_class = SoftDeletableQuerySet

    def get_queryset(self):
        """
        Return queryset limited to not removed entries.
        """
        kwargs = {"model": self.model, "using": self._db}
        if hasattr(self, "_hints"):
            kwargs["hints"] = self._hints

        return self._queryset_class(**kwargs).filter(removed=None)


class SoftDeletableManager(SoftDeletableManagerMixin, models.Manager):

    def get_queryset(self):
        qs = super().get_queryset()
        select_related = getattr(self.model.Meta, "select_related_default", None)
        return qs if select_related is None else qs.select_related(*select_related)


class SoftDeletableUserManager(SoftDeletableManager, UserManager):
    pass
