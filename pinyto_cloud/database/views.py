from django.http import HttpResponse
from project_path import project_path


def home(request):
    with open(project_path("static/index.html"), 'r') as index_html_file:
        return HttpResponse(index_html_file.read(), mimetype='text/html')


def store(request):
    """
    Store document in any format. The date of creation and request.user will be
    added automatically to the document

    :param request:
    """
    pass