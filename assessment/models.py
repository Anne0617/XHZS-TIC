from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from accounts.models import Branch, Project


class QuestionCategory(models.Model):
    """题目分类/测评维度"""
    name = models.CharField('维度名称', max_length=100)
    code = models.CharField('编码', max_length=50, unique=True, help_text='如 mental_health, stress_resistance')
    description = models.TextField('描述', blank=True)
    sort_order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('启用', default=True)

    class Meta:
        verbose_name = '题目分类'
        verbose_name_plural = '题目分类'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class Question(models.Model):
    """题目"""
    class QuestionType(models.TextChoices):
        SINGLE_CHOICE = 'single', '单选题'
        MULTIPLE_CHOICE = 'multiple', '多选题'
        LIKERT5 = 'likert5', '量表题(5级)'
        LIKERT7 = 'likert7', '量表题(7级)'

    question_type = models.CharField('题型', max_length=20, choices=QuestionType.choices, default=QuestionType.LIKERT5)
    category = models.ForeignKey(
        QuestionCategory, on_delete=models.CASCADE,
        verbose_name='所属维度', related_name='questions'
    )
    text = models.TextField('题目内容')
    description = models.TextField('说明/指导语', blank=True)
    sort_order = models.IntegerField('排序', default=0)
    score = models.DecimalField('默认分值', max_digits=5, decimal_places=1, default=1.0)
    weight = models.DecimalField('权重', max_digits=4, decimal_places=2, default=1.0, help_text='该题在维度中的权重系数')
    is_reversed = models.BooleanField('反向计分', default=False, help_text='量表题中高分表示消极则为反向')
    is_active = models.BooleanField('启用', default=True)
    review_status = models.CharField('审核状态', max_length=20,
        choices=[('pending', '待审核'), ('approved', '已通过'), ('rejected', '已驳回')],
        default='approved')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, verbose_name='创建人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '题目'
        verbose_name_plural = '题目'
        ordering = ['category', 'sort_order']

    def __str__(self):
        return f'[{self.category.name}] {self.text[:50]}...'


class QuestionOption(models.Model):
    """题目选项（单选题/多选题用）"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options', verbose_name='所属题目')
    label = models.CharField('选项标签', max_length=10, help_text='如 A、B、C 或 1、2、3')
    text = models.CharField('选项内容', max_length=200)
    score = models.DecimalField('分值', max_digits=5, decimal_places=1, default=0)
    sort_order = models.IntegerField('排序', default=0)

    class Meta:
        verbose_name = '题目选项'
        verbose_name_plural = '题目选项'
        ordering = ['question', 'sort_order']

    def __str__(self):
        return f'{self.label}. {self.text}'


class AssessmentTemplate(models.Model):
    """测评模板"""
    name = models.CharField('模板名称', max_length=200)
    description = models.TextField('描述', blank=True)
    target_position = models.CharField('适用岗位', max_length=100, blank=True, help_text='如 通用/销售/技术/管理')
    estimated_minutes = models.IntegerField('预计用时(分钟)', default=15)
    exam_type = models.CharField('考试类型', max_length=30, blank=True, default='', help_text='comprehensive, bigfive, pdp, mbti')
    is_active = models.BooleanField('启用', default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, verbose_name='创建人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '测评模板'
        verbose_name_plural = '测评模板'

    def __str__(self):
        return self.name

    @property
    def total_questions(self):
        return self.template_questions.count()


class TemplateQuestion(models.Model):
    """模板-题目关联（含权重）"""
    template = models.ForeignKey(AssessmentTemplate, on_delete=models.CASCADE, related_name='template_questions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='template_questions')
    weight = models.DecimalField('权重', max_digits=4, decimal_places=2, default=1.0)
    sort_order = models.IntegerField('排序', default=0)

    class Meta:
        verbose_name = '模板题目'
        verbose_name_plural = '模板题目'
        ordering = ['template', 'sort_order']
        unique_together = ['template', 'question']

    def __str__(self):
        return f'{self.template.name} - {self.question.text[:30]}'


class Employee(models.Model):
    """员工信息"""
    name = models.CharField('姓名', max_length=50)
    gender = models.CharField('性别', max_length=10, choices=[('male','男'),('female','女'),('other','其他')], blank=True)
    age = models.IntegerField('年龄', null=True, blank=True)
    phone = models.CharField('手机号', max_length=20, blank=True)
    email = models.EmailField('邮箱', blank=True)
    position = models.CharField('应聘岗位', max_length=100, blank=True)
    department = models.CharField('所属部门', max_length=100, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='所属分公司')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='所属项目')
    entry_date = models.DateField('入职时间', null=True, blank=True)
    status = models.CharField('状态', max_length=20,
        choices=[('pending','待测评'), ('assessed','已测评'), ('excluded','已排除')],
        default='pending')
    notes = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '员工信息'
        verbose_name_plural = '员工信息'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.position or "未填岗位"})'


class AssessmentTask(models.Model):
    """测评任务"""
    class TaskStatus(models.TextChoices):
        DRAFT = 'draft', '未开始'
        IN_PROGRESS = 'in_progress', '进行中'
        PAUSED = 'paused', '已暂停'
        FINISHED = 'finished', '已结束'
        CANCELLED = 'cancelled', '已作废'

    name = models.CharField('任务名称', max_length=200)
    template = models.ForeignKey(AssessmentTemplate, on_delete=models.CASCADE, verbose_name="测评模板")
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="所属分公司",
        help_text="超管可指定分公司，HR管理员自动关联")
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="所属项目")
    status = models.CharField('状态', max_length=20, choices=TaskStatus.choices, default=TaskStatus.DRAFT)
    description = models.TextField('任务说明', blank=True)

    # 时间设置
    valid_from = models.DateTimeField('有效期开始')
    valid_until = models.DateTimeField('有效期结束')
    duration_minutes = models.IntegerField('作答时长(分钟)', default=30)

    # 配置
    allow_retake = models.BooleanField('允许重新作答', default=False)
    is_anonymous = models.BooleanField('匿名作答', default=False, help_text='入职测评默认识名')
    max_retake_count = models.IntegerField('最大重答次数', default=1)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='创建人', related_name='created_tasks'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '测评任务'
        verbose_name_plural = '测评任务'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class TaskAssignment(models.Model):
    """任务分配（任务-员工关联）"""
    class AssignmentStatus(models.TextChoices):
        PENDING = 'pending', '待作答'
        IN_PROGRESS = 'in_progress', '作答中'
        COMPLETED = 'completed', '已完成'
        EXPIRED = 'expired', '已超时'
        INVALID = 'invalid', '已作废'

    task = models.ForeignKey(AssessmentTask, on_delete=models.CASCADE, related_name='assignments', verbose_name='测评任务')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='assignments', verbose_name='员工')
    access_code = models.CharField('测评码', max_length=20, unique=True, blank=True, null=True)
    status = models.CharField('状态', max_length=20, choices=AssignmentStatus.choices, default=AssignmentStatus.PENDING)
    assigned_at = models.DateTimeField('分配时间', auto_now_add=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    reminded_at = models.DateTimeField('最后提醒时间', null=True, blank=True)
    notes = models.TextField('备注', blank=True)

    class Meta:
        verbose_name = '任务分配'
        verbose_name_plural = '任务分配'
        unique_together = ['task', 'employee']

    def __str__(self):
        return f'{self.task.name} - {self.employee.name}'


class AssessmentSession(models.Model):
    """作答会话"""
    assignment = models.OneToOneField(TaskAssignment, on_delete=models.CASCADE, related_name='session', verbose_name='任务分配')
    start_time = models.DateTimeField('开始时间', auto_now_add=True)
    end_time = models.DateTimeField('结束时间', null=True, blank=True)
    duration_seconds = models.IntegerField('用时(秒)', default=0)
    is_timeout = models.BooleanField('是否超时提交', default=False)
    is_valid = models.BooleanField('是否有效', default=True)
    invalid_reason = models.CharField('无效原因', max_length=100, blank=True)
    device_info = models.CharField('设备信息', max_length=200, blank=True)
    ip_address = models.GenericIPAddressField('IP地址', blank=True, null=True)

    class Meta:
        verbose_name = '作答会话'
        verbose_name_plural = '作答会话'

    def __str__(self):
        return f'会话 #{self.id} - {self.assignment.employee.name}'


class Answer(models.Model):
    """答案记录"""
    session = models.ForeignKey(AssessmentSession, on_delete=models.CASCADE, related_name='answers', verbose_name='作答会话')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='题目')
    # 选择题：存选项ID（JSON），量表题：存分值
    value = models.TextField('原始答案', help_text='选择题存选项ID列表JSON，量表题存数值')
    score = models.DecimalField('得分', max_digits=5, decimal_places=1, default=0)
    created_at = models.DateTimeField('作答时间', auto_now_add=True)

    class Meta:
        verbose_name = '答案记录'
        verbose_name_plural = '答案记录'
        unique_together = ['session', 'question']

    def __str__(self):
        return f'{self.session.assignment.employee.name} - {self.question.text[:30]}'


class AssessmentResult(models.Model):
    """测评结果"""
    session = models.OneToOneField(AssessmentSession, on_delete=models.CASCADE, related_name='result', verbose_name='作答会话')
    assignment = models.OneToOneField(TaskAssignment, on_delete=models.CASCADE, related_name='result', verbose_name='任务分配')

    # 各维度得分（JSON存储，灵活扩展）
    dimension_scores = models.JSONField('维度得分', default=dict, help_text='{"dimension_code": {"score": 85, "max": 100, "level": "良好"}}')
    total_score = models.DecimalField('总分', max_digits=6, decimal_places=1, default=0)
    max_score = models.DecimalField('满分', max_digits=6, decimal_places=1, default=0)
    score_percent = models.DecimalField('得分率(%)', max_digits=5, decimal_places=1, default=0)

    # 风险标签
    risk_tags = models.JSONField('风险标签', default=list, help_text='["高焦虑","低抗压"]')
    risk_level = models.CharField('风险等级', max_length=20,
        choices=[('low','低风险'), ('medium','中风险'), ('high','高风险')],
        default='low')

    # 岗位适配建议
    fit_score = models.DecimalField('岗位适配度', max_digits=4, decimal_places=1, default=0, help_text='0-100')
    suggestion = models.TextField('综合建议', blank=True)
    hr_comment = models.TextField('HR人工评估意见', blank=True)

    # 异常检测
    is_abnormal = models.BooleanField('是否异常作答', default=False)
    abnormal_reason = models.CharField('异常原因', max_length=200, blank=True)

    generated_at = models.DateTimeField('生成时间', auto_now_add=True)

    class Meta:
        verbose_name = '测评结果'
        verbose_name_plural = '测评结果'

    def __str__(self):
        return f'{self.assignment.employee.name} - {self.score_percent}%'


class AssessmentReport(models.Model):
    """测评报告（缓存生成的HTML/PDF）"""
    result = models.OneToOneField(AssessmentResult, on_delete=models.CASCADE, related_name='report', verbose_name='测评结果')
    html_content = models.TextField('HTML报告', blank=True)
    pdf_file = models.FileField('PDF文件', upload_to='reports/', blank=True, null=True)
    is_pdf_generated = models.BooleanField('PDF已生成', default=False)
    created_at = models.DateTimeField('生成时间', auto_now_add=True)

    class Meta:
        verbose_name = '测评报告'
        verbose_name_plural = '测评报告'

    def __str__(self):
        return f'报告 #{self.id}'


class NotificationTemplate(models.Model):
    """通知模板（短信/邮件）"""
    class Channel(models.TextChoices):
        SMS = 'sms', '短信'
        EMAIL = 'email', '邮件'

    name = models.CharField('模板名称', max_length=100)
    channel = models.CharField('渠道', max_length=20, choices=Channel.choices)
    subject = models.CharField('标题', max_length=200, blank=True)
    content = models.TextField('内容', help_text='支持 {{employee_name}} {{task_name}} {{access_code}} {{valid_until}} 等变量')
    is_active = models.BooleanField('启用', default=True)

    class Meta:
        verbose_name = '通知模板'
        verbose_name_plural = '通知模板'

    def __str__(self):
        return f'{self.name} ({self.get_channel_display()})'


class SystemConfig(models.Model):
    """系统配置（超管设置）"""
    key = models.CharField('配置键', max_length=100, unique=True)
    value = models.TextField('配置值')
    description = models.CharField('说明', max_length=200, blank=True)

    class Meta:
        verbose_name = '系统配置'
        verbose_name_plural = '系统配置'

    def __str__(self):
        return self.key


