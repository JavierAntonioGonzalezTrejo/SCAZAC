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

def imecaO3(o3):
    """Formula to calculate the imeca of the Ozone"""
    if 0 <= o3 and o3 <= 0.220:
        return o3 * 50/0.055
    elif 0.220 < o3:
        return 03 * 200/0.22
    else:
        return 0
def imecaNO(no):
    """Imeca for the NO, NO2 and NOX"""
    if 0.000 <= no and no <= 0.420:
        return no * 50/0.105
    elif 0.420 < no:
        return no * 200/0.42
    return 0
    

        
def imecaSO2(so2):
    """Imeca for the SO2"""
    if 0.000 <= so2 and so2 <= 0.260:
        return so2 * 50 / 0.065
    elif 0.260 < so2:
        return so2 * 200 / 0.26
    else:
        return 0
            
def imecaCO(co):
    """Imeca for the CO"""
    if 0.00 <= co and co <= 22.00:
        return co * 50 / 5.5
    elif 22.00 < co:
        return co * 200 / 22
    else:
        return 0

def imecaPM10(pm10):
    """Imeca for the PM10"""
    if 0 <= pm10 and pm10 <= 120:
        return pm10 * 50 / 60
    elif 120 < pm10 and pm10 <= 320:
        return 40 + pm10 * 50 / 100
    elif 320 < pm10:
        return pm10 * 200 / 320
    else:
        return 0
        
def imecaPM25(pm25):
    """Imeca for the PM25"""
    if 0 <= pm25 and pm25 <= 15.4:
        return pm25 * 50 / 15.4
    elif 15.4 < pm25 and pm25 <= 40.4:
        return 20.50 + pm25 * 48 / 24.9
    elif 40.4 < pm25 and pm25 <= 65.4:
        return 21.30 + pm25 * 49 / 24.9
    elif 65.4 < pm25 and pm25 <= 150.4:
        return 113.20 + pm25 * 49 / 84.9
    elif 150.4 < pm25:
        return pm25 * 201 / 150.5
    else:
        return 0

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
    
    
