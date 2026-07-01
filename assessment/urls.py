from django.urls import path
from . import views
from . import views_employee as ev
from .views_employee import PublicExamQRCodeView


app_name = 'assessment'

urlpatterns = [

    path('assessment/exam-qrcode/', PublicExamQRCodeView.as_view(), name='exam_qrcode'),
    path('', views.HomeView.as_view(), name='home'),
    # 员工测评入口
    path('assessment/', ev.EmployeeAccessView.as_view(), name='employee_access'),
    path('assessment/enter/', ev.EmployeeDirectEntryView.as_view(), {'exam_type': 'comprehensive'}, name='employee_direct_enter'),
        path('assessment/enter/<slug:exam_type>/', ev.EmployeeDirectEntryView.as_view(), name='employee_direct'),
    path('assessment/take/<str:code>/', ev.EmployeeTakeView.as_view(), name='employee_take'),
    path('assessment/submit/<str:code>/', ev.EmployeeSubmitView.as_view(), name='employee_submit'),
    path('assessment/thanks/', ev.EmployeeThanksView.as_view(), name='employee_thanks'),
    path('assessment/qrcode/<int:branch_id>/', ev.EmployeeQRCodeView.as_view(), name='employee_qrcode'),
    path('assessment/result/<str:code>/', ev.EmployeeResultView.as_view(), name='employee_result'),

]

