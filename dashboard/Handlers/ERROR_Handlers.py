from dashboard.Handlers.AUTH_Handler import RequireLogin, RequirePermission
from django.shortcuts import render

@RequireLogin
def HTTP_404(request, exception=None, *args, **kwargs):
    response = render(request, "ErrorPages/404.html")
    response.status_code = 404
    return response


@RequireLogin
def HTTP_500(request):
    context = {}
    response = render(request, "ErrorPages/500.html", context=context)
    response.status_code = 500
    return response


@RequireLogin
def HTTP_403(request, context=None, *args, **kwargs):
    response = render(request, "ErrorPages/403.html", context=context)
    response.status_code = 403
    return response
