from django.conf.urls import url

from .views import PublicRegistrationsSettingsView

urlpatterns = [
    url(
        r"^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/public_registrations/$",
        PublicRegistrationsSettingsView.as_view(),
        name="settings",
    )
]
