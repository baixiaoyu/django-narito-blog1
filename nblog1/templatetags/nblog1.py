from urllib import parse
from django import template
from django.conf import settings
from django.shortcuts import resolve_url
from django.utils.safestring import mark_safe
from nblog1.forms import EmailForm
import markdown
from markdown.extensions import Extension

register = template.Library()


@register.simple_tag
def url_replace(request, field, value):
    """替换一些GET参数。"""
    url_dict = request.GET.copy()
    url_dict[field] = str(value)
    return url_dict.urlencode()


@register.filter
def markdown_to_html(text):
    """将markdown转换为html。"""
    html = markdown.markdown(text, extensions=settings.MARKDOWN_EXTENSIONS)
    return mark_safe(html)


class EscapeHtml(Extension):

    def extendMarkdown(self, md):
        md.preprocessors.deregister('html_block')
        md.inlinePatterns.deregister('html')


@register.filter
def markdown_to_html_with_escape(text):
    """"
    """
    extensions = settings.MARKDOWN_EXTENSIONS + [EscapeHtml()]
    html = markdown.markdown(text, extensions=extensions)
    return mark_safe(html)


@register.inclusion_tag('nblog1/includes/subscribe_section.html')
def render_subscribe_section():
    context = {
        'subscribe_email_form': EmailForm,
        'USE_LINE_BOT': settings.USE_LINE_BOT,
        'USE_WEB_PUSH': settings.USE_WEB_PUSH,
    }
    if settings.USE_WEB_PUSH:
        context['ONE_SIGNAL_APP_ID'] = settings.ONE_SIGNAL_APP_ID
    return context


@register.simple_tag
def get_return_link(request):
    top_page = resolve_url('nblog1:top')
    referer = request.environ.get('HTTP_REFERER')
    # 没有直接URL输入或收藏夹访问的引荐来源网址，因此请返回首页
    if referer:
        # 如果有引荐来源网址，则返回到您网站上的上一页。
        parse_result = parse.urlparse(referer)
        if request.get_host() == parse_result.netloc:
            return referer
    return top_page
