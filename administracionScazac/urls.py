from django.conf.urls import include, url
from django.views.generic import TemplateView
from account.decorators import login_required
from administracionScazac.views import MonitoringMapAdminView, MonitoringStationViewAdd, MonitoringStationViewModify, MonitoringDataViewAdd, MonitoringDataViewDelete

app_name = 'administracion'

urlpatterns = [
    url(r"^adminmapa$",login_required(MonitoringMapAdminView.as_view()), name="mapa"),
    url(r"^adminstationadd$",login_required(MonitoringStationViewAdd.as_view()), name="stationAdd"),
    url(r"^adminstationmodify$",login_required(MonitoringStationViewModify.as_view()), name="stationModify"),
    url(r"^admindata$",login_required(MonitoringDataViewAdd.as_view()), name="dataAdd"),
    url(r"^admindatadelete$",login_required(MonitoringDataViewDelete.as_view()), name="dataDelete"),
]

