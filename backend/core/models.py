import json
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Пользователь системы с ролью"""
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Администратор'
        AGENT = 'agent', 'Сотрудник техподдержки'
        VIEWER = 'viewer', 'Наблюдатель'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.VIEWER,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class UserProfile(models.Model):
    """Профиль сотрудника"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    phone_number = models.CharField(max_length=50, blank=True)
    department = models.CharField(max_length=200, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    telegram_id = models.CharField(max_length=100, blank=True)
    slack_webhook = models.CharField(max_length=500, blank=True)

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class EmailMessage(models.Model):
    """Исходное письмо и результаты его разбора"""
    message_id = models.CharField(max_length=500, unique=True)
    subject = models.CharField(max_length=1000)
    body_plain = models.TextField()
    body_html = models.TextField(blank=True, null=True)
    sender_name = models.CharField(max_length=500)
    sender_email = models.EmailField()
    sender_phone = models.CharField(max_length=100, blank=True, null=True)
    object_name = models.CharField(max_length=500, blank=True, null=True)
    device_serial_numbers = models.TextField(
        help_text='Список заводских номеров (JSON или текст)',
    )
    received_at = models.DateTimeField()
    attachments = models.JSONField(
        default=list,
        blank=True,
        help_text='Список имён файлов вложений',
    )
    raw_headers = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Письмо'
        verbose_name_plural = 'Письма'
        ordering = ['-received_at']

    def get_serial_numbers_list(self):
        """Вернуть device_serial_numbers как список строк."""
        raw = self.device_serial_numbers or '[]'
        try:
            return json.loads(raw) if isinstance(raw, str) else raw
        except (TypeError, json.JSONDecodeError):
            return [s.strip() for s in str(raw).split(',') if s.strip()]


class ProcessedData(models.Model):
    """Результат обработки письма агентом + поля техподдержки"""
    class Sentiment(models.TextChoices):
        POSITIVE = 'positive', 'Позитив'
        NEUTRAL = 'neutral', 'Нейтрально'
        NEGATIVE = 'negative', 'Негатив'

    class Status(models.TextChoices):
        NEW = 'new', 'Новое'
        IN_PROGRESS = 'in_progress', 'В работе'
        WAITING_FOR_CLIENT = 'waiting_for_client', 'Ожидает ответа клиента'
        RESOLVED = 'resolved', 'Решено'
        CLOSED = 'closed', 'Закрыто'

    email = models.OneToOneField(
        EmailMessage,
        on_delete=models.CASCADE,
        related_name='processed_data',
    )
    full_name = models.CharField(max_length=500)
    object = models.CharField(max_length=500, blank=True)
    device_type = models.CharField(max_length=300, default='')
    phone = models.CharField(max_length=100, blank=True)
    email_address = models.CharField(max_length=254, blank=True)
    serial_numbers = models.JSONField(default=list)
    sentiment = models.CharField(
        max_length=20,
        choices=Sentiment.choices,
        default=Sentiment.NEUTRAL,
    )
    category = models.CharField(max_length=100, blank=True)
    question_summary = models.TextField(default='')
    generated_response = models.TextField(blank=True)
    response_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.NEW,
    )
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_processed',
    )
    assigned_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    client_feedback = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Обработанные данные'
        verbose_name_plural = 'Обработанные данные'
        ordering = ['-created_at']


class Comment(models.Model):
    """Комментарий к обращению"""
    processed_data = models.ForeignKey(
        ProcessedData,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='comments',
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_internal = models.BooleanField(
        default=False,
        help_text='Виден только сотрудникам',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']


class KnowledgeBase(models.Model):
    """База знаний"""
    class ContentType(models.TextChoices):
        MANUAL = 'manual', 'Руководство'
        FAQ = 'faq', 'FAQ'
        SOLUTION = 'solution', 'Решение'

    title = models.CharField(max_length=500)
    content = models.TextField()
    content_type = models.CharField(
        max_length=30,
        choices=ContentType.choices,
        default=ContentType.MANUAL,
    )
    keywords = models.TextField(blank=True, help_text='Ключевые слова для поиска')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'База знаний'
        verbose_name_plural = 'База знаний'
        ordering = ['-updated_at']


class KnowledgeEmbedding(models.Model):
    """Эмбеддинг фрагмента базы знаний"""
    knowledge_item = models.ForeignKey(
        KnowledgeBase,
        on_delete=models.CASCADE,
        related_name='embeddings',
    )
    embedding = models.JSONField(
        help_text='Вектор эмбеддинга (список float). Для pgvector можно заменить на VectorField.',
    )
    chunk_text = models.TextField()

    class Meta:
        verbose_name = 'Эмбеддинг базы знаний'
        verbose_name_plural = 'Эмбеддинги базы знаний'


class ProcessingLog(models.Model):
    """Лог работы агента"""
    email = models.ForeignKey(
        EmailMessage,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='processing_logs',
    )
    action = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Лог обработки'
        verbose_name_plural = 'Логи обработки'
        ordering = ['-created_at']
