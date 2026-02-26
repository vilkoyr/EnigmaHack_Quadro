# Generated manually for initial models

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('role', models.CharField(choices=[('admin', 'Администратор'), ('agent', 'Сотрудник техподдержки'), ('viewer', 'Наблюдатель')], default='viewer', max_length=20)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='EmailMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_id', models.CharField(max_length=500, unique=True)),
                ('subject', models.CharField(max_length=1000)),
                ('body_plain', models.TextField()),
                ('body_html', models.TextField(blank=True, null=True)),
                ('sender_name', models.CharField(max_length=500)),
                ('sender_email', models.EmailField(max_length=254)),
                ('sender_phone', models.CharField(blank=True, max_length=100, null=True)),
                ('object_name', models.CharField(blank=True, max_length=500, null=True)),
                ('device_serial_numbers', models.TextField(help_text='Список заводских номеров (JSON или текст)')),
                ('received_at', models.DateTimeField()),
                ('attachments', models.JSONField(blank=True, default=list, help_text='Список имён файлов вложений')),
                ('raw_headers', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Письмо',
                'verbose_name_plural': 'Письма',
                'ordering': ['-received_at'],
            },
        ),
        migrations.CreateModel(
            name='KnowledgeBase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500)),
                ('content', models.TextField()),
                ('content_type', models.CharField(choices=[('manual', 'Руководство'), ('faq', 'FAQ'), ('solution', 'Решение')], default='manual', max_length=30)),
                ('keywords', models.TextField(blank=True, help_text='Ключевые слова для поиска')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'База знаний',
                'verbose_name_plural': 'База знаний',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(blank=True, max_length=50)),
                ('department', models.CharField(blank=True, max_length=200)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('telegram_id', models.CharField(blank=True, max_length=100)),
                ('slack_webhook', models.CharField(blank=True, max_length=500)),
                ('user', models.OneToOneField(on_delete=models.CASCADE, related_name='profile', to='core.user')),
            ],
            options={
                'verbose_name': 'Профиль',
                'verbose_name_plural': 'Профили',
            },
        ),
        migrations.CreateModel(
            name='ProcessedData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=500)),
                ('object', models.CharField(blank=True, max_length=500)),
                ('phone', models.CharField(blank=True, max_length=100)),
                ('email_address', models.CharField(blank=True, max_length=254)),
                ('serial_numbers', models.JSONField(default=list)),
                ('sentiment', models.CharField(blank=True, max_length=50)),
                ('category', models.CharField(blank=True, max_length=100)),
                ('generated_response', models.TextField(blank=True)),
                ('response_sent_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('new', 'Новое'), ('in_progress', 'В работе'), ('waiting_for_client', 'Ожидает ответа клиента'), ('resolved', 'Решено'), ('closed', 'Закрыто')], default='new', max_length=30)),
                ('assigned_at', models.DateTimeField(blank=True, null=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('client_feedback', models.TextField(blank=True)),
                ('internal_notes', models.TextField(blank=True)),
                ('assignee', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='assigned_processed', to='core.user')),
                ('email', models.OneToOneField(on_delete=models.CASCADE, related_name='processed_data', to='core.emailmessage')),
            ],
            options={
                'verbose_name': 'Обработанные данные',
                'verbose_name_plural': 'Обработанные данные',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProcessingLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=100)),
                ('status', models.CharField(max_length=20)),
                ('details', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('email', models.ForeignKey(blank=True, null=True, on_delete=models.CASCADE, related_name='processing_logs', to='core.emailmessage')),
            ],
            options={
                'verbose_name': 'Лог обработки',
                'verbose_name_plural': 'Логи обработки',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='KnowledgeEmbedding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('embedding', models.JSONField(help_text='Вектор эмбеддинга (список float). Для pgvector можно заменить на VectorField.')),
                ('chunk_text', models.TextField()),
                ('knowledge_item', models.ForeignKey(on_delete=models.CASCADE, related_name='embeddings', to='core.knowledgebase')),
            ],
            options={
                'verbose_name': 'Эмбеддинг базы знаний',
                'verbose_name_plural': 'Эмбеддинги базы знаний',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_internal', models.BooleanField(default=False, help_text='Виден только сотрудникам')),
                ('author', models.ForeignKey(null=True, on_delete=models.SET_NULL, related_name='comments', to='core.user')),
                ('processed_data', models.ForeignKey(on_delete=models.CASCADE, related_name='comments', to='core.processeddata')),
            ],
            options={
                'verbose_name': 'Комментарий',
                'verbose_name_plural': 'Комментарии',
                'ordering': ['created_at'],
            },
        ),
    ]
