import factory
from django.contrib.auth import get_user_model
from pools.models import Pool, Team


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password')


class PoolFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Pool

    name = factory.Sequence(lambda n: f'Pool {n}')
    slug = factory.Sequence(lambda n: f'pool-{n}')
    owner = factory.SubFactory(UserFactory)


class TeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Team

    name = factory.Sequence(lambda n: f'Team {n}')
