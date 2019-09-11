from django import forms
from django.dispatch import receiver
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _, get_language
from django.urls import resolve, reverse
from django_gravatar.helpers import get_gravatar_url
from i18nfield.strings import LazyI18nString
from pretix.presale.signals import question_form_fields, front_page_bottom, process_response, html_head
from pretix.control.signals import nav_event_settings
from pretix.base.models import OrderPosition, QuestionAnswer
from pretix.base.settings import settings_hierarkey


settings_hierarkey.add_default('public_registrations_items', None, list)
settings_hierarkey.add_default('public_registrations_questions', None, list)
settings_hierarkey.add_default('public_registrations_show_attendee_name', False, bool)
settings_hierarkey.add_default('public_registrations_show_item_name', False, bool)


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
def add_public_registration_question(sender, position, **kwargs):
    # TODO: This should also filter by items with an attendee
    if str(position.item.pk) in sender.settings.get('public_registrations_items'):
        return {'public_registrations_public_registration': forms.BooleanField(
            label=_('Public registration'),
            required=False,
            help_text=sender.settings.get('public_registrations_field_help_text', as_type=LazyI18nString),
        )}
    else:
        return {}


@receiver(signal=front_page_bottom, dispatch_uid="public_registrations_table")
def add_public_registrations_table(sender, **kwargs):
    cached = sender.cache.get('public_registrations_table_' + get_language())
    if cached is None:
        cached = ""
        public_questions = sender.questions.filter(pk__in=sender.settings.get('public_registrations_questions'))
        headers = (
            [_("Product")] if sender.settings.get('public_registrations_show_item_name') else []
        ) + (
            [_("Name")] if sender.settings.get('public_registrations_show_attendee_name') else []
        ) + [
            q.question for q in public_questions
        ]
        order_positions = OrderPosition.objects.filter(order__event=sender, item__pk__in=sender.settings.get('public_registrations_items'))
        public_order_positions = [
            op for op in order_positions
            if op.meta_info_data.get('question_form_data', {}).get('public_registrations_public_registration')
        ]
        answers = QuestionAnswer.objects.filter(orderposition__in=public_order_positions, question__in=public_questions)
        public_answers = {
            a.orderposition_id: {
                a.question_id: a
            }
            for a in answers
        }
        public_registrations = [
            {
                'gr_url': get_gravatar_url(pop.attendee_email, size=24, default="wavatar"),
                'fields': (
                    [pop.item.name] if sender.settings.get('public_registrations_show_item_name') else []
                ) + (
                    [pop.attendee_name_cached] if sender.settings.get('public_registrations_show_attendee_name') else []
                ) + [
                    public_answers[pop.pk][pq.pk].answer if public_answers.get(pop.pk, None) and public_answers[pop.pk].get(pq.pk, None) else ''
                    for pq in public_questions
                ]
            } for pop in public_order_positions if pop.attendee_email and pop.attendee_name_cached
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
