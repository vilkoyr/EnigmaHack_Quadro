from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User,
    UserProfile,
    EmailMessage,
    ProcessedData,
    Comment,
    KnowledgeBase,
    KnowledgeEmbedding,
    ProcessingLog,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (('Роль', {'fields': ('role',)}),)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'phone_number')
    raw_id_fields = ('user',)


@admin.register(EmailMessage)
class EmailMessageAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'subject', 'sender_email', 'received_at')
    search_fields = ('message_id', 'subject', 'sender_email', 'sender_name')
    list_filter = ('received_at',)
    readonly_fields = ('raw_headers',)


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    raw_id_fields = ('author',)


@admin.register(ProcessedData)
class ProcessedDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'object', 'device_type', 'sentiment', 'status', 'assignee', 'category', 'created_at')
    list_filter = ('status', 'sentiment', 'category')
    search_fields = ('full_name', 'email_address', 'phone', 'object')
    raw_id_fields = ('email', 'assignee')
    inlines = [CommentInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'processed_data', 'author', 'is_internal', 'created_at')
    list_filter = ('is_internal',)
    raw_id_fields = ('processed_data', 'author')


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type', 'updated_at')
    list_filter = ('content_type',)
    search_fields = ('title', 'keywords', 'content')


@admin.register(KnowledgeEmbedding)
class KnowledgeEmbeddingAdmin(admin.ModelAdmin):
    list_display = ('id', 'knowledge_item', 'chunk_text_preview')
    raw_id_fields = ('knowledge_item',)

    def chunk_text_preview(self, obj):
        return (obj.chunk_text or '')[:80] + '...' if len(obj.chunk_text or '') > 80 else (obj.chunk_text or '')
    chunk_text_preview.short_description = 'Фрагмент'


@admin.register(ProcessingLog)
class ProcessingLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'action', 'status', 'created_at')
    list_filter = ('action', 'status')
    raw_id_fields = ('email',)
