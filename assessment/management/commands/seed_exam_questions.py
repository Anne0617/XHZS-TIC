import os, re
from django.core.management.base import BaseCommand
class Command(BaseCommand):
    help = "Create questions for the 4 exam templates"
    def handle(self, *args, **options):
        from assessment.models import (QuestionCategory, Question, QuestionOption, AssessmentTemplate, TemplateQuestion)
        L5 = [("1","闈炲父涓嶇鍚?,1),("2","姣旇緝涓嶇鍚?,2),("3","涓€鑸?,3),("4","姣旇緝绗﹀悎",4),("5","闈炲父绗﹀悎",5)]
        B5 = [("1","闈炲父涓嶅悓鎰?,1),("2","涓嶅悓鎰?,2),("3","涓珛",3),("4","鍚屾剰",4),("5","闈炲父鍚屾剰",5)]
        def clean(t):
            return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", t)).replace("\u00a0", " ").strip()
        def get_cat(name, code, so):
            c, _ = QuestionCategory.objects.get_or_create(code=code, defaults={"name": name, "sort_order": so, "is_active": True})
            return c
        def make_q(text, cat, qtype, so):
            q, _ = Question.objects.get_or_create(text=text, category=cat, defaults={"question_type": qtype, "score": 5, "weight": 1.0, "sort_order": so, "is_active": True, "review_status": "approved"})
            return q
        html_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "survey_questions.html")
        total = 0
        if os.path.exists(html_path):
            self.stdout.write("Importing from survey file...")
            with open(html_path, "r", encoding="utf-8") as f:
                content = f.read()
            panels = content.split('<div class="tab-panel')
            if len(panels) < 5:
                self.stdout.write(self.style.WARNING("Only {0} panels found".format(len(panels))))
                return
            for idx, etype, opts in [(1,"comprehensive",L5),(2,"bigfive",B5)]:
                try:
                    tpl = AssessmentTemplate.objects.get(exam_type=etype)
                except AssessmentTemplate.DoesNotExist:
                    continue
                prefix = "comp_" if etype == "comprehensive" else "big_"
                dim_blocks = re.split(r'<div class="q-title[^"]*"[^>]*>', panels[idx])[1:]
                so = 0
                for di, block in enumerate(dim_blocks):
                    nm = clean(block.split("</div>")[0])
                    nm = re.sub(r"\s*\(.*?\)", "", nm).strip()
                    if etype == "bigfive": nm = re.sub(r"\s*[\u2014\-].*$", "", nm).strip()
                    cat = get_cat(nm, prefix + str(di), di)
                    for item in re.findall(r'<div class="q-item[^"]*">(.*?)(?=</div>\s*</div>)', block, re.DOTALL):
                        t = clean(item)
                        t = re.sub(r"^\d+\.\s*", "", t).strip()
                        if not t: continue
                        q = make_q(t, cat, "likert5", so)
                        if not QuestionOption.objects.filter(question=q).exists():
                            for l, txt, s in opts:
                                QuestionOption.objects.create(question=q, label=l, text=txt, score=s, sort_order=int(l))
                        TemplateQuestion.objects.get_or_create(template=tpl, question=q, defaults={"weight":1,"sort_order":so})
                        so += 1
                self.stdout.write("  " + tpl.name + ": " + str(so) + " questions")
                total += so
            try:
                tpl = AssessmentTemplate.objects.get(exam_type="pdp")
                cat, _ = QuestionCategory.objects.get_or_create(code="pdp", defaults={"name":"PDP\u884c\u4e3a\u98ce\u683c","sort_order":0,"is_active":True})
                animals = {"tiger":"\u8001\u864e","peacock":"\u5b54\u96c0","koala":"\u8003\u62c9","owl":"\u732b\u5934\u9e70"}
                q_divs = re.findall(r'<div class="pdp-q[^"]*">(.*?)</div>', panels[3], re.DOTALL)
                so = 0
                for q_html in q_divs:
                    spans = re.findall(r'<span[^>]*class="[^"]*pdp-opt\s+(\w+)-opt"[^>]*>(.*?)</span>', q_html, re.DOTALL)
                    if len(spans) != 4: continue
                    q_text = " / ".join([s[1] for s in spans])
                    q, created = Question.objects.get_or_create(text=q_text, category=cat, defaults={"question_type":"single","score":4,"weight":1.0,"sort_order":so,"is_active":True,"review_status":"approved"})
                    if created:
                        for oi, (at, adj) in enumerate(spans):
                            QuestionOption.objects.create(question=q, label=chr(65+oi), text=animals.get(at,at) + "\uff1a" + adj, score=oi+1, sort_order=oi)
                    TemplateQuestion.objects.get_or_create(template=tpl, question=q, defaults={"weight":1,"sort_order":so})
                    so += 1
                self.stdout.write("  " + tpl.name + ": " + str(so) + " questions")
                total += so
            except AssessmentTemplate.DoesNotExist:
                pass
            try:
                tpl = AssessmentTemplate.objects.get(exam_type="mbti")
                cat = get_cat("\u4eba\u683c\u7ef4\u5ea6", "mbti", 0)
                so = 0
                for q_block in re.findall(r'<div class="mbti-q[^"]*">(.*?)</div>', panels[4], re.DOTALL):
                    t = clean(q_block)
                    t = re.sub(r"^M\d+\.\s*", "", t).strip()
                    if not t: continue
                    parts = re.split(r"[AB]\.\s*", t)
                    q_text = parts[0].strip() if parts else t
                    choices = parts[1:] if len(parts) > 1 else ["\u662f","\u5426"]
                    q = make_q(q_text, cat, "single", so)
                    if not QuestionOption.objects.filter(question=q).exists():
                        for oi, c in enumerate(choices):
                            QuestionOption.objects.create(question=q, label=chr(65+oi), text=c.strip(), score=oi, sort_order=oi)
                    TemplateQuestion.objects.get_or_create(template=tpl, question=q, defaults={"weight":1,"sort_order":so})
                    so += 1
                self.stdout.write("  " + tpl.name + ": " + str(so) + " questions")
                total += so
            except AssessmentTemplate.DoesNotExist:
                pass
            self.stdout.write(self.style.SUCCESS("\nTotal: " + str(total) + " questions imported"))
            return
        self.stdout.write("File not found, creating sample questions...")
        self.stdout.write(self.style.WARNING("Only sample questions created"))
