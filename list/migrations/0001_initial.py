# Generated by Django 3.0.8 on 2020-07-28 02:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_text', models.CharField(max_length=200)),
                ('date', models.DateTimeField(verbose_name='date created')),
                ('completed', models.BooleanField()),
            ],
        ),
    ]