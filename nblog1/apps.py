from django.apps import AppConfig


class Nblog1Config(AppConfig):
    name = 'nblog1'

    def ready(self):

        from . import signals


