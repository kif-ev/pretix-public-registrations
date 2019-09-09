from django import forms
from django.dispatch import receiver
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _, get_language
from django.urls import resolve, reverse
from django_gravatar.helpers import get_gravatar_url
from i18nfield.strings import LazyI18nString
from pretix.presale.signals import question_form_fields, front_page_bottom, process_response, html_head
from pretix.control.signals import nav_event_settings
from pretix.base.models import OrderPosition
from pretix.base.settings import settings_hierarkey


settings_hierarkey.add_default('public_registrations_items', None, list)
settings_hierarkey.add_default('public_registrations_questions', None, list)


@receiver(html_head, dispatch_uid="public_registrations_html_head")
def add_public_registrations_html_head(sender, request=None, **kwargs):
    cached = sender.cache.get('public_registrations_html_head')
    if cached is None:
        url = resolve(request.path_info)
        if "event.index" in url.url_name:
            template = get_template("pretix_public_registrations/head.html")
            cached = template.render()
        else:
            cached = ""
        sender.cache.set('public_registrations_html_head', cached)
    return cached


@receiver(question_form_fields, dispatch_uid="public_registration_question")
def add_public_registration_question(sender, **kwargs):
    return {'public_registration': forms.CharField(
        label=_('Public registration'),
        required=False,
        help_text=sender.settings.get('public_registration_field_help_text', as_type=LazyI18nString),
        widget=forms.CheckboxInput(),
    )}


@receiver(signal=front_page_bottom, dispatch_uid="public_registrations_table")
def add_public_registrations_table(sender, **kwargs):
    cached = sender.cache.get('public_registrations_table_' + get_language())
    if cached is None:
        cached = ""
        headers = ["Name"]
        order_positions = OrderPosition.objects.filter(order__event=sender)
        public_order_positions = [
            op for op in order_positions
            if op.meta_info_data.get('question_form_data', {}).get('public_registration') == "True"
        ]
        public_registrations = [
            {
                'gr_url': get_gravatar_url(pop.attendee_email, size=24, default="wavatar"),
                'fields': [pop.attendee_name_cached]
            } for pop in public_order_positions
        ]
        template = get_template('pretix_public_registrations/front_page.html')
        cached = template.render({
            'headers': headers,
            'public_registrations': public_registrations
        })
        sender.cache.set('public_registrations_table_' + get_language(), cached)
    return cached


@receiver(signal=process_response, dispatch_uid="public_registragions_csp_headers")
def add_public_registrations_csp_headers(sender, request=None, response=None, **kwargs):
    if "event.index" in resolve(request.path_info).url_name:
        response['Content-Security-Policy'] = "img-src https://secure.gravatar.com"
    return response


@receiver(signal=nav_event_settings, dispatch_uid="public_registrations_nav_settings")
def navbar_settings(sender, request=None, **kwargs):
    url = resolve(request.path_info)
    return [{
        'label': _('Public registrations'),
        'url': reverse('plugins:pretix_public_registrations:settings', kwargs={
            'event': request.event.slug,
            'organizer': request.organizer.slug,
        }),
        'active': url.namespace == 'plugins:pretix_public_registrations' and url.url_name == 'settings',
    }]
