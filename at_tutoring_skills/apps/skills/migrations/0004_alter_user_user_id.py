# Generated by Django 5.1.7 on 2025-03-30 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skills', '0003_taskuser_is_completed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_id',
            field=models.CharField(max_length=255, primary_key=True, serialize=False),
        ),
    ]
