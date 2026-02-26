# Generated manually: extra web-table required fields

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="processeddata",
            name="device_type",
            field=models.CharField(default="", max_length=300),
        ),
        migrations.AddField(
            model_name="processeddata",
            name="question_summary",
            field=models.TextField(default=""),
        ),
        migrations.AlterField(
            model_name="processeddata",
            name="sentiment",
            field=models.CharField(
                choices=[
                    ("positive", "Позитив"),
                    ("neutral", "Нейтрально"),
                    ("negative", "Негатив"),
                ],
                default="neutral",
                max_length=20,
            ),
        ),
    ]

