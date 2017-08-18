# Report of Modifications
# Modification 20170723: Added the root URL to the F1-1 Requirment
# Modification 20170727: All the pages shuld end whit a slash. Added a namespace for Reverse url
from django.conf.urls import include, url
from calidadAire.views import ImecaData # 20170730: To load the Class based view
from django.views.generic import TemplateView # 20170811: To load templates directyle from the URL.py file
from . import views

app_name = 'calidadAire'

urlpatterns = [
    url(r"^$", views.index, name='PaginaPrincipal'),
    url(r"^datos/$", ImecaData.as_view(), name='DatosIMECA'),
    url(r"^reportes/$", views.reportes, name='ReportesAnuales'),
    url(r"^normatividad/$", TemplateView.as_view(template_name='calidadAire/f1_4.djhtml'), name='Normatividad'), # Added 20170811
    url(r"^infrestructura/$", TemplateView.as_view(template_name='calidadAire/f1_5.djhtml'), name='Infrestructura'), # Added 20170812
    url(r"^descargaimeca/(?P<stationID>[0-9]*)/$", views.descargaIMECA, name='DescargaIMECA'), # Added 20170814, can recibe the number id of an station.
    url(r"^descargaimeca/$", views.descargaIMECA, {'stationID': ''}, name='DescargaIMECAWA'), # Call the view Without Argument
]

