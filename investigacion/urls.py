from django.conf.urls import include, url
from django.views.generic import TemplateView
from investigacion.views import Principal
from account.decorators import login_required
from . import views

app_name = 'investigacion'

urlpatterns = [
    url(r"^$",login_required(Principal.as_view()), name="principal"),
]
