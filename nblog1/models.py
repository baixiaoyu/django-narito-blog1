import re

from ckeditor_uploader.fields import RichTextUploadingField
from django.conf import settings
from django.core.mail import EmailMessage
from django.db import models
from django.shortcuts import resolve_url
from django.template.loader import render_to_string
from django.utils import timezone


class Tag(models.Model):
    name = models.CharField('标签名', max_length=255, unique=True)

    def __str__(self):
        # 検索フォーム等では、紐づいた記事数を表示する。その場合はpost_countという属性に記事数を持つ。
        if hasattr(self, 'post_count'):
            return f'{self.name}({self.post_count})'
        else:
            return self.name


class Post(models.Model):
    """記事"""
    title = models.CharField('标题', max_length=32)
    text = RichTextUploadingField('文本')
    tags = models.ManyToManyField(Tag, verbose_name='标签', blank=True)

    relation_posts = models.ManyToManyField('self', verbose_name='关联文章', blank=True)
    is_public = models.BooleanField('是否公开', default=True)
    description = models.TextField('描述', max_length=130)
    keywords = models.CharField('关键字', max_length=255, default='关键字')
    created_at = models.DateTimeField('创建日期', default=timezone.now)
    updated_at = models.DateTimeField('更新日期', default=timezone.now)

    def __str__(self):
        return self.title

    def get_thumbnail(self):
        for match in re.finditer('https?://.*\.(?:jpg|jpeg|gif|png|PNG|GIF|JPEG|JPG)', self.text):
            return match.group()

    def line_push(self, request):
        """記事をラインで通知"""
        # if settings.USE_LINE_BOT:
        #     import linebot
        #     from linebot.models import TextSendMessage
        #     context = {
        #         'post': self,
        #     }
        #     message = render_to_string('nblog1/mail/send_latest_notify_message.txt', context, request)
        #     line_bot_api = linebot.LineBotApi(settings.LINE_BOT_API_KEY)
        #     for push in LinePush.objects.all():
        #         line_bot_api.push_message(push.user_id, messages=TextSendMessage(text=message))

    def email_push(self, request):
        """邮件通知"""
        context = {
            'post': self,
        }
        subject = render_to_string('nblog1/mail/send_latest_notify_subject.txt', context, request)
        message = render_to_string('nblog1/mail/send_latest_notify_message.txt', context, request)

        from_email = settings.DEFAULT_FROM_EMAIL
        bcc = [settings.DEFAULT_FROM_EMAIL]
        for mail_push in EmailPush.objects.filter(is_active=True):
            bcc.append(mail_push.mail)
        email = EmailMessage(subject, message, from_email, [], bcc)
        email.send()

    def browser_push(self):
        """浏览器通知"""
        if settings.USE_WEB_PUSH:
            import requests
            data = {
                'app_id': settings.ONE_SIGNAL_APP_ID,
                'included_segments': ['All'],
                'contents': {'en': self.title},
                'headings': {'en': 'test'},
                'url': resolve_url('nblog1:post_detail', pk=self.pk),
            }
            requests.post(
                "https://onesignal.com/api/v1/notifications",
                headers={'Authorization': settings.ONE_SIGNAL_REST_KEY},
                json=data,
            )


class Comment(models.Model):
    """评论"""
    name = models.CharField('你的名字', max_length=255, default='')
    text = models.TextField('评论内容')
    email = models.EmailField('邮件地址', blank=True, help_text='834829341@qq.com')
    target = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='目标文章')
    created_at = models.DateTimeField('创建日期', default=timezone.now)

    def __str__(self):
        return self.text[:20]


class Reply(models.Model):
    """回复"""
    name = models.CharField('名称', max_length=255, default='hi')
    text = models.TextField('回复内容')
    target = models.ForeignKey(Comment, on_delete=models.CASCADE, verbose_name='目标')
    created_at = models.DateTimeField('创建日期', default=timezone.now)

    def __str__(self):
        return self.text[:20]


class LinePush(models.Model):
    """line通知"""
    user_id = models.CharField('用户ID', max_length=100, unique=True)

    def __str__(self):
        return self.user_id


class EmailPush(models.Model):
    """邮件通知表"""
    mail = models.EmailField('邮件', unique=True)
    is_active = models.BooleanField('是否有效', default=False)

    def __str__(self):
        return self.mail
