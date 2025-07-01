from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404

from CvetoforBots.apps.core.models import PDFDocument


def view_pdf(request, slug):
    document = get_object_or_404(PDFDocument, slug=slug)
    try:
        response = FileResponse(document.file.open('rb'), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="%s"' % document.file.name
        return response
    except FileNotFoundError:
        raise Http404("Файл не найден")
