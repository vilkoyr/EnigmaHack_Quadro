import csv
from io import StringIO
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from .models import User, UserProfile, ProcessedData, Comment, KnowledgeBase, EmailMessage
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    ProcessedDataListSerializer,
    ProcessedDataDetailSerializer,
    ProcessedDataUpdateSerializer,
    CommentSerializer,
    CommentCreateSerializer,
    KnowledgeBaseSerializer,
)
from .permissions import IsAdmin, IsAdminOrAgent



class RegisterView(APIView):
    """Регистрация сотрудника"""
    serializer_class = UserCreateSerializer

    def get_permissions(self):
        if getattr(settings, 'REGISTRATION_OPEN_TO_ALL', False):
            return [AllowAny()]
        return [IsAuthenticated(), IsAdmin()]

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if getattr(settings, 'REGISTRATION_OPEN_TO_ALL', False):
            serializer.validated_data['role'] = User.Role.VIEWER
        elif not request.user.is_authenticated or request.user.role != 'admin':
            serializer.validated_data['role'] = User.Role.VIEWER
        user = serializer.save()
        return Response(
            {'id': user.id, 'username': user.username, 'email': user.email},
            status=status.HTTP_201_CREATED,
        )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_serializer = UserSerializer(request.user)
        return Response(user_serializer.data)

    def put(self, request):
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user, data=request.data, partial=True)
        user_serializer.fields.pop('profile', None)
        user_serializer.fields.pop('role_display', None)
        for f in ('id', 'username', 'role', 'is_active'):
            user_serializer.fields.get(f).read_only = True
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        profile_data = {k: request.data.get(k) for k in ('phone_number', 'department', 'avatar', 'telegram_id', 'slack_webhook') if k in request.data}
        if profile_data:
            for k, v in profile_data.items():
                setattr(profile, k, v)
            profile.save()
        return Response(UserSerializer(user).data)


class LogoutView(APIView):
    """Клиент удаляет токен"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({'detail': 'Вы вышли из системы'})


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not request.user.check_password(serializer.validated_data['old_password']):
            return Response({'old_password': 'Неверный пароль'}, status=status.HTTP_400_BAD_REQUEST)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'detail': 'Пароль изменён'})




class ProcessedDataViewSet(viewsets.ModelViewSet):
    queryset = ProcessedData.objects.select_related('email', 'assignee').prefetch_related('comments')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('status', 'category', 'sentiment', 'assignee')

    def get_serializer_class(self):
        if self.action == 'list':
            return ProcessedDataListSerializer
        return ProcessedDataDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)
        return qs

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not (request.user.role == 'admin' or (request.user.role == 'agent' and instance.assignee_id == request.user.id)):
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = ProcessedDataUpdateSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ProcessedDataDetailSerializer(instance).data)

    def destroy(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['patch'], url_path='assign')
    def assign(self, request, pk=None):
        obj = self.get_object()
        if request.user.role not in ('admin', 'agent'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        user_id = request.data.get('user_id')
        if request.user.role == 'admin' and user_id is not None:
            try:
                new_assignee = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return Response({'user_id': 'Пользователь не найден'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            new_assignee = request.user
        obj.assignee = new_assignee
        obj.assigned_at = timezone.now()
        obj.status = ProcessedData.Status.IN_PROGRESS
        obj.save()
        return Response(ProcessedDataDetailSerializer(obj).data)

    @action(detail=True, methods=['patch'], url_path='status')
    def set_status(self, request, pk=None):
        obj = self.get_object()
        if request.user.role not in ('admin', 'agent'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        new_status = request.data.get('status')
        if new_status not in dict(ProcessedData.Status.choices):
            return Response({'status': 'Недопустимое значение'}, status=status.HTTP_400_BAD_REQUEST)
        obj.status = new_status
        if new_status == ProcessedData.Status.RESOLVED or new_status == ProcessedData.Status.CLOSED:
            obj.resolved_at = timezone.now()
        obj.save()
        return Response(ProcessedDataDetailSerializer(obj).data)


class ProcessedDataCommentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, processed_id):
        if not ProcessedData.objects.filter(pk=processed_id).exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        comments = Comment.objects.filter(processed_data_id=processed_id).select_related('author')
        if request.user.role == 'viewer':
            comments = comments.filter(is_internal=False)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, processed_id):
        if request.user.role not in ('admin', 'agent'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        try:
            processed = ProcessedData.objects.get(pk=processed_id)
        except ProcessedData.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(processed_data=processed, author=request.user)
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)


class ProcessedDataCommentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, processed_id, comment_id):
        try:
            comment = Comment.objects.get(pk=comment_id, processed_data_id=processed_id)
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.role != 'admin' and comment.author_id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExportView(APIView):
    permission_classes = [IsAuthenticated]
    """Экспорт отфильтрованных обращений в CSV/XLSX."""

    def post(self, request):
        if request.user.role == 'viewer':
            return Response(status=status.HTTP_403_FORBIDDEN)
        qs = ProcessedData.objects.select_related('email', 'assignee')
        for key in ('status', 'category', 'sentiment', 'assignee', 'date_from', 'date_to'):
            val = request.data.get(key) or request.query_params.get(key)
            if not val:
                continue
            if key == 'date_from':
                qs = qs.filter(created_at__date__gte=val)
            elif key == 'date_to':
                qs = qs.filter(created_at__date__lte=val)
            else:
                qs = qs.filter(**{key: val})
        format_type = (request.data.get('format') or request.query_params.get('format') or 'csv').lower()
        if format_type == 'xlsx':
            return self._export_xlsx(qs)
        return self._export_csv(qs)

    def _export_csv(self, qs):
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow([
            'id', 'full_name', 'object', 'device_type', 'phone', 'email_address', 'serial_numbers',
            'sentiment', 'category', 'question_summary', 'status', 'assignee', 'created_at', 'internal_notes',
        ])
        for row in qs:
            writer.writerow([
                row.id, row.full_name, row.object, row.device_type, row.phone, row.email_address,
                row.serial_numbers, row.sentiment, row.category, row.question_summary, row.status,
                row.assignee.get_full_name() or row.assignee.username if row.assignee else '',
                row.created_at.isoformat() if row.created_at else '', row.internal_notes,
            ])
        response = HttpResponse(buffer.getvalue(), content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="processed_export.csv"'
        return response

    def _export_xlsx(self, qs):
        try:
            import openpyxl
            from openpyxl.writer.excel import save_virtual_workbook
        except ImportError:
            return Response(
                {'detail': 'Формат XLSX недоступен. Установите openpyxl.'},
                status=status.HTTP_501_NOT_IMPLEMENTED,
            )
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Обращения'
        headers = [
            'id', 'full_name', 'object', 'device_type', 'phone', 'email_address', 'serial_numbers',
            'sentiment', 'category', 'question_summary', 'status', 'assignee', 'created_at', 'internal_notes',
        ]
        ws.append(headers)
        for row in qs:
            ws.append([
                row.id, row.full_name, row.object, row.device_type, row.phone, row.email_address,
                str(row.serial_numbers), row.sentiment, row.category, row.question_summary, row.status,
                row.assignee.get_full_name() or row.assignee.username if row.assignee else '',
                row.created_at.isoformat() if row.created_at else '', row.internal_notes,
            ])
        response = HttpResponse(
            save_virtual_workbook(wb),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="processed_export.xlsx"'
        return response




class KnowledgeBaseViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeBase.objects.all()
    serializer_class = KnowledgeBaseSerializer
    permission_classes = [IsAuthenticated]




class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().select_related('profile')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_fields = ('role',)
    search_fields = ('username', 'email', 'first_name', 'last_name')

    def get_queryset(self):
        qs = super().get_queryset()
        dept = self.request.query_params.get('department')
        if dept:
            qs = qs.filter(profile__department=dept)
        return qs

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()




class ProcessEmailView(APIView):
    """Заглушка для интеграции с агентом"""
    permission_classes = [IsAuthenticated, IsAdminOrAgent]

    def post(self, request):
        email_id = request.data.get('email_id')
        text = request.data.get('text')
        if not email_id and not text:
            return Response(
                {'detail': 'Укажите email_id или text для обработки'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if email_id:
            try:
                email = EmailMessage.objects.get(pk=email_id)
            except EmailMessage.DoesNotExist:
                return Response({'detail': 'Письмо не найдено'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'detail': 'Задача обработки поставлена в очередь', 'email_id': email.id})
        return Response({'detail': 'Обработка по тексту — реализуется в агенте', 'received_text': bool(text)})
