from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_from_json(request):
    user = request.user
    if not user.is_super_admin:
        return Response({'error': chr(20165) + chr(36229) + chr(31649) + chr(21487) + chr(23548) + chr(20837)}, status=status.HTTP_403_FORBIDDEN)
    import_data = request.data
    if not import_data:
        return Response({'error': 'no data'}, status=status.HTTP_400_BAD_REQUEST)
    from .models import QuestionCategory, Question, QuestionOption
    created_cats = []
    created_qs = []
    for section in import_data:
        cat_name = section['category']
        qtype = section.get('question_type', 'likert5')
        cat_code = cat_name.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_').replace('-', '_')[:30]
        cat, _ = QuestionCategory.objects.get_or_create(code=cat_code, defaults={'name': cat_name, 'sort_order': 100})
        QuestionCategory.objects.filter(pk=cat.pk).update(name=cat_name)
        created_cats.append(cat_name)
        for item in section['questions']:
            text = item.get('text', '')
            opts = item.get('options', [])
            q, q_new = Question.objects.get_or_create(text=text, category=cat, defaults={'question_type': qtype, 'score': 5, 'weight': 1.0, 'review_status': 'approved', 'is_reversed': False, 'created_by': user})
            if q_new:
                for idx, opt_text in enumerate(opts):
                    QuestionOption.objects.create(question=q, label=str(idx + 1), text=opt_text, score=idx + 1, sort_order=idx + 1)
                created_qs.append(text[:30])
    return Response({'categories_created': len(created_cats), 'questions_created': len(created_qs)})



import os
import re
import tempfile

from django.db import transaction

from .models import QuestionCategory, Question, QuestionOption, AssessmentTemplate, TemplateQuestion


LIKERT5_OPTIONS = [
    ("1", "完全不符合", 1),
    ("2", "基本符合", 2),
    ("3", "一般", 3),
    ("4", "比较符合", 4),
    ("5", "完全符合", 5),
]


def import_questions_from_docx(docx_path, template=None, request_user=None, replace_existing=True):
    """
    从 docx 问卷文件导入题目到数据库。

    参数:
        docx_path: .docx 文件路径
        template: AssessmentTemplate 实例（可选），导入后自动关联题目
        request_user: User 实例（可选），作为创建人
        replace_existing: 如果 template 已有题目，是否先清空再导入

    返回:
        dict: { 'categories': [名称列表], 'questions': [题目文本列表], 'errors': [错误信息] }
    """
    from docx import Document

    doc = Document(docx_path)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    results = {
        'categories': [],
        'questions': [],
        'errors': [],
    }

    # --- 解析段落 ---
    module_pattern = re.compile(r'模块[一二三四五六七八九十]+[：:]\s*(.+)')
    question_pattern = re.compile(r'^(\d+)[.、]\s*(.+)')

    modules = []  # [(module_name, [(question_text, sort_order)])]
    current_module = None
    sort_counter = 0

    # 需要在模块解析前过滤掉的行关键词
    skip_keywords = ['评分标准', '答题说明', '姓名', '部门', '岗位', '填写日期',
                     '星河智善', '内部员工', '机密文件', '━━━']

    for line in paragraphs:
        # 跳过标题/说明行（但如果匹配题目或模块则保留）
        if any(kw in line for kw in skip_keywords):
            if not question_pattern.match(line) and not module_pattern.match(line):
                continue

        # 匹配模块头
        m = module_pattern.match(line)
        if m:
            if current_module is not None:
                modules.append(current_module)
            module_name = m.group(1).strip()
            module_name = re.sub(r'[（(]第\d+.*?[)）]', '', module_name).strip()
            current_module = {'name': module_name, 'questions': []}
            continue

        # 匹配题目行（跳过选项行）
        m = question_pattern.match(line)
        if m:
            if current_module is None:
                current_module = {'name': '默认维度', 'questions': []}
            question_text = m.group(2).strip()
            # 去掉行尾附带的量表数字
            question_text = re.sub(
                r'\d+\s*\S+\s*\d+\s*\S+\s*\d+\s*\S+.*$', '', question_text
            ).strip()
            current_module['questions'].append((question_text, sort_counter))
            sort_counter += 1
            continue

    if current_module is not None:
        modules.append(current_module)

    if not modules:
        results['errors'].append('未能解析出任何模块和题目，请检查文档格式。')
        return results

    # --- 写入数据库 ---
    with transaction.atomic():
        if template and replace_existing:
            template.template_questions.all().delete()

        for mi, module in enumerate(modules):
            name = module['name']
            # 生成唯一的 code
            code = 'docx_' + re.sub(r'\s+', '_', name)[:30]
            cat, created = QuestionCategory.objects.get_or_create(
                code=code,
                defaults={'name': name, 'sort_order': mi, 'is_active': True},
            )
            if not created:
                QuestionCategory.objects.filter(pk=cat.pk).update(name=name)
            results['categories'].append(name)

            for q_text, so in module['questions']:
                if not q_text:
                    continue

                existing = Question.objects.filter(text=q_text, category=cat).first()
                if existing:
                    q = existing
                else:
                    q = Question.objects.create(
                        question_type='likert5',
                        category=cat,
                        text=q_text,
                        score=5,
                        weight=1.0,
                        sort_order=so,
                        is_active=True,
                        review_status='approved',
                        created_by=request_user,
                    )
                    for label, opt_text, score in LIKERT5_OPTIONS:
                        QuestionOption.objects.create(
                            question=q,
                            label=label,
                            text=opt_text,
                            score=score,
                            sort_order=int(label),
                        )
                    results['questions'].append(q_text[:50])

                # 关联到模板
                if template:
                    TemplateQuestion.objects.get_or_create(
                        template=template,
                        question=q,
                        defaults={'weight': 1.0, 'sort_order': so},
                    )

    return results


def process_uploaded_docx(uploaded_file, template=None, request_user=None, replace_existing=True):
    """
    处理上传的 .docx 文件并导入题目。

    uploaded_file: UploadedFile 对象（来自 request.FILES）
    返回同 import_questions_from_docx。
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
        for chunk in uploaded_file.chunks():
            tmp.write(chunk)
        tmp_path = tmp.name

    try:
        result = import_questions_from_docx(
            tmp_path, template, request_user, replace_existing
        )
    finally:
        os.unlink(tmp_path)

    return result

