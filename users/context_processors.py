"""Добавляет is_teacher, avatar_url и can_upload_avatar в контекст шаблонов."""

from django.conf import settings


def user_role(request):
    is_teacher = False
    profile_avatar_url = None
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            is_teacher = profile.role == "teacher"
            if profile.avatar:
                profile_avatar_url = profile.avatar.url
        except Exception:
            pass
    # Загрузка аватара только при DEBUG (локально); на Render (DEBUG=False) — скрыта
    can_upload_avatar = settings.DEBUG
    return {"is_teacher": is_teacher, "profile_avatar_url": profile_avatar_url, "can_upload_avatar": can_upload_avatar}
