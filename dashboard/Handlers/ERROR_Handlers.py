from dashboard.Handlers.AUTH_Handler import RequireLogin, RequirePermission
from dashboard.models import APP_Settings
from django.shortcuts import render

@RequireLogin
def HTTP_404(request, exception=None, *args, **kwargs):
    settings = APP_Settings.objects.all().first()
    response = render(request, str(settings.APP_lang)+"/ErrorPages/404.html")
    response.status_code = 404
    return response


@RequireLogin
def HTTP_500(request):
    context = {}
    settings = APP_Settings.objects.all().first()
    response = render(request, str(settings.APP_lang)+"/ErrorPages/500.html", context=context)
    response.status_code = 500
    return response


@RequireLogin
def HTTP_403(request, context=None, *args, **kwargs):
    settings = APP_Settings.objects.all().first()
    response = render(request, str(settings.APP_lang)+"/ErrorPages/403.html", context=context)
    response.status_code = 403
    return response
