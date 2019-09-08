from django.conf.urls import url

from .views import PublicParticipationsView

urlpatterns = [
    url(r'^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/public_participations/$', PublicParticipationsView.as_view(), name='settings')
]
