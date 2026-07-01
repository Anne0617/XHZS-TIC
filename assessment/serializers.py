from rest_framework import serializers
from accounts.models import User, Branch, Project
from assessment.models import Employee, QuestionCategory, Question, AssessmentTemplate, TemplateQuestion, AssessmentTask, AssessmentResult

class UserSerializer(serializers.ModelSerializer):
    role_display_name = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'role', 'role_display_name', 'branch', 'project', 'is_super_admin', 'is_project_admin']
    def get_role_display_name(self, obj):
        labels = {'super_admin':'超管本部','hr_admin':'分公司管理员','project_admin':'项目管理员'}
        return labels.get(obj.role, obj.role)

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    class Meta:
        model = Question
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    class Meta:
        model = AssessmentTask
        fields = '__all__'

class ResultSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='assignment.employee.name', read_only=True)
    task_name = serializers.CharField(source='assignment.task.name', read_only=True)
    class Meta:
        model = AssessmentResult
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        level_map = {
            'high_risk': '有风险',
            'medium_risk': '需关注',
            'good': '健康',
            '良好': '健康',
        }
        dims = data.get('dimension_scores', {})
        if dims:
            for code, d in dims.items():
                if isinstance(d, dict) and d.get('level'):
                    d['level'] = level_map.get(d['level'], d['level'])
        return data

class DashboardStatsSerializer(serializers.Serializer):
    total_employees = serializers.IntegerField()
    assessed_count = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    total_tasks = serializers.IntegerField()
    low_risk = serializers.IntegerField()
    medium_risk = serializers.IntegerField()
    high_risk = serializers.IntegerField()


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = "__all__"

class ProjectSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    class Meta:
        model = Project
        fields = "__all__"


class TemplateSerializer(serializers.ModelSerializer):
    total_questions = serializers.SerializerMethodField()
    class Meta:
        model = AssessmentTemplate
        fields = '__all__'
    def get_total_questions(self, obj):
        return obj.template_questions.count()

