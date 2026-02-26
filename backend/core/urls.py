from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

router = DefaultRouter()
router.register(r'processed', views.ProcessedDataViewSet, basename='processed')
router.register(r'knowledge', views.KnowledgeBaseViewSet, basename='knowledge')
router.register(r'users', views.UserViewSet, basename='users')

urlpatterns = [
    path('auth/register/', views.RegisterView.as_view()),
    path('auth/login/', TokenObtainPairView.as_view()),
    path('auth/logout/', views.LogoutView.as_view()),
    path('auth/refresh/', TokenRefreshView.as_view()),
    path('auth/profile/', views.ProfileView.as_view()),
    path('auth/change-password/', views.ChangePasswordView.as_view()),
    path('processed/<int:processed_id>/comments/', views.ProcessedDataCommentsView.as_view()),
    path('processed/<int:processed_id>/comments/<int:comment_id>/', views.ProcessedDataCommentDetailView.as_view()),
    path('export/', views.ExportView.as_view()),
    path('process-email/', views.ProcessEmailView.as_view()),
    path('', include(router.urls)),
]
