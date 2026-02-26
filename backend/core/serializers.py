from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
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


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('phone_number', 'department', 'avatar', 'telegram_id', 'slack_webhook')


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'is_active', 'profile',
        )
        read_only_fields = ('id', 'username', 'role', 'is_active')

    def get_profile(self, obj):
        try:
            return UserProfileSerializer(obj.profile).data
        except UserProfile.DoesNotExist:
            return None


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    phone_number = serializers.CharField(required=False, allow_blank=True)
    department = serializers.CharField(required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=User.Role.choices, default=User.Role.VIEWER)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'password', 'first_name', 'last_name',
            'phone_number', 'department', 'role',
        )

    def create(self, validated_data):
        profile_data = {
            k: validated_data.pop(k)
            for k in ('phone_number', 'department')
            if k in validated_data
        }
        role = validated_data.pop('role', User.Role.VIEWER)
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, role=role, **validated_data)
        UserProfile.objects.update_or_create(user=user, defaults=profile_data)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])


class EmailMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailMessage
        fields = '__all__'
        read_only_fields = ('message_id', 'received_at')


class ProcessedDataListSerializer(serializers.ModelSerializer):
    assignee_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ProcessedData
        fields = (
            'id', 'email', 'full_name', 'object', 'phone', 'email_address',
            'device_type', 'serial_numbers', 'sentiment', 'category', 'question_summary', 'status', 'status_display',
            'assignee', 'assignee_name', 'assigned_at', 'resolved_at',
            'created_at', 'response_sent_at',
        )

    def get_assignee_name(self, obj):
        return obj.assignee.get_full_name() or obj.assignee.username if obj.assignee else None


class ProcessedDataDetailSerializer(ProcessedDataListSerializer):
    email_data = EmailMessageSerializer(source='email', read_only=True)

    class Meta(ProcessedDataListSerializer.Meta):
        fields = ProcessedDataListSerializer.Meta.fields + (
            'generated_response', 'client_feedback', 'internal_notes', 'email_data',
        )


class ProcessedDataUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessedData
        fields = (
            'full_name', 'object', 'phone', 'email_address', 'serial_numbers',
            'device_type', 'sentiment', 'category', 'question_summary', 'internal_notes', 'client_feedback',
        )


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'processed_data', 'author', 'author_name', 'text', 'created_at', 'is_internal')
        read_only_fields = ('id', 'author', 'created_at')

    def get_author_name(self, obj):
        return obj.author.get_full_name() or obj.author.username if obj.author else None


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('text', 'is_internal')


class KnowledgeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeBase
        fields = ('id', 'title', 'content', 'content_type', 'keywords', 'created_at', 'updated_at')


class KnowledgeEmbeddingSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeEmbedding
        fields = ('id', 'knowledge_item', 'embedding', 'chunk_text')


class ProcessingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessingLog
        fields = ('id', 'email', 'action', 'status', 'details', 'created_at')
