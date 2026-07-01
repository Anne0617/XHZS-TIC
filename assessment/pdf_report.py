from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def _register_font():
    """Register CJK fonts for PDF generation"""
    import os
    font_paths = [
        r"C:\Windows\Fonts\msyh.ttc",      # Microsoft YaHei
        r"C:\Windows\Fonts\simhei.ttf",     # SimHei
        r"C:\Windows\Fonts\simsun.ttc",     # SimSun
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont('CJK', path))
                return 'CJK'
            except:
                continue
    return _try_cid_font()


def _try_cid_font():
    try:
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
        return 'STSong-Light'
    except:
        from reportlab.pdfbase import pdfmetrics as pm
        return 'Helvetica'


def generate_pdf_report(result):
    """Generate a PDF report from an AssessmentResult"""
    font_name = _register_font()

    emp = result.assignment.employee
    task = result.assignment.task
    dims = result.dimension_scores if result.dimension_scores else {}
    risk_map = {"low": "\u5065\u5eb7", "medium": "\u6709\u98ce\u9669", "high": "\u6709\u98ce\u9669"}
    risk_text = risk_map.get(result.risk_level, result.risk_level)

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            topMargin=2*cm, bottomMargin=2*cm,
                            leftMargin=2*cm, rightMargin=2*cm)

    styles = getSampleStyleSheet()
    style_title = ParagraphStyle('Title', parent=styles['Title'],
                                  fontName=font_name, fontSize=22, spaceAfter=6*mm,
                                  textColor=colors.HexColor('#0A1628'))
    style_h2 = ParagraphStyle('H2', parent=styles['Heading2'],
                               fontName=font_name, fontSize=14, spaceBefore=6*mm, spaceAfter=4*mm,
                               textColor=colors.HexColor('#0A1628'))
    style_body = ParagraphStyle('Body', parent=styles['Normal'],
                                 fontName=font_name, fontSize=10, leading=16,
                                 spaceAfter=2*mm)
    style_label = ParagraphStyle('Label', parent=styles['Normal'],
                                  fontName=font_name, fontSize=10, leading=16,
                                  textColor=colors.HexColor('#666666'))
    style_value = ParagraphStyle('Value', parent=styles['Normal'],
                                  fontName=font_name, fontSize=11, leading=16,
                                  textColor=colors.HexColor('#0A1628'))

    elements = []

    # Title
    elements.append(Paragraph(f"{emp.name} - \u6d4b\u8bc4\u62a5\u544a", style_title))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1565c0')))
    elements.append(Spacer(1, 4*mm))

    # Info block
    info_data = [
        ["\u59d3\u540d", emp.name, "\u4efb\u52a1", task.name if task else ''],
        ["\u65f6\u95f4", result.generated_at.strftime('%Y-%m-%d %H:%M') if result.generated_at else '',
         "\u72b6\u6001", "\u5df2\u5b8c\u6210"],
    ]
    info_table = Table(info_data, colWidths=[3*cm, 5*cm, 3*cm, 5.5*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#666666')),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (3, 0), (3, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 8*mm))

    # Score summary
    elements.append(Paragraph("\u6d4b\u8bc4\u7ed3\u679c\u6982\u89c8", style_h2))

    score_table_data = [
        [Paragraph("\u7efc\u5408\u5f97\u5206", style_label),
         Paragraph(f"{result.score_percent:.1f}%", style_value)],
        [Paragraph("\u5c97\u4f4d\u9002\u914d\u5ea6", style_label),
         Paragraph(f"{result.fit_score:.1f}", style_value)],
        [Paragraph("\u98ce\u9669\u7b49\u7ea7", style_label),
         Paragraph(risk_text, ParagraphStyle('RiskValue', parent=style_value,
                   textColor=colors.HexColor('#C62828') if result.risk_level in ('medium','high') else colors.HexColor('#2E7D32'), fontName=font_name))],
    ]
    score_table = Table(score_table_data, colWidths=[4*cm, 4*cm])
    score_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0E0E0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0E0E0')),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F7FA')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 8*mm))

    # Dimension scores table
    if dims:
        elements.append(Paragraph("\u7ef4\u5ea6\u5f97\u5206", style_h2))
        dim_headers = ["\u7ef4\u5ea6", "\u5f97\u5206", "\u6ee1\u5206", "\u5f97\u5206\u7387", "\u7b49\u7ea7"]
        dim_rows = [dim_headers]
        for code, d in dims.items():
            dim_rows.append([
                d.get("name", code),
                f"{d.get('score', 0):.1f}",
                f"{d.get('max', 0):.1f}",
                f"{d.get('percent', 0):.1f}%",
                d.get("level", "")
            ])
        dim_table = Table(dim_rows, colWidths=[4*cm, 2.5*cm, 2.5*cm, 2.5*cm, 3.5*cm])
        dim_style = [
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (-1, 0), font_name),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0A1628')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0E0E0')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]
        # Alternate row colors
        for i in range(1, len(dim_rows)):
            if i % 2 == 0:
                dim_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F5F7FA')))
        dim_table.setStyle(TableStyle(dim_style))
        elements.append(dim_table)

    # Warning for abnormal results
    if result.is_abnormal:
        elements.append(Spacer(1, 6*mm))
        warn_text = f"\u6ce8\u610f\uff1a\u8be5\u6d4b\u8bc4\u5f02\u5e38 ({result.abnormal_reason})"
        elements.append(Paragraph(warn_text, ParagraphStyle('Warn', parent=style_body,
                          textColor=colors.HexColor('#C62828'), fontName=font_name)))

    # Footer
    elements.append(Spacer(1, 2*cm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#E0E0E0')))
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph(f"\u751f\u6210\u65f6\u95f4: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                              ParagraphStyle('Footer', parent=style_body, fontSize=8,
                                            textColor=colors.HexColor('#999999'), fontName=font_name)))

    doc.build(elements)
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes


# Alias for backwards compatibility
generate_report_pdf = generate_pdf_report
