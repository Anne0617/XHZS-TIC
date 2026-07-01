"""Import exam questions from survey data file to the database.
Run after seed_data to populate the 4 exam templates with questions.
Usage: python manage.py import_exam_questions
"""
import os, re, sys
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

class Command(BaseCommand):
    help = "Import questions for the 4 exam templates from survey data file"

    def handle(self, *args, **options):
        import django
        from assessment.models import (QuestionCategory, Question, QuestionOption, AssessmentTemplate, TemplateQuestion)

        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
        html_path = os.path.join(data_dir, "survey_questions.html")
        
        if not os.path.exists(html_path):
            self.stdout.write(self.style.WARNING(f"Survey file not found: {html_path}"))
            self.stdout.write(self.style.WARNING("Skipping exam question import"))
            return
        
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        panels = content.split('<div class="tab-panel')
        
        def clean(t):
            return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", t)).replace("\u00a0", " ").strip()
        
        def get_cat(name, code, so):
            c, _ = QuestionCategory.objects.get_or_create(code=code, defaults={"name": name, "sort_order": so, "is_active": True})
            return c
        
        def make_q(text, cat, qtype, so):
            if Question.objects.filter(text=text, category=cat).exists():
                return Question.objects.get(text=text, category=cat)
            return Question.objects.create(text=text, category=cat, question_type=qtype, score=5, weight=1.0, sort_order=so, is_active=True, review_status="approved")
        
        L5 = [("1","非常不符合",1),("2","比较不符合",2),("3","一般",3),("4","比较符合",4),("5","非常符合",5)]
        B5 = [("1","非常不同意",1),("2","不同意",2),("3","中立",3),("4","同意",4),("5","非常同意",5)]
        
        exam_configs = [
            (1, "comprehensive", L5, "comp_"),
            (2, "bigfive", B5, "big_"),
        ]
        
        total = 0
        
        for panel_idx, exam_type, opts, cat_prefix in exam_configs:
            tpl = AssessmentTemplate.objects.get(exam_type=exam_type)
            TemplateQuestion.objects.filter(template=tpl).delete()
            panel = panels[panel_idx]
            dim_blocks = re.split(r'<div class="q-title[^"]*"[^>]*>', panel)[1:]
            so = 0
            for di, block in enumerate(dim_blocks):
                name = clean(block.split("</div>")[0])
                name = re.sub(r"\s*\(.*?\)", "", name).strip()
                if exam_type == "bigfive":
                    name = re.sub(r"\s*—.*$", "", name).strip()
                cat = get_cat(name, f"{cat_prefix}{di}", di)
                for item in re.findall(r'<div class="q-item[^"]*">(.*?)(?=</div>\s*</div>)', block, re.DOTALL):
                    t = clean(item)
                    t = re.sub(r"^\d+\.\s*", "", t).strip()
                    t = re.sub(r"\d+\s*完全\S+\s*\d+\s*完全\S+\s*$", "", t).strip()
                    t = re.sub(r"\d+\s*非常\S+\s*\d+\s*非常\S+\s*$", "", t).strip()
                    if not t: continue
                    q = make_q(t, cat, "likert5", so)
                    if not QuestionOption.objects.filter(question=q).exists():
                        for l, txt, s in opts:
                            QuestionOption.objects.create(question=q, label=l, text=txt, score=s, sort_order=int(l))
                    TemplateQuestion.objects.get_or_create(template=tpl, question=q, defaults={"weight":1,"sort_order":so})
                    so += 1
            total += so
            self.stdout.write(f"{tpl.name}: {so} questions")
        
        # PDP (fixed: separate pdp-q divs with animal labels)
        ANIMALS = {"tiger":"老虎","peacock":"孔雀","koala":"考拉","owl":"猫头鹰"}
        tpl = AssessmentTemplate.objects.get(exam_type="pdp")
        TemplateQuestion.objects.filter(template=tpl).delete()
        cat, _ = QuestionCategory.objects.get_or_create(code="pdp", defaults={"name":"PDP行为风格","sort_order":0,"is_active":True})
        q_divs = re.findall(r'<div class="pdp-q[^"]*">(.*?)</div>', panels[3], re.DOTALL)
        so = 0
        for q_html in q_divs:
            spans = re.findall(r'<span[^>]*class="[^"]*pdp-opt\s+(\w+)-opt"[^>]*>(.*?)</span>', q_html, re.DOTALL)
            if len(spans) != 4: continue
            texts = [s[1] for s in spans]
            q_text = " / ".join(texts)
            q, created = Question.objects.get_or_create(text=q_text, category=cat, defaults={"question_type":"single","score":4,"weight":1.0,"sort_order":so,"is_active":True,"review_status":"approved"})
            if created:
                for oi,(at,adj) in enumerate(spans):
                    QuestionOption.objects.create(question=q, label=chr(65+oi), text=f"{ANIMALS.get(at,at)}：{adj}", score=oi+1, sort_order=oi)
            TemplateQuestion.objects.get_or_create(template=tpl, question=q, defaults={"weight":1,"sort_order":so})
            so += 1
        total += so
        self.stdout.write(f"{tpl.name}: {so} questions")
        
                # MBTI (fixed: individual mbti-q divs via findall)
        tpl = AssessmentTemplate.objects.get(exam_type="mbti")
        TemplateQuestion.objects.filter(template=tpl).delete()
        cat = get_cat("人格维度", "mbti", 0)
        so = 0
        for q_block in re.findall(r'<div class="mbti-q[^"]*">(.*?)</div>', panels[4], re.DOTALL):
            t = clean(q_block)
            t = re.sub(r"^M\d+\.\s*", "", t).strip()
            if not t: continue
            parts = re.split(r"[AB]\.\s*", t)
            q_text = parts[0].strip() if parts else t
            choices = parts[1:] if len(parts) > 1 else ["是","否"]
            q = make_q(q_text, cat, "single", so)
            if not QuestionOption.objects.filter(question=q).exists():
                for oi, c in enumerate(choices):
                    QuestionOption.objects.create(question=q, label=chr(65+oi), text=c.strip(), score=oi, sort_order=oi)
            TemplateQuestion.objects.get_or_create(template=tpl, question=q, defaults={"weight":1,"sort_order":so})
            so += 1
        total += so
        self.stdout.write(f"{tpl.name}: {so} questions")
        self.stdout.write(self.style.SUCCESS(f"\nTotal: {total} questions imported"))

