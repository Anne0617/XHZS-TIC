# -*- coding: utf-8 -*-
import json
from decimal import Decimal
from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.db.models import Q

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from assessment.models import (
    Employee, AssessmentTemplate, TemplateQuestion,
    AssessmentTask, TaskAssignment, AssessmentSession,
    Answer, AssessmentResult, AssessmentReport,
    Question, QuestionOption,
)
from accounts.models import OperationLog

def _parse_code(code):
    """Parse code - returns (mode, obj)"""
    code = (code or "").strip()
    if not code:
        return None, None
    if code.upper().startswith("TPL"):
        try:
            tpl_id = int(code[3:])
            tpl = AssessmentTemplate.objects.get(pk=tpl_id, is_active=True)
            return "template", tpl
        except (ValueError, AssessmentTemplate.DoesNotExist):
            return None, None
    assign = TaskAssignment.objects.filter(access_code=code).select_related(
        "task__template", "employee"
    ).first()
    if assign:
        return "assignment", assign
    return None, None


def _build_questions_data(template):
    """Build question list from template"""
    tqs = TemplateQuestion.objects.filter(template=template) \
        .select_related("question__category") \
        .order_by("sort_order")
    questions = []
    for tq in tqs:
        q = tq.question
        opts = QuestionOption.objects.filter(question=q).order_by("sort_order")
        questions.append({
            "id": q.id,
            "text": q.text,
            "description": q.description,
            "question_type": q.question_type,
            "category_name": q.category.name,
            "is_reversed": q.is_reversed,
            "sort_order": q.sort_order,
            "options": [
                {"id": o.id, "label": o.label, "text": o.text, "score": float(o.score)}
                for o in opts
            ],
        })
    return questions

@api_view(["GET"])
@permission_classes([AllowAny])
def public_assess_detail(request, code):
    """Get assessment info"""
    mode, obj = _parse_code(code)
    if not mode:
        return Response({"valid": False, "error": "Invalid or expired link"}, status=404)

    if mode == "assignment":
        assign = obj
        task = assign.task
        tpl = task.template
        now = timezone.now()
        if task.valid_until and task.valid_until < now:
            assign.status = "expired"
            assign.save()
            return Response({"valid": False, "error": "Assessment expired"}, status=410)

        employee_info = {
            "name": assign.employee.name,
            "phone": assign.employee.phone,
            "email": assign.employee.email,
        }
        task_info = {
            "id": task.id,
            "name": task.name,
            "template_name": tpl.name,
            "duration_minutes": task.duration_minutes,
            "valid_from": task.valid_from.isoformat() if task.valid_from else None,
            "valid_until": task.valid_until.isoformat() if task.valid_until else None,
        }
        questions = _build_questions_data(tpl)
        return Response({
            "valid": True, "mode": "assignment",
            "task": task_info, "employee": employee_info,
            "questions": questions, "total_questions": len(questions),
        })

    tpl = obj
    task_info = {
        "id": tpl.id, "name": tpl.name, "template_name": tpl.name,
        "description": tpl.description,
        "duration_minutes": tpl.estimated_minutes or 30,
        "estimated_minutes": tpl.estimated_minutes,
        "total_questions": tpl.total_questions,
    }
    questions = _build_questions_data(tpl)
    return Response({
        "valid": True, "mode": "template",
        "task": task_info, "employee": None,
        "questions": questions, "total_questions": len(questions),
    })


@api_view(["POST"])
@permission_classes([AllowAny])
def public_assess_start(request, code):
    """Start assessment - create/confirm Employee + Task + Assignment + Session"""
    mode, obj = _parse_code(code)
    if not mode:
        return Response({"error": "Invalid link"}, status=404)

    name = request.data.get("name", "").strip()
    phone = request.data.get("phone", "").strip()
    position = request.data.get("position", "").strip()
    email = request.data.get("email", "").strip()
    if not name:
        return Response({"error": "请填写姓名"}, status=400)
    if not phone:
        return Response({"error": "请填写手机号"}, status=400)

    now = timezone.now()

    if mode == "assignment":
        assign = obj
        emp = assign.employee
        emp.name = name
        emp.phone = phone
        if email:
            emp.email = email
        emp.save()
        session = AssessmentSession.objects.filter(assignment=assign, end_time__isnull=True).first()
        if session:
            return Response({"session_id": session.id})
        session = AssessmentSession.objects.create(assignment=assign)
        assign.status = "in_progress"
        assign.save()
        return Response({"session_id": session.id})

    tpl = obj
    with transaction.atomic():
        # check phone dedup
        existing_emp = Employee.objects.filter(phone=phone).first()
        if existing_emp:
            finished = TaskAssignment.objects.filter(employee=existing_emp, status='completed').exists()
            if finished:
                return Response({"error": "该手机号已完成测评，请勿重复提交"}, status=400)
            # 存在但未完成: 复用该员工，更新信息
            emp = existing_emp
            emp.name = name
            if position:
                emp.position = position
            if email:
                emp.email = email
            emp.save()
        else:
            emp = Employee.objects.create(
                name=name, phone=phone, email=email or "",
                department="", position=position, status="pending",
            )
        # inherit branch/project from template creator# inherit branch/project from template creator
        if tpl.created_by:
            changed = False
            if tpl.created_by.branch and not emp.branch:
                emp.branch = tpl.created_by.branch
                changed = True
            if tpl.created_by.project and not emp.project:
                emp.project = tpl.created_by.project
                changed = True
            if changed:
                emp.save(update_fields=['branch', 'project'])
        access_code = "EX" + now.strftime("%m%d") + str(emp.id).zfill(4)
        task = AssessmentTask.objects.create(
            name=f"{tpl.name} - {name}", template=tpl, status="in_progress",
            valid_from=now, valid_until=now + timedelta(days=7),
            duration_minutes=tpl.estimated_minutes or 30, created_by=None,
        )
        assign = TaskAssignment.objects.create(
            task=task, employee=emp, access_code=access_code, status="in_progress",
        )
        session = AssessmentSession.objects.create(assignment=assign)
    return Response({"session_id": session.id, "access_code": access_code})

@api_view(["POST"])
@permission_classes([AllowAny])
def public_assess_submit(request, code):
    """Submit assessment answers"""
    mode, obj = _parse_code(code)
    if not mode:
        return Response({"error": "Invalid link"}, status=404)

    if mode == "assignment":
        assign = obj
    else:
        session_id = request.data.get("session_id")
        if not session_id:
            return Response({"error": "Missing session"}, status=400)
        session = AssessmentSession.objects.filter(pk=session_id).first()
        if not session:
            return Response({"error": "Session not found"}, status=404)
        assign = session.assignment

    session = AssessmentSession.objects.filter(assignment=assign, end_time__isnull=True).first()
    if not session:
        return Response({"error": "Session error, please restart"}, status=400)

    answers_data = request.data.get("answers", [])
    if not answers_data:
        return Response({"error": "Please answer at least one question"}, status=400)

    with transaction.atomic():
        total_score = Decimal("0")
        max_score = Decimal("0")
        dimension_scores = {}

        for item in answers_data:
            q_id = item.get("question_id")
            value = item.get("value", "")
            question = get_object_or_404(Question, pk=q_id)
            score = Decimal("0")

            if question.question_type in ("likert5", "likert7"):
                try:
                    score = Decimal(str(value))
                except Exception:
                    score = Decimal("0")
                if question.is_reversed:
                    max_val = 5 if question.question_type == "likert5" else 7
                    score = Decimal(max_val + 1) - score
            else:
                try:
                    opt_id = int(value)
                    opt = QuestionOption.objects.filter(pk=opt_id).first()
                    if opt:
                        score = opt.score
                except (ValueError, TypeError):
                    if value:
                        avg_score = 0
                        parts = [p.strip() for p in value.split(",") if p.strip()]
                        opts = QuestionOption.objects.filter(question=question, label__in=parts)
                        if opts.exists():
                            avg_score = sum(float(o.score) for o in opts) / len(parts)
                        score = Decimal(str(avg_score))

            Answer.objects.create(session=session, question=question, value=str(value), score=score)

            cat_code = question.category.code
            if cat_code not in dimension_scores:
                dimension_scores[cat_code] = {"name": question.category.name, "score": Decimal("0"), "max": Decimal("0"), "count": 0}
            dimension_scores[cat_code]["score"] += score
            dimension_scores[cat_code]["max"] += question.score
            total_score += score
            max_score += question.score

        score_percent = (total_score / max_score * 100) if max_score > 0 else Decimal("0")

        dimension_result = {}
        risk_tags = []
        for ccode, ds in dimension_scores.items():
            percent = (ds["score"] / ds["max"] * 100) if ds["max"] > 0 else Decimal("0")
            if percent < 40:
                level = "有风险"
                risk_tags.append(ds["name"] + "_low")
            elif percent < 60:
                level = "需关注"
                risk_tags.append(ds["name"] + "_attention")
            else:
                level = "健康"
            dimension_result[ccode] = {"name": ds["name"], "score": float(ds["score"]), "max": float(ds["max"]), "percent": float(percent), "level": level}

        fit_score = float(score_percent)
        if fit_score >= 70:
            risk_level = "low"
        elif fit_score >= 50:
            risk_level = "medium"
        else:
            risk_level = "high"

        duration = int((timezone.now() - session.start_time).total_seconds())
        is_abnormal = duration < 60
        session.end_time = timezone.now()
        session.duration_seconds = duration
        session.is_valid = not is_abnormal
        if is_abnormal:
            session.invalid_reason = "too_short"
        session.save()

        result = AssessmentResult.objects.create(
            session=session, assignment=assign,
            total_score=float(total_score), max_score=float(max_score),
            score_percent=float(score_percent),
            dimension_scores=dimension_result, risk_tags=risk_tags,
            risk_level=risk_level, fit_score=fit_score,
            is_abnormal=is_abnormal, abnormal_reason=session.invalid_reason,
        )

        _generate_report(result)
        assign.status = "completed"
        assign.completed_at = timezone.now()
        assign.save()
        assign.employee.status = "assessed"
        assign.employee.save()
        OperationLog.objects.create(action=f"completed_{assign.employee.name}")

    return Response({"success": True})


def _generate_report(result):
    """Generate simple HTML report"""
    dims = result.dimension_scores
    employee = result.assignment.employee
    task = result.assignment.task
    html_parts = []
    html_parts.append(f"<h2>{employee.name} - Report</h2>")
    html_parts.append(f"<p>Position: {employee.position} | Task: {task.name}</p>")
    html_parts.append(f"<p>Time: {result.generated_at.strftime('%Y-%m-%d %H:%M')}</p>")
    html_parts.append(f"<p><strong>Score%: {result.score_percent:.1f}%</strong></p>")
    html_parts.append(f"<p><strong>Fit: {result.fit_score:.1f}</strong></p>")
    risk_text = {"low": "健康", "medium": "有风险", "high": "有风险"}.get(result.risk_level, result.risk_level)
    html_parts.append(f"<p>风险等级: {risk_text}</p>")
    if result.risk_tags:
        html_parts.append("<p>Items: " + ", ".join(result.risk_tags) + "</p>")
    html_parts.append("<h3>Dimensions</h3><table border='1' cellpadding='6' style='border-collapse:collapse;width:100%;'>")
    html_parts.append("<tr><th>Dimension</th><th>Score</th><th>Max</th><th>%</th><th>Level</th></tr>")
    for code, d in dims.items():
        html_parts.append(f"<tr><td>{d['name']}</td><td>{d['score']:.1f}</td><td>{d['max']:.1f}</td><td>{d['percent']:.1f}%</td><td>{d['level']}</td></tr>")
    html_parts.append("</table>")
    if result.is_abnormal:
        html_parts.append(f"<p style='color:red;'>Abnormal: {result.abnormal_reason}</p>")
    AssessmentReport.objects.create(result=result, html_content="".join(html_parts))

@api_view(["GET"])
@permission_classes([AllowAny])
def public_template_list(request):
    """List active templates for sharing"""
    templates = AssessmentTemplate.objects.filter(is_active=True).order_by("id")
    data = []
    for t in templates:
        data.append({
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "estimated_minutes": t.estimated_minutes,
            "exam_type": t.exam_type,
            "total_questions": t.total_questions,
            "share_code": "TPL" + str(t.id),
            "share_url": "/assess/TPL" + str(t.id) + "/",
        })
    return Response(data)


@api_view(["GET"])
@permission_classes([AllowAny])
def public_qrcode_data(request):
    """Get QR code page data for all shareable templates"""
    from django.conf import settings
    templates = AssessmentTemplate.objects.filter(is_active=True).order_by("id")
    site_url = getattr(settings, "SITE_URL", "https://xhzs-tic-production.up.railway.app")
    items = []
    for t in templates:
        share_code = "TPL" + str(t.id)
        entry_path = "/assess/" + share_code + "/"
        items.append({
            "id": t.id,
            "name": t.name,
            "exam_type": t.exam_type,
            "estimated_minutes": t.estimated_minutes,
            "total_questions": t.total_questions,
            "share_code": share_code,
            "entry_url": entry_path,
            "full_url": site_url + entry_path,
            "qr_url": "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=" + site_url + entry_path,
        })
    return Response({"site_url": site_url, "templates": items})

@api_view(["POST"])
@permission_classes([AllowAny])
def public_assess_result(request, code):
    """Get assessment result by code"""
    mode, obj = _parse_code(code)
    if not mode:
        return Response({"error": "Invalid link"}, status=404)

    if mode == "assignment":
        assign = obj
    else:
        return Response({"error": "Please use your assignment code"}, status=400)

    result = AssessmentResult.objects.filter(assignment=assign).first()
    if not result:
        return Response({"error": "No result found"}, status=404)

    report = AssessmentReport.objects.filter(result=result).first()

    return Response({
        "employee_name": assign.employee.name,
        "task_name": assign.task.name,
        "score_percent": result.score_percent,
        "fit_score": result.fit_score,
        "risk_level": result.risk_level,
        "risk_tags": result.risk_tags,
        "dimension_scores": result.dimension_scores,
        "report_html": report.html_content if report else None,
        "completed_at": assign.completed_at.isoformat() if assign.completed_at else None,
    })
