from django.urls import reverse
from pretix.control.views.event import EventSettingsViewMixin, EventSettingsFormView
from pretix.base.models import Event

from .forms import PublicRegistrationsForm


class PublicParticipationsView(EventSettingsViewMixin, EventSettingsFormView):
    form_class = PublicRegistrationsForm
    template_name = 'pretix_public_registrations/settings.html'

    def get_success_url(self, **kwargs):
        return reverse('plugins:pretix_public_registrations:settings', kwargs={
            'organizer': self.request.event.organizer.slug,
            'event': self.request.event.slug,
        })
