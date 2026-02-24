from user.models import UserPool, UserPoolHasUser


class UserPoolService(object):

    @classmethod
    def create_user_pool(cls, queryset: list) -> UserPool:
        pool = UserPool.objects.create(name="_")

        uphu = [UserPoolHasUser(pool_id=pool.id, user_id=user.id) for user in queryset]
        UserPoolHasUser.objects.bulk_create(uphu)

        return pool.save_fields(name=f"Turma_{pool.id}_{pool.created}")
