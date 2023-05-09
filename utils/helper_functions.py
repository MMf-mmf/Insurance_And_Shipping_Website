from django.http import HttpResponse
import os
from .email_sender import dev_alert_email

def download_csv_from_cloud(file):
    response = HttpResponse(file.file.read(), content_type="application/force-download")
    response['Content-Disposition'] = 'attachment; filename=' + file.file.name
    return response


def download_csv(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type="application/force-download")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            return response
    return HttpResponse("File not found")


def get_ip_address(request):
    user_ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
    if user_ip_address:
        ip = user_ip_address.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip



def get_object_or_email_alert(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        dev_alert_email(model, *args, **kwargs)
        print(f'error could not find object {model} {args} {kwargs}')
        return None