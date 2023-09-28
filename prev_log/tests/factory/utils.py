import factory

from prev_log.models import OrigemPrevisao


class OriginFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrigemPrevisao

    designacao = 1
