# -*- coding: utf-8 -*-
# Modified 20171009: Adding all the models form the app to be modifies on the Admin site
from __future__ import unicode_literals
from django.contrib import admin
from calidadAire.models import *

admin.site.register(MonitoringReports)
admin.site.register(MonitoringMap)
admin.site.register(ImecaDataDay)
admin.site.register(ImecaDataMonth)
admin.site.register(ImecaDataHour)

