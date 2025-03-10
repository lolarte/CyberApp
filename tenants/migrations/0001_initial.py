# Generated by Django 5.1.6 on 2025-03-05 01:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('mailtemplates', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='uploads/')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(unique=True)),
                ('contact_name', models.CharField(max_length=255)),
                ('contact_email', models.CharField(max_length=255)),
                ('contact_phone', models.CharField(max_length=50)),
                ('contact_plan', models.CharField(max_length=150)),
                ('contact_payment_date', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='TenantAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('attachment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tenant_attachments', to='mailtemplates.attachment')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenants.client')),
            ],
        ),
        migrations.CreateModel(
            name='TenantGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, null=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenants.client')),
                ('group', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='tenant_data', to='auth.group')),
            ],
        ),
    ]
