from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0014_alter_book_options_alter_category_options_and_more"),
    ]

    operations = [
        migrations.DeleteModel(name="CourseCertificate"),
    ]
