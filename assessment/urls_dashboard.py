from django.urls import path
from . import views_dashboard as dv

app_name = 'dashboard'

urlpatterns = [
    path('', dv.DashboardHomeView.as_view(), name='home'),
    path('employees/', dv.EmployeeListView.as_view(), name='employee_list'),
    path('employees/create/', dv.EmployeeCreateView.as_view(), name='employee_create'),
    path('employees/<int:pk>/delete/', dv.EmployeeDeleteView.as_view(), name='employee_delete'),
    path('employees/batch-import/', dv.EmployeeBatchImportView.as_view(), name='batch_import'),
    path('questions/', dv.QuestionListView.as_view(), name='question_list'),
    path('questions/<int:pk>/delete/', dv.QuestionDeleteView.as_view(), name='question_delete'),
    path('categories/', dv.CategoryListView.as_view(), name='category_list'),
    path('categories/<int:pk>/delete/', dv.CategoryDeleteView.as_view(), name='category_delete'),
    path('templates/', dv.TemplateListView.as_view(), name='template_list'),
    path('exams/', dv.ExamListView.as_view(), name='exam_list'),
    path('exams/import/', dv.ExamImportView.as_view(), name='exam_import'),
    path('tasks/', dv.TaskListView.as_view(), name='task_list'),
    path('tasks/create/', dv.TaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', dv.TaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/<str:action>/', dv.TaskStatusView.as_view(), name='task_status'),
    path('reports/', dv.ReportListView.as_view(), name='report_list'),
    path('reports/<int:pk>/pdf/', dv.ReportPdfDownloadView.as_view(), name='report_pdf'),
    path('reports/<int:pk>/ppt/', dv.ReportPptDownloadView.as_view(), name='report_ppt'),

    path('branches/', dv.BranchListView.as_view(), name='branch_list'),
    path('branches/create/', dv.BranchCreateView.as_view(), name='branch_create'),
    path('branches/<int:pk>/delete/', dv.BranchDeleteView.as_view(), name='branch_delete'),
    path('admins/', dv.AdminUserListView.as_view(), name='admin_list'),
    path('admins/create/', dv.AdminUserCreateView.as_view(), name='admin_create'),
    path('admins/<int:pk>/toggle/', dv.AdminUserToggleView.as_view(), name='admin_toggle'),
    path('admins/<int:pk>/reset-password/', dv.AdminUserResetPasswordView.as_view(), name='admin_reset_password'),
    path('settings/', dv.SystemSettingsView.as_view(), name='settings'),
    path('logs/', dv.LogListView.as_view(), name='log_list'),
]
