"""Шаблонный тег для рендеринга Markdown в HTML."""

import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def markdown_to_html(text):
    """Превращает Markdown в HTML (с подсветкой кода)."""
    if not text:
        return ""
    md = markdown.Markdown(extensions=["extra", "fenced_code"])
    return mark_safe(md.convert(text))
