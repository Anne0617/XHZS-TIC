import sys

def update_views_api():
    path = "assessment/views_api.py"
    with open(path, encoding="utf-8") as f:
        content = f.read()
    
    # Find a good insertion point - before the import_from_json function
    marker = "def import_from_json"
    pos = content.find(marker)
    if pos == -1:
        print("ERROR: import_from_json not found")
        return False
    
    # Go back to find the previous decorator line
    new_func = '''

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_report_ppt(request, pk):
    from .models import AssessmentResult
    from django.shortcuts import get_object_or_404
    result = get_object_or_404(AssessmentResult, pk=pk)
    user = request.user
    if user.is_hr_admin and user.branch:
        if result.assignment.employee.branch_id != user.branch_id:
            return Response({'error': '\u65e0\u6743\u8bbf\u95ee'}, status=status.HTTP_403_FORBIDDEN)
    try:
        from .ppt_report import generate_report_ppt
        pptx_bytes = generate_report_ppt(result)
        from django.http import HttpResponse
        emp_name = result.assignment.employee.name
        response = HttpResponse(pptx_bytes, content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation')
        response['Content-Disposition'] = 'attachment; filename=TIC_Report_' + emp_name + '_' + result.generated_at.strftime('%Y%m%d') + '.pptx'
        return response
    except Exception as e:
        return Response({'error': 'PPT\u751f\u6210\u5931\u8d25: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

'''
    
    content = content[:pos] + new_func + "\n\n" + content[pos:]
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated views_api.py OK")
    return True


def update_urls_api():
    path = "assessment/urls_api.py"
    with open(path, encoding="utf-8") as f:
        content = f.read()
    
    old = "path('import-pdp-mbti/', import_tools.import_from_json, name='api_import_pdp_mbti'),"
    new = "path('import-pdp-mbti/', import_tools.import_from_json, name='api_import_pdp_mbti'),\n    path('results/<int:pk>/ppt/', views_api.download_report_ppt, name='api_report_ppt'),"
    
    if old in content:
        content = content.replace(old, new)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Updated urls_api.py OK")
        return True
    print("ERROR: import-pdp-mbti route not found")
    return False


if __name__ == "__main__":
    ok = True
    ok &= update_views_api()
    ok &= update_urls_api()
    print("Done" if ok else "FAILED")
