from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0007_merge_20260312_1252"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="cover_image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="courses/covers/",
                verbose_name="Обложка курса",
            ),
        ),
        migrations.AddField(
            model_name="lesson",
            name="image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="courses/lessons/",
                verbose_name="Картинка урока",
            ),
        ),
    ]

