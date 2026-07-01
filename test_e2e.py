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


class EmployeeAccessView(TemplateView):
    """员工测评入口 - 直接跳转到直接答题页"""
    template_name = 'assessment/direct_entry.html'
    
    def get(self, request, *args, **kwargs):
        return redirect('/assessment/enter/')
    
    def get_context_data(self, **kwargs):
        from accounts.models import Branch
        ctx = super().get_context_data(**kwargs)
        ctx['branches'] = Branch.objects.filter(is_active=True).order_by('sort_order')
        ctx['selected_branch'] = self.request.GET.get('branch', '')
        return ctx





@method_decorator(csrf_exempt, name='post')

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
    
    def get(self, request,