# Generated by Django 5.2 on 2025-04-12 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mistakes', '0002_alter_mistake_mistake_type'),
        ('skills', '0005_skill_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='mistake',
            name='skills',
            field=models.ManyToManyField(blank=True, to='skills.skill'),
        ),
    ]
