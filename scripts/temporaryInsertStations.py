from random import randint
import os
import sys
import django
import math
import pandas
import dateutil.parser
from django.core.wsgi import get_wsgi_application # To run the webserver
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scazac.settings")

application = get_wsgi_application()

from investigacion.models import MonitoringStation

def newstOldestDate(data):
    """Calculate both the Newest and Oldest Date on the data specified"""
    new = dateutil.parser.parse(data[0])
    old = new

    for dateStr in data:
        date = dateutil.parser.parse(dateStr)
        if date < old:
            old = date
        elif date > new:
            new = date
    return { 'old':  old, 'new': new }

numberSerial = 1
monitoringPlaceName = "C. Zacatecas Centro"
lat = 22.7744958
lng = -102.5770257
radius = 1000
data = pandas.read_csv(sys.argv[1], low_memory=False)
sizeData = len(data["Fecha"])
listDate = newstOldestDate(data["Fecha"])
newDate = listDate['new']
oldDate = listDate['old']

monitoring = MonitoringStation()
monitoring.serialNumber = numberSerial
monitoring.nameMonitoringPlace = monitoringPlaceName
monitoring.latitude = lat
monitoring.length = lng
monitoring.monitoringRadius = radius
monitoring.dateNewestRegister = newDate
monitoring.dateOldestRegister = oldDate
monitoring.save()
