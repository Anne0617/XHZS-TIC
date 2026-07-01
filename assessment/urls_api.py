from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views_api
from . import import_tools
from . import views_public
from accounts.views import UserViewSet

router = DefaultRouter()
router.register(r'employees', views_api.EmployeeViewSet, basename='api_employees')
router.register(r'questions', views_api.QuestionViewSet, basename='api_questions')
router.register(r'tasks', views_api.TaskViewSet, basename='api_tasks')
router.register(r'results', views_api.ResultViewSet, basename='api_results')
router.register(r'branches', views_api.BranchViewSet, basename='api_branches')
router.register(r'projects', views_api.ProjectViewSet, basename='api_projects')
router.register('templates', views_api.TemplateViewSet, basename='api_templates')

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', views_api.session_login, name='api_session_login'),
    path('forgot-username/', views_api.forgot_username, name='api_forgot_username'),
    path('import-survey/', views_api.import_talent_survey, name='api_import_survey'),
    path('import-pdp-mbti/', import_tools.import_from_json, name='api_import_pdp_mbti'),
    path('results/<int:pk>/ppt/', views_api.download_report_ppt, name='api_report_ppt'),
    path('results/<int:pk>/pdf/', views_api.download_report_pdf, name='api_report_pdf'),
    path('results/export/excel/', views_api.export_results_excel, name='api_export_results_excel'),
    path('change-password/', views_api.change_password, name='api_change_password'),
    path('me/', views_api.me_view, name='api_me'),
    path('dashboard/', views_api.dashboard_stats, name='api_dashboard'),

    path('questions/import/', views_api.import_exam_file, name='api_import_exam_file'),
    path('questions/import-template/', views_api.download_import_template, name='api_import_template'),

    # 公开 API（不限权限）
    path('public/assess/<str:code>/', views_public.public_assess_detail, name='api_public_assess_detail'),
    path('public/assess/<str:code>/start/', views_public.public_assess_start, name='api_public_assess_start'),
    path('public/assess/<str:code>/submit/', views_public.public_assess_submit, name='api_public_assess_submit'),
    path('public/assess/<str:code>/result/', views_public.public_assess_result, name='api_public_assess_result'),
    path('public/templates/', views_public.public_template_list, name='api_public_templates'),
    path('public/qrcode/', views_public.public_qrcode_data, name='api_public_qrcode'),

    path('admins/', UserViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('admins/<int:pk>/toggle_lock/', UserViewSet.as_view({'post': 'toggle_lock'}), name='admin-toggle-lock'),
    path('admins/<int:pk>/reset_password/', UserViewSet.as_view({'post': 'reset_password'}), name='admin-reset-password'),
    path('', include(router.urls)),
]


