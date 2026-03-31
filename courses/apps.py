from django.apps import AppConfig


class CoursesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "courses"

    def ready(self) -> None:
        # Регистрация msgid для gettext (БД + каталог строк уроков Junior)
        import courses.i18n_db_strings  # noqa: F401
        import courses.i18n_junior_lessons  # noqa: F401
