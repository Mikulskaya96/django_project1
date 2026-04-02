"""Добавляет is_teacher, avatar_url и can_upload_avatar в контекст шаблонов."""

from django.conf import settings


def user_role(request):
    is_teacher = False
    profile_avatar_url = None
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            is_teacher = profile.role == "teacher"
            profile_avatar_url = profile.avatar_url or None
        except Exception:
            pass
    # Локально: DEBUG=True → файлы в media/. На проде: только если задан CLOUDINARY_URL (облако), иначе диск эфемерный.
    can_upload_avatar = bool(settings.DEBUG) or bool(getattr(settings, "CLOUDINARY_URL", ""))
    return {"is_teacher": is_teacher, "profile_avatar_url": profile_avatar_url, "can_upload_avatar": can_upload_avatar}
