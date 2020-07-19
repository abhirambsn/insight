# Generated by Django 3.0.8 on 2020-07-19 17:23

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('passport', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('profile_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=60)),
                ('last_name', models.CharField(max_length=60)),
                ('color_accent', models.CharField(choices=[('Blue', 'blue'), ('Green', 'green'), ('Pink', 'pink'), ('Red', 'red')], default='blue', max_length=10)),
                ('plan', models.CharField(choices=[('Monthly', 'monthly'), ('Annual', 'annual'), ('Trial', 'trial')], max_length=15)),
                ('isTrial', models.BooleanField()),
                ('validity', models.IntegerField()),
                ('linked_passport', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='passport.Passport')),
            ],
        ),
    ]
