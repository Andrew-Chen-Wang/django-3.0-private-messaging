from django.apps import AppConfig


class PublicConfig(AppConfig):
    name = 'public'

    def ready(self):
        import public.signals  # noqa
