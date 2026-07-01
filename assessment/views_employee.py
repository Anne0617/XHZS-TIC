import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from decimal import Decimal

from assessment.models import (
    Employee,

    TaskAssignment, AssessmentSession, Answer, AssessmentResult,
    AssessmentReport, Question, QuestionOption, TemplateQuestion,
)
from accounts.models import OperationLog
from django.http import Http404


class EmployeeAccessView(View):
    """员工测评入口 - 根据code参数跳转到答题页"""
    def get(self, request, *args, **kwargs):
        code = request.GET.get("code", "")
        if code:
            return redirect(f"/assessment/take/{code}/")
        return redirect("/")





@method_decorator(csrf_exempt, name='dispatch')

class EmployeeDirectEntryView(TemplateView):
    """通过URL指定考试类型，不提供选择"""
    template_name = 'assessment/direct_entry.html'
    
    def get_template_by_exam_type(self, exam_type):
        from assessment.models import AssessmentTemplate
        try:
            return AssessmentTemplate.objects.get(exam_type=exam_type, is_active=True)
        except AssessmentTemplate.DoesNotExist:
            return None
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        exam_type = self.kwargs.get('exam_type', '')
        if exam_type:
            tpl = self.get_template_by_exam_type(exam_type)
            ctx['exam'] = tpl
        else:
            ctx['exam'] = None
        return ctx
    
    def get(self, request, *args, **kwargs):
        exam_type = self.kwargs.get('exam_type', '')
        if not exam_type:
            raise Http404('请指定考试类型')
        tpl = self.get_template_by_exam_type(exam_type)
        if not tpl:
            raise Http404('\u8003\u8bd5\u7c7b\u578b\u4e0d\u5b58\u5728')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        from assessment.models import AssessmentTemplate, AssessmentTask, TaskAssignment, AssessmentSession
        from assessment.models import Employee
        from django.utils import timezone
        from datetime import timedelta
        
        exam_type = self.kwargs.get('exam_type', '')
        if not exam_type:
            messages.error(request, '\u8003\u8bd5\u7c7b\u578b\u65e0\u6548')
            return redirect('/assessment/qrcode/')
        
        tpl = self.get_template_by_exam_type(exam_type)
        if not tpl:
            messages.error(request, '\u8003\u8bd5\u7c7b\u578b\u4e0d\u5b58\u5728')
            return redirect('/assessment/qrcode/')
        
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        department = request.POST.get('department', '').strip()
        position = request.POST.get('position', '').strip()
        
        if not name:
            messages.error(request, '\u8bf7\u586b\u5199\u59d3\u540d')
            return redirect(f'/assessment/enter/{exam_type}/')
        if not phone:
            messages.error(request, '\u8bf7\u586b\u5199\u624b\u673a\u53f7')
            return redirect(f'/assessment/enter/{exam_type}/')
        # phone dedup
        dup = Employee.objects.filter(phone=phone).first()
        if dup:
            done = TaskAssignment.objects.filter(employee=dup, status='completed').exists()
            if done:
                messages.error(request, '该手机号已完成测评，请勿重复提交')
                return redirect(f'/assessment/enter/{exam_type}/')
            
            # 存在但未完成: 复用该员工
            emp = dup
            emp.name = name
            emp.department = department or ''
            emp.position = position or ''
            emp.save()
        else:
            emp = Employee.objects.create(
                name=name, phone=phone,
                department=department or '',
                position=position or '',
                status='pending',
            )
        
        now = timezone.now()
        code = 'EX' + now.strftime('%m%d') + str(emp.id).zfill(4)
        
        task = AssessmentTask.objects.create(
            name=tpl.name + ' - ' + name,
            template=tpl,
            status='in_progress',
            valid_from=now,
            valid_until=now + timedelta(days=7),
            duration_minutes=15,
            created_by=None,
        )
        
        assign = TaskAssignment.objects.create(
            task=task, employee=emp, access_code=code, status='pending',
        )
        
        session = AssessmentSession.objects.create(assignment=assign)
        assign.status = 'in_progress'
        assign.save()
        
        return redirect('/assessment/take/' + code + '/')

class EmployeeTakeView(TemplateView):
    """作答页面"""
    template_name = 'assessment/take.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        code = self.kwargs['code']
        assign = get_object_or_404(
            TaskAssignment.objects.select_related('task__template', 'employee'),
            access_code=code
        )

        # 检查是否已有进行中的会话
        session = AssessmentSession.objects.filter(
            assignment=assign, end_time__isnull=True
        ).first()

        if not session:
            # 创建新会话
            session = AssessmentSession.objects.create(assignment=assign)
            assign.status = 'in_progress'
            assign.save()

        # 获取模板题目
        template = assign.task.template
        tqs = TemplateQuestion.objects.filter(template=template) \
            .select_related('question__category') \
            .order_by('sort_order')

        questions = []
        for tq in tqs:
            q = tq.question
            opts = QuestionOption.objects.filter(question=q).order_by('sort_order')
            questions.append({
                'id': q.id,
                'text': q.text,
                'type': q.question_type,
                'is_reversed': q.is_reversed,
                'category': q.category.name,
                'options': [{'id': o.id, 'label': o.label, 'text': o.text, 'score': float(o.score)} for o in opts],
            })

        ctx['assignment'] = assign
        ctx['questions'] = questions
        ctx['task'] = assign.task
        ctx['employee'] = assign.employee
        ctx['session'] = session
        ctx['duration_minutes'] = assign.task.duration_minutes
        ctx['questions_json'] = json.dumps(questions, ensure_ascii=False)
        return ctx


@method_decorator(csrf_exempt, name='dispatch')
class EmployeeSubmitView(View):
    """提交作答"""
    def post(self, request, code):
        assign = get_object_or_404(TaskAssignment, access_code=code)
        session = AssessmentSession.objects.filter(assignment=assign, end_time__isnull=True).first()

        if assign.status == "completed":
            messages.error(request, '已完成')
            return redirect('/assessment/thanks/')

        if not session:
            messages.error(request, '会话异常，请重新开始')
            return redirect('/assessment/thanks/')

        try:
            with transaction.atomic():
                # 保存答案
                answers_data = {}
                total_score = Decimal('0')
                max_score = Decimal('0')
                dimension_scores = {}
    
                for key, value in request.POST.items():
                    if key.startswith('q_'):
                        q_id = int(key[2:])
                        question = get_object_or_404(Question, pk=q_id)
    
                        # 计算得分
                        score = Decimal('0')
                        if question.question_type in ('likert5', 'likert7'):
                            score = Decimal(value)
                            if question.is_reversed:
                                # 反向计分: 6 - score (for 5级: 1->5, 2->4, etc.)
                                max_val = 5 if question.question_type == 'likert5' else 7
                                score = Decimal(max_val + 1) - score
                        else:
                            # 单选题/多选题
                            opt = QuestionOption.objects.filter(pk=int(value)).first()
                            if opt:
                                score = opt.score
    
                        # 保存答案
                        Answer.objects.create(
                            session=session,
                            question=question,
                            value=str(value),
                            score=score,
                        )
    
                        # 累加维度得分
                        cat_code = question.category.code
                        if cat_code not in dimension_scores:
                            dimension_scores[cat_code] = {
                                'name': question.category.name,
                                'score': Decimal('0'),
                                'max': Decimal('0'),
                                'count': 0,
                            }
                        dimension_scores[cat_code]['score'] += score
                        dimension_scores[cat_code]['max'] += question.score
                        dimension_scores[cat_code]['count'] += 1
    
                        total_score += score
                        max_score += question.score
    
                # 计算得分率
                score_percent = (total_score / max_score * 100) if max_score > 0 else Decimal('0')
    
                # 计算各维度得分和风险等级
                dimension_result = {}
                risk_tags = []
                risk_count = 0
                for code, ds in dimension_scores.items():
                    percent = (ds['score'] / ds['max'] * 100) if ds['max'] > 0 else Decimal('0')
                    if percent < 40:
                        level = '有风险'
                        risk_tags.append(f'{ds["name"]}需关注')
                        risk_count += 1
                    elif percent < 60:
                        level = '需关注'
                        risk_tags.append(f'{ds["name"]}需关注')
                    else:
                        level = '健康'
                    dimension_result[code] = {
                        'name': ds['name'],
                        'score': float(ds['score']),
                        'max': float(ds['max']),
                        'percent': float(percent),
                        'level': level,
                    }
    
                # 计算适配度
                fit_score = float(score_percent)
                if fit_score >= 70:
                    risk_level = 'low'
                elif fit_score >= 50:
                    risk_level = 'medium'
                else:
                    risk_level = 'high'
    
                # 异常检测
                duration = int((timezone.now() - session.start_time).total_seconds())
                is_abnormal = duration < 60  # 1分钟内提交判为异常
    
                # 更新会话
                session.end_time = timezone.now()
                session.duration_seconds = duration
                session.is_valid = not is_abnormal
                if is_abnormal:
                    session.invalid_reason = '作答时间过短'
                session.save()
    
                # 创建结果
                result = AssessmentResult.objects.create(
                    session=session,
                    assignment=assign,
                    total_score=float(total_score),
                    max_score=float(max_score),
                    score_percent=float(score_percent),
                    dimension_scores=dimension_result,
                    risk_tags=risk_tags,
                    risk_level=risk_level,
                    fit_score=fit_score,
                    is_abnormal=is_abnormal,
                    abnormal_reason=session.invalid_reason,
                )
    
                # 生成简易报告
                generate_report(result)
    
                # 更新分配状态
                assign.status = 'completed'
                assign.completed_at = timezone.now()
                assign.save()
    
                # 更新员工状态
                assign.employee.status = 'assessed'
                assign.employee.save()
    
                OperationLog.objects.create(
                    action=f'员工 {assign.employee.name} 完成测评 {assign.task.name}'
                )
    
            return redirect('/assessment/thanks/')
        except Exception:
            import traceback, sys
            traceback.print_exc(file=sys.stderr)
            messages.error(request, '\u63d0\u4ea4\u5931\u8d25')
            return redirect('/assessment/')


def generate_report(result):
    """生成测评报告"""
    dims = result.dimension_scores
    employee = result.assignment.employee
    task = result.assignment.task

    html_parts = []
    html_parts.append(f'<h2>{employee.name} - 入职人才测评报告</h2>')
    html_parts.append(f'<p>岗位: {employee.position} | 测评任务: {task.name}</p>')
    html_parts.append(f'<p>测评时间: {result.generated_at.strftime("%Y-%m-%d %H:%M")}</p>')
    html_parts.append(f'<p><strong>综合得分率: {result.score_percent:.1f}%</strong></p>')
    html_parts.append(f'<p><strong>岗位适配度: {result.fit_score:.1f}</strong></p>')
    风险_map = {"low": "健康", "medium": "有风险", "high": "有风险"}
    html_parts.append(f'<p>风险等级: {风险_map.get(result.risk_level, result.risk_level)}</p>')

    if result.risk_tags:
        html_parts.append('<p>关注项: ' + ', '.join(result.risk_tags) + '</p>')

    html_parts.append('<h3>各维度得分</h3><table border="1" cellpadding="6" style="border-collapse:collapse;width:100%;">')
    html_parts.append('<tr><th>维度</th><th>得分</th><th>满分</th><th>得分率</th><th>评估</th></tr>')
    for code, d in dims.items():
        html_parts.append(f'<tr><td>{d["name"]}</td><td>{d["score"]:.1f}</td><td>{d["max"]:.1f}</td><td>{d["percent"]:.1f}%</td><td>{d["level"]}</td></tr>')
    html_parts.append('</table>')

    if result.is_abnormal:
        html_parts.append(f'<p style="color:red;">注意: 该测评可能存在异常 ({result.abnormal_reason})，建议HR复核</p>')

    AssessmentReport.objects.create(
        result=result,
        html_content=''.join(html_parts),
    )




class EmployeeQRCodeView(TemplateView):
    template_name = 'assessment/qrcode.html'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from accounts.models import Branch
        branch = Branch.objects.filter(pk=self.kwargs['branch_id']).first()
        ctx['branch'] = branch
        ctx['entry_url'] = '/assessment/enter/?branch=' + str(branch.id) if branch else '/assessment/enter/'
        return ctx
class EmployeeResultView(TemplateView):
    """测评结果页"""
    template_name = 'assessment/result.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        code = self.kwargs['code']
        assign = get_object_or_404(
            TaskAssignment.objects.select_related('employee', 'task__template'),
            access_code=code
        )
        result = AssessmentResult.objects.filter(assignment=assign).first()
        report = AssessmentReport.objects.filter(result=result).first() if result else None

        ctx['assignment'] = assign
        ctx['result'] = result
        ctx['report'] = report
        ctx['employee'] = assign.employee
        return ctx


class EmployeeThanksView(TemplateView):
    """提交后的感谢页面"""
    template_name = 'assessment/thanks.html'


class PublicExamQRCodeView(TemplateView):
    template_name = 'assessment/qrcode.html'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from assessment.models import AssessmentTemplate
        ctx['exam_templates'] = AssessmentTemplate.objects.filter(
            is_active=True
        ).order_by('name')
        ctx['entry_url'] = '/assessment/enter/'
        ctx['site_url'] = self.request.build_absolute_uri('/').rstrip('/')
        return ctx

    """提交后的感谢页面"""

