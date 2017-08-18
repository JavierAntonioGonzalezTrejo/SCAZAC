# Report of Modifications
# Modification 20170723: Givesd the root URL to the calidadAire app to handle. 
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib import admin

urlpatterns = [
    url(r"^", include("calidadAire.urls")),                # TemplateView.as_view(template_name="homepage.html"), name="home")
    url(r"^admin/", include(admin.site.urls)),
    url(r"^account/", include("account.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
