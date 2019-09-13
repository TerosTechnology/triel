# Generated by Django 2.2.4 on 2019-09-13 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(editable=False, max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Simulator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(editable=False, max_length=255, unique=True)),
                ('path', models.CharField(max_length=255, null=True)),
                ('languages', models.ManyToManyField(editable=False, related_name='simulators', to='manager.Language')),
            ],
        ),
        migrations.CreateModel(
            name='Suite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(editable=False, max_length=255, unique=True)),
                ('simulators', models.ManyToManyField(editable=False, related_name='suites', to='manager.Simulator')),
            ],
        ),
    ]
