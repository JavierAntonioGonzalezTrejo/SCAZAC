# Register of change
# Modification 20170721: use of the make_aware function to make a proper treatment to the DateTimeField
# Modification 20170807: Dates will be naive on the TimeZone
from random import randint
from django.core.wsgi import get_wsgi_application # To run the webserver
from django.utils.timezone import make_aware
import math
import os
import sys
import django
import math
import pandas
import dateutil.parser
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scazac.settings")

application = get_wsgi_application()

from investigacion.models import MonitoringStation, MonitoringData


# The first Step is to give the general information for the MonitoringStation

data = pandas.read_csv(sys.argv[1], low_memory=False) # First Argument the name path to the csv file
sizeData = len(data["Fecha"])
monitoringStation = MonitoringStation.objects.get(pk=int(sys.argv[2])) # Second Argument the Id of the monitoring Station as an Integer

for i in range(0, sizeData):
    pollant = MonitoringData()
    pollant.idStation = monitoringStation
    pollant.fecha = dateutil.parser.parse(data["Fecha"][i]) # BUG CORRECTED: Make all the register TimeZone Aware, Modified 20170807: Make all the Dates naive Date (WhitOutTimeZone)
    print pollant.fecha
    pollant.temperatura = data["Temp"][i]
    pollant.o3 = data["O3"][i]
    pollant.co = data["CO"][i]
    pollant.no = data["NO"][i]
    pollant.no2 = data["NO2"][i]
    pollant.nox = data["NOX"][i]
    pollant.so2 = data["SO2"][i]
    pollant.temperaturaAmbiente = data["TempAmbiente"][i]
    pollant.humedadRelativa = data["RH"][i]
    pollant.ws = data["WS"][i]
    pollant.wd = data["WD"][i]
    pollant.presionBarometrica = data["PresionBaro"][i]
    pollant.radiacionSolar = data["RadSolar"][i]
    pollant.precipitacion = data["Precipitacion"][i]
    pollant.pm10 = data["PM10"][i]
    pollant.pm25 = data["PM2.5"][i]
    pollant.imecaO3 = imecaO3(data["O3"][i])
    pollant.imecaNO = imecaNO(data["NO"][i])
    pollant.imecaNO2 = imecaNO(data["NO2"][i])
    pollant.imecaNOX = imecaNO(data["NOX"][i])
    pollant.imecaSO2 = imecaSO2(data["SO2"][i])
    pollant.imecaCO = imecaCO(data["CO"][i])
    pollant.imecaPM10 = imecaPM10(data["PM10"][i])
    pollant.imecaPM25 = imecaPM25(data["PM2.5"][i])
    pollant.save()
    
    
