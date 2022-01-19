from captcha.fields import CaptchaField
from django import forms
from django.db.models import Count
from django.core.files.storage import default_storage
from django.urls import reverse_lazy
from .fields import SimpleCaptchaField
from .models import Comment, Reply, Post, EmailPush, Tag
from .widgets import SuggestPostWidget, UploadableTextarea, CustomCheckboxSelectMultiple


class PostSearchForm(forms.Form):
    """文档搜索"""
    key_word = forms.CharField(
        label='关键字搜索',
        required=False,
    )

    tags = forms.ModelMultipleChoiceField(
        label='标签缩放',
        required=False,
        queryset=Tag.objects.annotate(post_count=Count('post')).order_by('name'),
        widget=CustomCheckboxSelectMultiple,
    )


class AdminPostCreateForm(forms.ModelForm):
    """文章创建和更新"""

    class Meta:
        model = Post
        fields = '__all__'
        widgets = {
            'text': UploadableTextarea(attrs={'placeholder': '[TOC]\n\n## 概要\n示例'}),
            'relation_posts': SuggestPostWidget(attrs={'data-url': reverse_lazy('nblog1:posts_suggest')}),
        }


class CommentCreateForm(forms.ModelForm):
    """注释创建表单"""
    #captcha = SimpleCaptchaField()
    captcha = CaptchaField(label='验证码', required=True, error_messages={'invalid': '验证码错误'})

    class Meta:
        model = Comment
        fields = ('name', 'text', 'email')

        # widgets = {
        #     'text': forms.Textarea(
        #         attrs={'placeholder': '支持下标。\n\n```python\nprint("xxx")\n```\n\n[](https://narito.ninja/)\n\n![画像alt](画像URL)'}
        #     )
        # }


class ReplyCreateForm(forms.ModelForm):
    """回信创建表单"""
    captcha = SimpleCaptchaField()

    class Meta:
        model = Reply
        fields = ('name', 'text')
        widgets = {
            'text': forms.Textarea(
                attrs={'placeholder': 'xxx。\n\n```python\nprint("コードはこのような感じで書く")\n```\n\n[リンクテキスト](https://narito.ninja/)\n\n![画像alt](画像URL)'}
            )
        }


class EmailForm(forms.ModelForm):
    """邮件表单"""

    class Meta:
        model = EmailPush
        fields = ('mail',)
        widgets = {
            'mail': forms.EmailInput(attrs={'placeholder': '电子邮件地址'})
        }
        error_messages = {
            'mail': {
                'unique': '邮件地址已经注册！',
            }
        }

    def clean_email(self):
        mail = self.cleaned_data['mail']
        EmailPush.objects.filter(mail=mail, is_active=False).delete()
        return mail


class FileUploadForm(forms.Form):
    """文件上传"""
    file = forms.FileField()

    def save(self):
        upload_file = self.cleaned_data['file']
        file_name = default_storage.save(upload_file.name, upload_file)
        file_url = default_storage.url(file_name)
        return file_url


