"""Шаблонный тег для рендеринга Markdown в HTML."""

import markdown
from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext

register = template.Library()


@register.filter
def translate_author(username):
    """Переводит 'teacher' как 'Преподаватель', остальные возвращает как есть."""
    if username == "teacher":
        return gettext("Преподаватель")
    return username


@register.filter
def translate_db_text(text):
    """Переводит текст из БД (названия курсов, уроков и т.д.)."""
    if not text:
        return ""
    return gettext(text)


@register.filter
def translate_category(name):
    """Переводит название категории."""
    if not name:
        return ""
    return gettext(name)


def _lesson_for_cover_fallback(course):
    """Урок, с которого берётся картинка как обложка курса при пустой «Обложке курса».

    Junior: второй по порядку (первый урок часто слишком тяжёлый для сохранения в админке на Render).
    Pro: третий по порядку — отдельно от финального урока с «Слово автора» (там своя картинка).
    """
    if not course:
        return None
    try:
        lessons = list(course.lessons.order_by("order", "id"))
    except Exception:
        return None
    if not lessons:
        return None
    if getattr(course, "level", None) == "junior":
        return lessons[1] if len(lessons) > 1 else lessons[0]
    # pro
    if len(lessons) >= 3:
        return lessons[2]
    if len(lessons) == 2:
        return lessons[1]
    return lessons[0]


@register.filter
def course_cover_image(course):
    """Обложка курса или картинка урока-запаса (см. _lesson_for_cover_fallback)."""
    if not course:
        return None
    if course.cover_image and getattr(course.cover_image, "name", ""):
        return course.cover_image
    lesson = _lesson_for_cover_fallback(course)
    if lesson and lesson.image and getattr(lesson.image, "name", ""):
        return lesson.image
    return None


@register.filter
def is_course_cover_source_lesson(lesson):
    """True, если картинка этого урока показывается как обложка курса (нет своей обложки у курса)."""
    if not lesson or not getattr(lesson, "course_id", None):
        return False
    course = lesson.course
    if course.cover_image and getattr(course.cover_image, "name", ""):
        return False
    source = _lesson_for_cover_fallback(course)
    return bool(source and source.pk == lesson.pk)


@register.filter
def translate_content(text):
    """Переводит контент урока построчно."""
    if not text:
        return ""
    lines = text.split("\n")
    out = []
    for line in lines:
        # Убираем \r (CRLF в БД/Windows), иначе gettext не находит msgid в каталоге
        key = line.rstrip("\r")
        if key.strip():
            out.append(gettext(key))
        else:
            out.append(line)
    return "\n".join(out)


@register.filter
def markdown_to_html(text):
    """Превращает Markdown в HTML (с подсветкой кода)."""
    if not text:
        return ""
    md = markdown.Markdown(extensions=["extra", "fenced_code"])
    return mark_safe(md.convert(text))


@register.filter
def inject_author_photo(html, lesson):
    """Подставляет фото вместо маркера <!-- AUTHOR_PHOTO --> (финальный урок Pro).

    Приоритет: «Фото автора» у курса; если не задано — «Картинка урока» (удобно при лимите
    размера POST в админке: фото грузят в уроке отдельно от тяжёлого текста курса).
    """
    if not html or not lesson:
        return html
    course = getattr(lesson, "course", None)
    if not course:
        return html
    from django.utils.html import escape
    from django.utils.translation import gettext as _

    marker = "<!-- AUTHOR_PHOTO -->"
    img_html = ""
    url = ""
    course_img = getattr(course, "author_image", None)
    if course_img and getattr(course_img, "name", ""):
        try:
            url = course_img.url
        except ValueError:
            url = ""
    if not url:
        lesson_img = getattr(lesson, "image", None)
        if lesson_img and getattr(lesson_img, "name", ""):
            try:
                url = lesson_img.url
            except ValueError:
                url = ""
    if not url:
        # Не вырезаем маркер без фото — иначе ломается wrap_author_word_section и пропадает блок.
        return html

    alt = _("Фото автора курса")
    img_html = (
        '<figure class="lesson-author-photo">'
        f'<img src="{escape(url)}" alt="{escape(alt)}" loading="lazy" />'
        "</figure>"
    )
    text = str(html)
    for fragment in (
        marker,
        "<p><!-- AUTHOR_PHOTO --></p>",
        "<p>\n<!-- AUTHOR_PHOTO -->\n</p>",
    ):
        text = text.replace(fragment, img_html)
    return mark_safe(text)


@register.filter
def wrap_author_word_section(html):
    """
    Оформляет блок «Слово автора»: заголовок h2 + фото + текст в карточке с сеткой.
    Текст урока не меняется — только обёртка HTML.
    """
    if not html:
        return html
    text = str(html)
    fig_open = '<figure class="lesson-author-photo">'
    pos = text.find(fig_open)
    if pos == -1:
        return html
    before_fig = text[:pos]
    h2_open = before_fig.rfind("<h2")
    if h2_open == -1:
        return html
    fig_close = text.find("</figure>", pos)
    if fig_close == -1:
        return html
    fig_end = fig_close + len("</figure>")
    head = text[:h2_open]
    h2_block = text[h2_open:pos]
    figure_block = text[pos:fig_end]
    rest = text[fig_end:]
    next_h2 = rest.find("<h2")
    if next_h2 != -1:
        message_block = rest[:next_h2]
        tail = rest[next_h2:]
    else:
        message_block = rest
        tail = ""
    wrapped = (
        f'{head}<div class="lesson-author-word">{h2_block}'
        f'<div class="lesson-author-word__card">'
        f'<div class="lesson-author-word__grid">'
        f'<div class="lesson-author-word__photo">{figure_block}</div>'
        f'<div class="lesson-author-word__message">{message_block}</div>'
        f"</div></div></div>{tail}"
    )
    return mark_safe(wrapped)


@register.filter
def wrap_solution_spoiler(html, course_level):
    """Прячет секцию «Решение» в кнопку-спойлер (Junior и Pro — разбор домашки)."""
    if not html or course_level not in ("junior", "pro"):
        return html
    start_marker = "<!-- SPOILER_START -->"
    end_marker = "<!-- SPOILER_END -->"
    if start_marker not in html or end_marker not in html:
        return html
    try:
        start = html.index(start_marker)
        end = html.index(end_marker) + len(end_marker)
        before = html[:start]
        spoiler_content = html[start:end].replace(start_marker, "").replace(end_marker, "").strip()
        after = html[end:]
        summary = gettext("Показать решение")
        wrapped = f'<details class="lesson-spoiler"><summary>{summary}</summary><div class="lesson-spoiler__content">{spoiler_content}</div></details>'
        return mark_safe(before + wrapped + after)
    except (ValueError, TypeError):
        return html
