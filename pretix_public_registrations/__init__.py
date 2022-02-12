from django.utils.translation import gettext_lazy as _
try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")

__version__ = "1.4.0"


class PluginApp(PluginConfig):
    name = 'pretix_public_registrations'
    verbose_name = 'Pretix public registrations'

    class PretixPluginMeta:
        name = _('Pretix public registrations')
        author = 'Felix Schäfer, Dominik Weitz'
        description = _('This plugin will give the option to attendees of an event to mark their registration as public. Public registrations will be shown along their answers to questions marked as public by the organizers on a world-readable page.')
        visible = True
        version = __version__
        category = "FEATURE"
        compatibility = "pretix>=2.7.0"

    def ready(self):
        from . import signals  # NOQA


default_app_config = 'pretix_public_registrations.PluginApp'
