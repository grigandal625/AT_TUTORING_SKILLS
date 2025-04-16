# Generated by Django 5.1.7 on 2025-04-13 14:16
import django.db.models.deletion
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Skill",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("group", models.IntegerField(choices=[(1, "KB"), (2, "SIMULATION")])),
                ("code", models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                ("user_id", models.CharField(max_length=255, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("task_name", models.CharField(max_length=255)),
                (
                    "task_object",
                    models.IntegerField(
                        choices=[
                            (1, "Тип"),
                            (2, "Объект"),
                            (3, "Событие"),
                            (4, "Интервал"),
                            (5, "Правило"),
                            (6, "Тип ресурса"),
                            (7, "Ресурс"),
                            (8, "Образец операции"),
                            (9, "Операции"),
                            (10, "Функция"),
                        ]
                    ),
                ),
                ("object_name", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("object_reference", models.JSONField(blank=True, null=True)),
                ("skills", models.ManyToManyField(default=None, related_name="tasks_skills", to="skills.skill")),
            ],
        ),
        migrations.CreateModel(
            name="TaskUser",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("attempts", models.IntegerField(default=0)),
                ("is_completed", models.BooleanField(default=False)),
                ("task", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="skills.task")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="skills.user")),
            ],
        ),
        migrations.CreateModel(
            name="UserSkill",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("mark", models.FloatField(default=100)),
                ("is_completed", models.BooleanField(default=False)),
                ("skill", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="skills.skill")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="skills.user")),
            ],
        ),
        migrations.CreateModel(
            name="Variant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(default=None, max_length=255)),
                ("task", models.ManyToManyField(to="skills.task")),
            ],
        ),
        migrations.AddField(
            model_name="user",
            name="variant",
            field=models.ForeignKey(
                blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to="skills.variant"
            ),
        ),
    ]
