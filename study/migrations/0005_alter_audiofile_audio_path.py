# Generated by Django 5.0 on 2024-01-10 06:45

import study.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("study", "0004_alter_result_comprehendeval_alter_result_fluencyeval_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="audiofile",
            name="audio_path",
            field=models.FileField(
                upload_to="audios/", validators=[study.validators.AudioFileValidator]
            ),
        ),
    ]