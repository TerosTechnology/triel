# Generated by Django 2.2.4 on 2019-09-01 15:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Simulator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('path', models.FileField(upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='Suite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='SuiteSimulator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=255)),
                ('simulator', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='manager.Simulator')),
                ('suite', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='manager.Suite')),
            ],
            options={
                'unique_together': {('suite', 'simulator')},
            },
        ),
        migrations.CreateModel(
            name='SimulatorLanguage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=255)),
                ('language', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='manager.Language')),
                ('simulator', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='manager.Simulator')),
            ],
            options={
                'unique_together': {('simulator', 'language')},
            },
        ),
    ]
