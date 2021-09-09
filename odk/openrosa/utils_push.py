from django.http import HttpResponse, StreamingHttpResponse
from datetime import datetime



def response_with_mimetype_and_name(mimetype,
                                    name,
                                    extension=None,
                                    show_date=True,
                                    file_path=None,
                                    use_local_filesystem=False,
                                    full_mime=False):
    if extension is None:
        extension = mimetype
    if not full_mime:
        mimetype = "application/%s" % mimetype
    if file_path:
        try:
            if not use_local_filesystem:
                default_storage = get_storage_class()()
                wrapper = FileWrapper(default_storage.open(file_path))
                response = StreamingHttpResponse(
                    wrapper, content_type=mimetype)
                response['Content-Length'] = default_storage.size(file_path)
            else:
                wrapper = FileWrapper(open(file_path))
                response = StreamingHttpResponse(
                    wrapper, content_type=mimetype)
                response['Content-Length'] = os.path.getsize(file_path)
        except IOError:
            response = HttpResponseNotFound(
                "The requested file could not be found.")
    else:
        response = HttpResponse(content_type=mimetype)
    response['Content-Disposition'] = generate_content_disposition_header(
        name, extension, show_date)
    return response


def generate_content_disposition_header(name, extension, show_date=True):
    if name is None:
        return 'attachment;'
    if show_date:
        name = "%s-%s" % (name, datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    return 'attachment; filename=%s.%s' % (name, extension)
