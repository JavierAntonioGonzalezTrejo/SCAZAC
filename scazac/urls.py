# Report of Modifications
# Modification 20170723: Givesd the root URL to the calidadAire app to handle.
# 20170924: URL from requirment F3 handle by investigacion
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib import admin
import calidadAire.views


urlpatterns = [
    url(r"^$", calidadAire.views.index, name='home'),#              
    url(r"^", include("calidadAire.urls")),                # 
    url(r"^admin/", include(admin.site.urls)),
    url(r"^usuario/", include("account.urls")),
    url(r"^investigacion/", include("investigacion.urls")), # Added 20170924
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
