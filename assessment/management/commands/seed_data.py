"""
种子数据脚本
运行: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.hashers import make_password
from accounts.models import Branch, User
from assessment.models import (
    QuestionCategory, Question, QuestionOption,
    AssessmentTemplate, TemplateQuestion, SystemConfig,
)


class Command(BaseCommand):
    help = "初始化系统种子数据"

    def handle(self, *args, **options):
        self.stdout.write("开始初始化种子数据...")
        
        # 1. 创建分公司
        branches_data = [
            ("广州分公司", "GZ", 0),
            ("粤东分公司", "YD", 1),
            ("深圳分公司", "SZ", 2),
            ("华东分公司", "HD", 3),
            ("天津分公司", "TJ", 4),
            ("成都分公司", "CD", 5),
        ]
        branches = {}
        for name, code, sort in branches_data:
            branch, _ = Branch.objects.get_or_create(
                code=code,
                defaults={"name": name, "sort_order": sort, "is_active": True}
            )
            branches[code] = branch
            self.stdout.write(f"   分公司: {name}")
        
        # 2. 创建超管
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin", password="admin123",
                email="admin@company.com",
                role=User.Role.SUPER_ADMIN,
                first_name="系统", last_name="管理员",
            )
            self.stdout.write("   超管: admin / admin123")
        
        # 3. 创建各分公司HR管理员
        hr_accounts = [
            ("gz_hr", "广州HR", "GZ"), ("yd_hr", "粤东HR", "YD"),
            ("sz_hr", "深圳HR", "SZ"), ("hd_hr", "华东HR", "HD"),
            ("tj_hr", "天津HR", "TJ"), ("cd_hr", "成都HR", "CD"),
        ]
        hr_phones = {'GZ':'13800138001','YD':'13800138002','SZ':'13800138003','HD':'13800138004','TJ':'13800138005','CD':'13800138006'}
        for username, fullname, bc in hr_accounts:
            if not User.objects.filter(username=username).exists():
                User.objects.create(
                    username=username, password=make_password("hr123456"),
                    role=User.Role.HR_ADMIN, branch=branches[bc],
                    first_name=fullname, department="人力资源部",
                    phone=hr_phones.get(bc, ""),
                    can_manage_questions=True, can_manage_tasks=True,
                    can_view_data=True, can_export_data=True,
                    can_manage_employees=True, is_active=True,
                )
            self.stdout.write(f"   HR: {username} / hr123456 ({fullname})")
        
        # 4. 创建题目分类
        cats_data = [
            ("心理健康", "mental_health", 0),
            ("抗压能力", "stress_resistance", 1),
            ("职业稳定性", "career_stability", 2),
            ("人格特质", "personality", 3),
            ("情绪管理", "emotion_management", 4),
            ("团队适配度", "team_fit", 5),
            ("职场风险倾向", "workplace_risk", 6),
        ]
        categories = {}
        for name, code, sort in cats_data:
            cat, _ = QuestionCategory.objects.get_or_create(
                code=code, defaults={"name": name, "sort_order": sort}
            )
            categories[code] = cat
            self.stdout.write(f"   维度: {name}")
        
        # 5. 创建题目
        questions_data = [
            ("mental_health", "我最近感到心情愉快，生活充满乐趣", False),
            ("mental_health", "我经常无缘无故感到紧张或焦虑", True),
            ("mental_health", "我对未来持乐观态度", False),
            ("mental_health", "我经常感到疲惫不堪，即使休息后也难以恢复", True),
            ("mental_health", "我能够专注于当前的工作和生活", False),
            ("stress_resistance", "面对紧迫的工作任务，我能保持冷静", False),
            ("stress_resistance", "工作中遇到挫折时，我容易产生放弃的念头", True),
            ("stress_resistance", "我能在压力环境下保持较高的工作效率", False),
            ("stress_resistance", "即使工作量大，我也能合理安排时间和精力", False),
            ("stress_resistance", "我经常因为工作压力而影响睡眠质量", True),
            ("career_stability", "我愿意在当前行业长期发展", False),
            ("career_stability", "如果有更好的薪资待遇，我会毫不犹豫地跳槽", True),
            ("career_stability", "我有清晰的职业发展规划", False),
            ("career_stability", "过去三年内我更换工作的频率较低", False),
            ("career_stability", "我认为忠诚度是职场中非常重要的品质", False),
            ("personality", "我喜欢与人交往，乐于结识新朋友", False),
            ("personality", "我做事有条理，喜欢提前规划", False),
            ("personality", "我容易接受新事物和新变化", False),
            ("personality", "在工作中我倾向于遵循既定的规则和流程", False),
            ("personality", "我常常能注意到细节和潜在问题", False),
            ("emotion_management", "我能清楚识别自己当下的情绪状态", False),
            ("emotion_management", "情绪波动时，我常常做出事后后悔的决定", True),
            ("emotion_management", "即使心情不好，我也不会影响工作表现", False),
            ("emotion_management", "我能理性看待他人的批评意见", False),
            ("emotion_management", "我经常因为小事而情绪失控", True),
            ("team_fit", "我喜欢在团队中与他人协作完成任务", False),
            ("team_fit", "团队中出现分歧时，我能主动沟通协调", False),
            ("team_fit", "我倾向于独立工作，不喜欢被他人干扰", True),
            ("team_fit", "我愿意主动帮助遇到困难的同事", False),
            ("team_fit", "我能够尊重团队中不同的观点和意见", False),
            ("workplace_risk", "我认为只要能达到目的，适当违反规则是可以接受的", True),
            ("workplace_risk", "我能够严格遵守公司的各项规章制度", False),
            ("workplace_risk", "如果对工作不满，我可能会采取消极对抗的方式", True),
            ("workplace_risk", "我认同诚实守信是职场中最重要的原则", False),
            ("workplace_risk", "我有时会为了个人利益而牺牲团队利益", True),
        ]
        
        admin_user = User.objects.filter(username="admin").first()
        likert5_opts = [
            ("1", "非常不符合", 1), ("2", "比较不符合", 2),
            ("3", "一般", 3), ("4", "比较符合", 4), ("5", "非常符合", 5),
        ]
        
        q_objects = []
        for cat_code, text, is_rev in questions_data:
            cat = categories[cat_code]
            q, created = Question.objects.get_or_create(
                text=text, category=cat,
                defaults={
                    "question_type": "likert5", "is_reversed": is_rev,
                    "score": 5, "weight": 1.0, "created_by": admin_user,
                    "review_status": "approved",
                }
            )
            if created:
                for label, txt, score in likert5_opts:
                    QuestionOption.objects.create(
                        question=q, label=label, text=txt,
                        score=score, sort_order=int(label)
                    )
                q_objects.append(q)
        
        self.stdout.write(f"   共 {len(q_objects)} 道题目")
        
        # 6. 创建测评模板
        tpl, created = AssessmentTemplate.objects.get_or_create(
            name="通用入职人才测评",
            defaults={
                "description": "适用于所有岗位的标准化入职心理评估",
                "target_position": "通用", "estimated_minutes": 20,
                "created_by": admin_user,
            }
        )
        if created:
            for idx, q in enumerate(q_objects):
                TemplateQuestion.objects.create(
                    template=tpl, question=q, weight=1.0, sort_order=idx
                )
            self.stdout.write(f"   模板: 通用入职人才测评（{len(q_objects)} 道题）")
        
        for name, desc, pos, minutes in [
            # ("销售岗专项测评", ... 已删除),
            # ("技术岗专项测评", ... 已删除),
            # ("管理岗专项测评", ... 已删除),
        ]:
            AssessmentTemplate.objects.get_or_create(
                name=name,
                defaults={
                    "description": desc, "target_position": pos,
                    "estimated_minutes": minutes, "created_by": admin_user,
                }
            )
            self.stdout.write(f"   模板: {name}")
        
        # 8. 创建公开考试模板（统一公共入口）
        exam_templates = [
            ("人才综合评估", "comprehensive", "综合评估候选人各项心理素质与岗位匹配度"),
            ("大五人格BigFive", "bigfive", "基于大五人格模型评估候选人性格特质"),
            ("PDP性格测试", "pdp", "PDP行为风格测试，评估候选人的行为特质与沟通风格"),
            ("MBTI人格测试", "mbti", "MBTI职业人格测试，评估候选人的性格类型与职业倾向"),
        ]
        for name, etype, desc in exam_templates:
            AssessmentTemplate.objects.get_or_create(
                exam_type=etype,
                defaults={
                    "name": name, "description": desc,
                    "target_position": "通用", "estimated_minutes": 15,
                    "created_by": admin_user, "is_active": True,
                }
            )
            self.stdout.write(f"   考试模板: {name}（{etype}）")
        
        # 7. 系统配置
        for key, value, desc in [
            ("system_name", "智善TIC人才测评体系", "系统名称"),
            ("default_duration", "30", "默认作答时长(分钟)"),
            ("default_valid_days", "7", "默认有效期(天)"),
            ("min_password_length", "8", "密码最小长度"),
            ("copyright_info", "\u00a9 2026 企业人力资源部", "版权信息"),
        ]:
            SystemConfig.objects.get_or_create(
                key=key, defaults={"value": value, "description": desc}
            )
        
        self.stdout.write(self.style.SUCCESS("\n 种子数据初始化完成！"))

