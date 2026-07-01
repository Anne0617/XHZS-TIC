from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.contrib import messages
from .models import (
    QuestionCategory, Question, QuestionOption,
    AssessmentTemplate, TemplateQuestion,
    Employee, AssessmentTask, TaskAssignment,
    AssessmentSession, Answer, AssessmentResult,
    AssessmentReport, NotificationTemplate, SystemConfig
)


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 3
    fields = ['label', 'text', 'score', 'sort_order']


class TemplateQuestionInline(admin.TabularInline):
    model = TemplateQuestion
    extra = 5


class AnswerInline(admin.TabularInline):
    model = Answer
    readonly_fields = ['question', 'value', 'score', 'created_at']
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(QuestionCategory)
class QuestionCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'sort_order', 'is_active']
    list_editable = ['sort_order', 'is_active']
    search_fields = ['name', 'code']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text_preview', 'question_type', 'category', 'score', 'weight', 'is_reversed', 'is_active', 'review_status']
    list_filter = ['question_type', 'category', 'is_active', 'review_status', 'is_reversed']
    search_fields = ['text', 'category__name']
    list_editable = ['is_active', 'review_status']
    inlines = [QuestionOptionInline]
    fieldsets = (
        ('基本信息', {'fields': ('question_type', 'category', 'text', 'description')}),
        ('计分设置', {'fields': ('score', 'weight', 'is_reversed')}),
        ('状态', {'fields': ('is_active', 'review_status', 'created_by')}),
    )
    readonly_fields = ['created_at', 'updated_at']

    def text_preview(self, obj):
        return obj.text[:60]
    text_preview.short_description = '题目内容'


@admin.register(AssessmentTemplate)
class AssessmentTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'target_position', 'estimated_minutes', 'total_questions', 'is_active', 'import_button']
    list_filter = ['is_active', 'target_position']
    search_fields = ['name', 'description']
    inlines = [TemplateQuestionInline]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-docx/', self.admin_site.admin_view(self.import_docx_view),
                 name='assessment_assessmenttemplate_import_docx'),
        ]
        return custom_urls + urls

    def import_button(self, obj):
        from django.utils.html import format_html
        return format_html(
            '<a class="button" href="{}?template_id={}">导入Word</a>',
            '/admin/assessment/assessmenttemplate/import-docx/',
            obj.id,
        )
    import_button.short_description = '操作'
    import_button.allow_tags = True

    def import_docx_view(self, request):
        from django.http import HttpResponseRedirect
        from .import_tools import process_uploaded_docx

        template_id = request.GET.get('template_id')
        template = None
        if template_id:
            try:
                template = AssessmentTemplate.objects.get(id=template_id)
            except AssessmentTemplate.DoesNotExist:
                pass

        if request.method == 'POST':
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                messages.error(request, '请选择要上传的 .docx 文件。')
                return HttpResponseRedirect(request.path)

            if not uploaded_file.name.endswith('.docx'):
                messages.error(request, '仅支持 .docx 格式的 Word 文件。')
                return HttpResponseRedirect(request.path)

            replace = request.POST.get('replace_existing') == 'yes'
            selected_template_id = request.POST.get('template')
            selected_template = None
            if selected_template_id:
                try:
                    selected_template = AssessmentTemplate.objects.get(id=selected_template_id)
                except AssessmentTemplate.DoesNotExist:
                    pass

            result = process_uploaded_docx(
                uploaded_file,
                template=selected_template,
                request_user=request.user,
                replace_existing=replace,
            )

            if result['errors']:
                for err in result['errors']:
                    messages.error(request, err)
            else:
                messages.success(
                    request,
                    f'导入成功！创建/更新了 {len(result["categories"])} 个维度分类，'
                    f'导入了 {len(result["questions"])} 道题目。'
                )
                if selected_template:
                    messages.success(
                        request,
                        f'已关联到模板 "{selected_template.name}" （共 {selected_template.total_questions} 题）。'
                    )

            return HttpResponseRedirect(
                '/admin/assessment/assessmenttemplate/'
            )

        templates = AssessmentTemplate.objects.filter(is_active=True).order_by('name')
        return render(
            request,
            'admin/assessment/assessmenttemplate/import_docx.html',
            {
                'title': '从 Word 导入问卷',
                'templates': templates,
                'preselected_template': template,
                'opts': self.model._meta,
            },
        )


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'gender', 'position', 'branch', 'status', 'phone', 'created_at']
    list_filter = ['status', 'branch', 'gender', 'position']
    search_fields = ['name', 'phone', 'position', 'department']
    list_editable = ['status']


@admin.register(AssessmentTask)
class AssessmentTaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'template', 'branch', 'status', 'valid_from', 'valid_until', 'created_by']
    list_filter = ['status', 'branch', 'template']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = ['task', 'employee', 'status', 'access_code', 'assigned_at', 'completed_at']
    list_filter = ['status', 'task__branch']
    search_fields = ['employee__name', 'access_code', 'task__name']
    readonly_fields = ['assigned_at']


@admin.register(AssessmentSession)
class AssessmentSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'assignment', 'start_time', 'end_time', 'duration_seconds', 'is_valid']
    list_filter = ['is_valid', 'is_timeout']
    inlines = [AnswerInline]


@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'total_score', 'score_percent', 'risk_level', 'fit_score', 'is_abnormal']
    list_filter = ['risk_level', 'is_abnormal']
    search_fields = ['assignment__employee__name']
    readonly_fields = ['generated_at']


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'channel', 'is_active']
    list_filter = ['channel', 'is_active']


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'description']
    search_fields = ['key', 'description']
