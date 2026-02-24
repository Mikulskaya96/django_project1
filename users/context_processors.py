"""Добавляет is_teacher в контекст шаблонов — для отображения ссылки «Создать курс»."""

def user_role(request):
    is_teacher = False
    if request.user.is_authenticated:
        profile = getattr(request.user, "profile", None)
        is_teacher = profile and profile.role == "teacher"
    return {"is_teacher": is_teacher}
