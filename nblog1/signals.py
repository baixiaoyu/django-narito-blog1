from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from .models import Comment, Reply


@receiver(post_save, sender=Comment)
def send_mail_to_author(sender, instance, created, **kwargs):
    """告诉管理员有评论"""
    if created:
        request = instance.request

        request.session[str(instance.pk)] = True

        context = {
            'post': instance.target,
        }
        subject = render_to_string('nblog1/mail/comment_notify_subject.txt', context, request)
        message = render_to_string('nblog1/mail/comment_notify_message.txt', context, request)
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [settings.DEFAULT_FROM_EMAIL]
        send_mail(subject, message, from_email, recipient_list)


@receiver(post_save, sender=Reply)
def send_mail_to_comment_user(sender, instance, created, **kwargs):
    """将留言的回信传达给管理者和评论者"""
    if created:

        request = instance.request

        comment = instance.target
        post = comment.target
        context = {
            'post': post,
        }
        subject = render_to_string('nblog1/mail/reply_notify_subject.txt', context, request)
        message = render_to_string('nblog1/mail/reply_notify_message.txt', context, request)

        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = []
        bcc = [settings.DEFAULT_FROM_EMAIL]
        # 留言的人正在输入邮箱地址。
        # 留言的人和回复的人不一样的时候，留言的人会回复哦
        if comment.email and not request.session.get(str(comment.pk)):
            recipient_list.append(comment.email)
        email = EmailMessage(subject, message, from_email, recipient_list, bcc)
        email.send()
