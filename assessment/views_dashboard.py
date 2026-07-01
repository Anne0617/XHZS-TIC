from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, View
from django.contrib import messages
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta

from accounts.models import Branch, User, OperationLog
from assessment.models import (
    QuestionCategory, Question, QuestionOption,
    AssessmentTemplate, TemplateQuestion,
    AssessmentTask, TaskAssignment, Employee,
    AssessmentSession, Answer, AssessmentResult, SystemConfig
)


class HRAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (user.is_super_admin or user.is_hr_admin)
    def handle_no_permission(self):
        return redirect('admin:login')


class SuperAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_super_admin
    def handle_no_permission(self):
        messages.error(self.request, '无权访问，仅超级管理员可操作')
        return redirect('dashboard:home')


class DashboardHomeView(HRAdminRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['section'] = 'dashboard'
        user = self.request.user
        base_q = Q()
        if user.is_hr_admin and user.branch:
            base_q = Q(branch=user.branch)
        employees = Employee.objects.filter(base_q) if user.can_view_data else Employee.objects.none()
        tasks = AssessmentTask.objects.filter(base_q)
        ctx['total_employees'] = employees.count()
        ctx['assessed_count'] = employees.filter(status='assessed').count()
        ctx['pending_count'] = employees.filter(status='pending').count()
        ctx['total_tasks'] = tasks.count()
        ctx['active_tasks'] = tasks.filter(status='in_progress').count()
        recent_results = AssessmentResult.objects.filter(
            assignment__employee__branch=user.branch if user.is_hr_admin else None
        ) if user.can_view_data else AssessmentResult.objects.none()
        if user.is_hr_admin and user.branch:
            recent_results = recent_results.filter(assignment__employee__branch=user.branch)
        ctx['low_risk'] = recent_results.filter(risk_level='low').count()
        ctx['medium_risk'] = recent_results.filter(risk_level='medium').count()
        ctx['high_risk'] = recent_results.filter(risk_level='high').count()
        month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0)
        ctx['month_assessed'] = recent_results.filter(generated_at__gte=month_start).count()
        return ctx


class EmployeeListView(HRAdminRequiredMixin, ListView):
    model = Employee
    template_name = 'dashboard/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 20
    def get_queryset(self):
        qs = Employee.objects.all()
        if self.request.user.is_hr_admin and self.request.user.branch:
            qs = qs.filter(Q(branch=self.request.user.branch) | Q(branch__isnull=True))
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(phone__icontains=search) | Q(position__icontains=search))
        return qs.prefetch_related('assignments__result').order_by('-created_at')
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['section'] = 'employees'
        from accounts.models import Branch
        if self.request.user.is_super_admin:
            ctx['branches'] = Branch.objects.filter(is_active=True).order_by('sort_order')
        elif self.request.user.branch:
            ctx['branches'] = [self.request.user.branch]
        else:
            ctx['branches'] = []
        return ctx


class EmployeeCreateView(HRAdminRequiredMixin, View):
    def post(self, request):
        employee = Employee.objects.create(
            name=request.POST.get('name'),
            gender=request.POST.get('gender', ''),
            age=request.POST.get('age') or None,
            phone=request.POST.get('phone', ''),
            email=request.POST.get('email', ''),
            position=request.POST.get('position', ''),
            department=request.POST.get('department', ''),
            branch=request.user.branch if request.user.is_hr_admin else Branch.objects.get(pk=request.POST.get('branch')),
            entry_date=request.POST.get('entry_date') or None,
        )
        OperationLog.objects.create(user=request.user, action=f'添加员工 {employee.name}')
        messages.success(request, f'员工 "{employee.name}" 已添加')
        return redirect('dashboard:employee_list')


class EmployeeDeleteView(HRAdminRequiredMixin, View):
    def post(self, request, pk):
        emp = get_object_or_404(Employee, pk=pk)
        OperationLog.objects.create(user=request.user, action=f'删除员工 {emp.name}')
        emp.delete()
        messages.success(request, '员工已删除')
        return redirect('dashboard:employee_list')


class ExamListView(HRAdminRequiredMixin, ListView):
    model = AssessmentTemplate
    template_name = 'dashboard/question_list.html'
    context_object_name = 'templates'
    def get_queryset(self):
        return AssessmentTemplate.objects.filter(
            exam_type__in=['comprehensive', 'bigfive', 'pdp', 'mbti']
        ).order_by('exam_type')
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['section'] = 'questions'
        return ctx

class QuestionListView(HRAdminRequiredMixin, ListView):
    model = Question
    template_name = 'dashboard/question_list.html'
    context_object_name = 'questions'
    paginate_by = 20
    def get_queryset(self):
        qs = Question.objects.select_related('category').all()
        cat = self.request.GET.get('category', '')
        qtype = self.request.GET.get('type', '')
        if cat: qs = qs.filter(category_id=cat)
        if qtype: qs = qs.filter(question_type=qtype)
        search = self.request.GET.get('search', '')
        if search: qs = qs.filter(text__icontains=search)
        return qs.order_by('category', 'sort_order')
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['section'] = 'question_list'
        ctx['categories'] = QuestionCategory.objects.all()
        ctx['selected_cat'] = self.request.GET.get('category', '')
        ctx['selected_type'] = self.request.GET.get('type', '')
        return ctx


class QuestionDeleteView(HRAdminRequiredMixin, View):
    def post(self, request, pk):
        q = get_object_or_404(Question, pk=pk)
        q.delete()
        messages.success(request, '题目已删除')
        return redirect('dashboard:question_list')


class CategoryListView(HRAdminRequiredMixin, ListView):
    model = QuestionCategory
    template_name = 'dashboard/category_list.html'
    context_object_name = 'categories'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['section'] = 'categories'
        return ctx


class CategoryDeleteView(HRAdminRequiredMixin, View):
    def post(self, request, pk):
        cat = get_object_or_404(QuestionCategory, pk=pk)
        cat.delete()
        messages.success(request, '维度已删除')
        return redirect('dashboard:category_list')


class TemplateListView(HRAdminRequiredMixin, ListView):
    model = AssessmentTemplate
    template_name = 'dashboard/template_list.html'
    context_object_name = 'templates'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['section'] = 'templates'
        return ctx


class TaskListView(HRAdminRequiredMixin, ListView):
    model = AssessmentTask
    template_name = 'dashboard/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 20
    def get_queryset(self):
        qs = AssessmentTask.objects.select_related('template', 'branch', 'created_by').all()
        if self.request.user.is_hr_admin and self.request.user.branch:
            qs = qs.filter(Q(branch=self.request.user.branch) | Q(branch__isnull=True))
        status = self.request.GET.get('status', '')
        if status: qs = qs.filter(status=status)
        return qs.prefetch_related('assignments__result').order_by('-created_at')
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['section'] = 'tasks'
        ctx['selected_status'] = self.request.GET.get('status', '')
        return ctx


class TaskCreateView(HRAdminRequiredMixin, TemplateView):
    template_name = 'dashboard/task_create.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['section'] = 'tasks'
        ctx['templates'] = AssessmentTemplate.objects.filter(is_active=True)
        qs = Employee.objects.all()
        if self.request.user.is_hr_admin and self.request.user.branch:
            qs = qs.filter(Q(branch=self.request.user.branch) | Q(branch__isnull=True))
        ctx['employees'] = qs.filter(status='pending').order_by('-created_at')
        ctx['branches'] = Branch.objects.filter(is_active=True)
        return ctx
    def post(self, request):
        template = get_object_or_404(AssessmentTemplate, pk=request.POST.get('template'))
        branch_id = request.POST.get('branch') or (request.user.branch_id if request.user.is_hr_admin else None)
        employee_ids = request.POST.getlist('employees')
        if not employee_ids:
            messages.error(request, '请选择至少一名员工')
            return redirect('dashboard:task_create')
        now = timezone.now()
        valid_days = int(request.POST.get('valid_days', 7))
        duration = int(request.POST.get('duration_minutes', 30))
        task = AssessmentTask.objects.create(
            name=request.POST.get('name', f'入职测评 - {now.strftime("%Y%m%d")}'),
            template=template, branch_id=branch_id, status='in_progress',
            valid_from=now, valid_until=now + timedelta(days=valid_days),
            duration_minutes=duration, created_by=request.user,
        )
        for emp_id in employee_ids:
            emp = Employee.objects.get(pk=emp_id)
            code = f'PS{now.strftime("%m%d")}{emp.id:04d}'
            TaskAssignment.objects.create(task=task, employee=emp, access_code=code)
            emp.status = 'pending'
            emp.save()
        OperationLog.objects.create(user=request.user, action=f'创建测评任务 {task.name}，下发 {len(employee_ids)} 人')
        messages.success(request, f'任务 "{task.name}" 已创建，已下发 {len(employee_ids)} 名员工')
        return redirect('dashboard:task_detail', pk=task.pk)


class TaskDetailView(HRAdminRequiredMixin, TemplateView):
    template_name = 'dashboard/task_detail.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        task = get_object_or_404(AssessmentTask, pk=self.kwargs['pk'])
        ctx['task'] = task
        ctx['section'] = 'tasks'
        ctx['assignments'] = TaskAssignment.objects.filter(task=task).select_related('employee').all()
        ctx['completed_count'] = ctx['assignments'].filter(status='completed').count()
        ctx['pending_count'] = ctx['assignments'].filter(status='pending').count()
        ctx['expired_count'] = ctx['assignments'].filter(status='expired').count()
        return ctx


class TaskStatusView(HRAdminRequiredMixin, View):
    def post(self, request, pk, action):
        task = get_object_or_404(AssessmentTask, pk=pk)
        actions = {'pause': 'paused', 'resume': 'in_progress', 'finish': 'finished', 'cancel': 'cancelled'}
        if action in actions:
            task.status = actions[action]
            task.save()
            OperationLog.objects.create(user=request.user, action=f'变更任务 {task.name} 状态为 {task.status}')
            messages.success(request, '任务状态已更新')
        return redirect('dashboard:task_detail', pk=task.pk)


class ReportListView(HRAdminRequiredMixin, ListView):
    model = AssessmentResult
    template_name = 'dashboard/report_list.html'
    context_object_name = 'results'
    paginate_by = 20
    def get_queryset(self):
        qs = AssessmentResult.objects.select_related('session', 'assignment__employee', 'assignment__task').all()
        user = self.request.user
        if user.is_hr_admin and user.branch:
            qs = qs.filter(assignment__employee__branch=user.branch)
        risk = self.request.GET.get('risk', '')
        if risk: qs = qs.filter(risk_level=risk)
        return qs.order_by('-generated_at')
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['section'] = 'reports'
        ctx['selected_risk'] = self.request.GET.get('risk', '')
        return ctx


class BranchListView(SuperAdminRequiredMixin, ListView):
    model = Branch
    template_name = 'dashboard/branch_list.html'
    context_object_name = 'branches'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['section'] = 'branches'
        return ctx


class BranchCreateView(SuperAdminRequiredMixin, View):
    def post(self, request):
        Branch.objects.create(name=request.POST.get('name'), code=request.POST.get('code'),
            contact_phone=request.POST.get('phone', ''), address=request.POST.get('address', ''))
        messages.success(request, '分公司已添加')
        return redirect('dashboard:branch_list')


class BranchDeleteView(SuperAdminRequiredMixin, View):
    def post(self, request, pk):
        b = get_object_or_404(Branch, pk=pk)
        b.delete()
        messages.success(request, '分公司已删除')
        return redirect('dashboard:branch_list')


class AdminUserListView(SuperAdminRequiredMixin, ListView):
    model = User
    template_name = 'dashboard/admin_list.html'
    context_object_name = 'admins'
    paginate_by = 20
    def get_queryset(self):
        return User.objects.exclude(role=User.Role.SUPER_ADMIN).select_related('branch').all()
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['section'] = 'admins'
        ctx['branches'] = Branch.objects.filter(is_active=True)
        return ctx


class AdminUserCreateView(SuperAdminRequiredMixin, View):
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            messages.error(request, f'用户名 "{username}" 已存在')
            return redirect('dashboard:admin_list')
        user = User.objects.create(username=username, role=User.Role.HR_ADMIN,
            branch_id=request.POST.get('branch') or None,
            first_name=request.POST.get('full_name', ''),
            department='人力资源部',
            can_manage_questions=request.POST.get('can_manage_questions') == 'on',
            can_manage_tasks=request.POST.get('can_manage_tasks') == 'on',
            can_view_data=request.POST.get('can_view_data') == 'on',
            can_export_data=request.POST.get('can_export_data') == 'on',
            can_manage_employees=request.POST.get('can_manage_employees') == 'on',
        )
        user.set_password(password)
        user.save()
        OperationLog.objects.create(user=request.user, action=f'创建管理员账号 {username}')
        messages.success(request, f'管理员 "{request.POST.get("full_name", username)}" 创建成功')
        return redirect('dashboard:admin_list')


class AdminUserToggleView(SuperAdminRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user.is_super_admin:
            messages.error(request, '无法冻结超管账号')
        else:
            user.is_locked = not user.is_locked
            user.is_active = not user.is_locked
            user.save()
            OperationLog.objects.create(user=request.user, action=f'{"冻结" if user.is_locked else "解冻"}管理员 {user.username}')
            messages.success(request, f'账号 {user.username} 已{"冻结" if user.is_locked else "解冻"}')
        return redirect('dashboard:admin_list')


class AdminUserResetPasswordView(SuperAdminRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        new_pw = request.POST.get('new_password', 'hr123456')
        user.set_password(new_pw)
        user.save()
        OperationLog.objects.create(user=request.user, action=f'重置管理员 {user.username} 密码')
        messages.success(request, f'密码已重置为: {new_pw}')
        return redirect('dashboard:admin_list')


class SystemSettingsView(SuperAdminRequiredMixin, TemplateView):
    template_name = 'dashboard/settings.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['section'] = 'settings'
        configs = SystemConfig.objects.all()
        ctx['configs'] = {c.key: c for c in configs}
        return ctx
    def post(self, request):
        for key in ['system_name', 'default_duration', 'default_valid_days', 'copyright_info']:
            val = request.POST.get(key, '')
            SystemConfig.objects.update_or_create(key=key, defaults={'value': val})
        OperationLog.objects.create(user=request.user, action='修改系统设置')
        messages.success(request, '系统设置已保存')
        return redirect('dashboard:settings')




class ReportPdfDownloadView(HRAdminRequiredMixin, View):
    def get(self, request, pk):
        from .models import AssessmentResult
        result = get_object_or_404(AssessmentResult, pk=pk)
        user = request.user
        if user.is_hr_admin and user.branch:
            if result.assignment.employee.branch_id != user.branch_id:
                messages.error(request, '无权访问该报告')
                return redirect('dashboard:report_list')
        try:
            from .pdf_report import generate_report_pdf
            pdf_bytes = generate_report_pdf(result)
            from django.http import HttpResponse
            emp_name = result.assignment.employee.name
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename=TIC_Report_{emp_name}_{result.generated_at.strftime("%Y%m%d")}.pdf'
            return response
        except Exception as e:
            messages.error(request, f'PDF生成失败: {str(e)}')
            return redirect('dashboard:report_list')

class ReportPptDownloadView(HRAdminRequiredMixin, View):
    def get(self, request, pk):
        from .models import AssessmentResult
        result = get_object_or_404(AssessmentResult, pk=pk)
        user = request.user
        if user.is_hr_admin and user.branch:
            if result.assignment.employee.branch_id != user.branch_id:
                messages.error(request, '无权访问该报告')
                return redirect('dashboard:report_list')
        try:
            from .ppt_report import generate_report_ppt
            pptx_bytes = generate_report_ppt(result)
            from django.http import HttpResponse
            emp_name = result.assignment.employee.name
            response = HttpResponse(pptx_bytes, content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation')
            response['Content-Disposition'] = 'attachment; filename=TIC_Report_' + emp_name + '_' + result.generated_at.strftime('%Y%m%d') + '.pptx'
            return response
        except Exception as e:
            messages.error(request, f'PPT生成失败: {str(e)}')
            return redirect('dashboard:report_list')




class EmployeeBatchImportView(HRAdminRequiredMixin, View):
    def post(self, request):
        from accounts.models import Branch
        branch_id = request.POST.get('branch')
        emp_data = request.POST.get('employees_data', '').strip()
        if not emp_data:
            messages.error(request, '请输入员工数据')
            return redirect('dashboard:employee_list')
        lines = emp_data.split(chr(10))
        count = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(',')]
            if len(parts) < 2:
                continue
            dept = parts[0]
            name = parts[1]
            gender = parts[2] if len(parts) > 2 else ''
            position = parts[3] if len(parts) > 3 else ''
            phone = parts[4] if len(parts) > 4 else ''
            email = parts[5] if len(parts) > 5 else ''
            gender_val = 'male' if gender == '男' else ('female' if gender == '女' else '')
            Employee.objects.create(
                name=name, gender=gender_val, phone=phone, email=email,
                position=position, department=dept,
                branch_id=branch_id if branch_id else (request.user.branch_id if request.user.branch else None),
            )
            count += 1
        if count > 0:
            messages.success(request, f'成功导入 {count} 名员工')
            OperationLog.objects.create(user=request.user, action=f'批量导入{count}名员工')
        return redirect('dashboard:employee_list')

class ExamImportView(HRAdminRequiredMixin, View):
    template_name = 'dashboard/exam_import.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            messages.error(request, '请选择文件')
            return render(request, self.template_name)
        
        if not uploaded_file.name.endswith('.html'):
            messages.error(request, '请上传 .html 格式文件')
            return render(request, self.template_name)
        
        try:
            import os
            from django.conf import settings
            data_dir = os.path.join(settings.BASE_DIR, 'assessment', 'data')
            os.makedirs(data_dir, exist_ok=True)
            filepath = os.path.join(data_dir, 'survey_questions.html')
            with open(filepath, 'wb+') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
            from django.core.management import call_command
            from io import StringIO
            out = StringIO()
            call_command('import_exam_questions', stdout=out)
            output = out.getvalue()
            messages.success(request, f'导入成功！\\n' + output.split('\\n')[-2] if output else '导入完成')
        except Exception as e:
            messages.error(request, f'导入失败: {str(e)}')
        
        return redirect('dashboard:exam_list')


class LogListView(SuperAdminRequiredMixin, ListView):
    model = OperationLog
    template_name = 'dashboard/log_list.html'
    context_object_name = 'logs'
    paginate_by = 30
    def get_queryset(self):
        return OperationLog.objects.select_related('user').all().order_by('-created_at')
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['section'] = 'logs'
        return ctx
