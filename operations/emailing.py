from django.conf import settings
from django.template import Context, Engine

from .models import EmailTask, EmailTemplate


def _render(value, context):
    return Engine.get_default().from_string(value).render(Context(context))


def create_email_task(template_key, recipients, context, *, kind, inquiry=None, contact=None, created_by=None):
    recipients = [address for address in recipients if address]
    if not recipients:
        return None
    template = EmailTemplate.objects.filter(key=template_key, is_active=True).first()
    if not template:
        return None
    return EmailTask.objects.create(
        template=template,
        kind=kind,
        inquiry=inquiry,
        contact=contact,
        recipients=recipients,
        subject=_render(template.subject, context),
        html_body=_render(template.html_body, context),
        text_body=_render(template.text_body, context),
        created_by=created_by,
    )


def queue_lead_messages(lead, kind):
    is_inquiry = kind == "inquiry"
    summary = lead.detailed_requirements if is_inquiry else lead.message
    context = {
        "lead_type": "询盘" if is_inquiry else "联系留言",
        "contact_name": lead.contact_name,
        "email": lead.email,
        "phone": lead.phone,
        "summary": summary[:500],
    }
    relation = {"inquiry": lead} if is_inquiry else {"contact": lead}
    create_email_task(
        "sales-notice",
        settings.SALES_EMAILS,
        context,
        kind=EmailTask.Kind.SALES_NOTICE,
        **relation,
    )
    create_email_task(
        "inquiry-receipt" if is_inquiry else "contact-receipt",
        [lead.email],
        context,
        kind=EmailTask.Kind.CUSTOMER_RECEIPT,
        **relation,
    )
