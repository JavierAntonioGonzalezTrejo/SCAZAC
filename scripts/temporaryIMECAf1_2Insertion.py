from django.core.wsgi import get_wsgi_application # To run the webserver
from django.utils.timezone import make_aware
import math
import os
import sys
import django
import math
import pandas
import dateutil.parser
import datetime

def number2ZeroBeforeDigit(number):
        """Returns a the digit whit a zero before if the number it is below 10"""
        if number < 10:
            return "0" + str(number)
        else:
            return str(number)

def imecaMean(monitoringStation, sizeData): # Rewwited 20170730: Replaced Ifs on the for loop whit try to make them faster.
    """Determines the mean of each IMECA. If the IMECA does"""
    imecas = [0 for i in range(0, 8)]

    for imeca in monitoringStation:
        try:
            imecas[0] += imeca.imecaO3
        except:
            imecas[0] = None

        try:
            imecas[1] += imeca.imecaNO
        except:
            imecas[1] = None
        try:
            imecas[2] += imeca.imecaNO2
        except:
            imecas[2] = None
        try:
            imecas[3] += imeca.imecaNOX
        except:
            imecas[3] = None
        try:
            imecas[4] += imeca.imecaSO2
        except:
            imecas[4] = None
        try:
            imecas[5] += imeca.imecaCO
        except:
            imecas[5] = None
        try:
            imecas[6] += imeca.imecaPM10
        except:
            imecas[6] = None
        try:
            imecas[7] += imeca.imecaPM25
        except:
            imecas[7] = None
    # Calculate the mean of the imeca and converit to float
    for i in range(0, 8):
        try:
            imecas[i] /= sizeData
            imecas[i] = imecas[i]
        except:
            imecas[i] = None
    return imecas

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scazac.settings")

application = get_wsgi_application()

from investigacion.models import MonitoringStation, MonitoringData
from calidadAire.models import ImecaDataDay, ImecaDataMonth

allStations = MonitoringStation.objects.all()

for station in allStations:

    # Put the oldest day of monitoring 
    pollantDay = station.dateOldestRegister
    pollantDayData = MonitoringData.objects.filter(fecha__icontains=pollantDay).filter(idStation__pk=station.serialNumber)
    
    
    while pollantDay <= station.dateNewestRegister:
        
        dayImecas = ImecaDataDay()
        pollantDayDataSize = len(pollantDayData)
        
        if not(pollantDayData == 0):
            # Save the data on the system
            arrayIMECA = imecaMean(pollantDayData, pollantDayDataSize)
            dayImecas.fecha = pollantDay
            dayImecas.idStation = station
            dayImecas.imecaO3 = arrayIMECA[0]
            dayImecas.imecaNO = arrayIMECA[1]
            dayImecas.imecaNO2 = arrayIMECA[2]
            dayImecas.imecaNOX = arrayIMECA[3]
            dayImecas.imecaSO2 = arrayIMECA[4]
            dayImecas.imecaCO = arrayIMECA[5]
            dayImecas.imecaPM10 = arrayIMECA[6]
            dayImecas.imecaPM25 = arrayIMECA[7]
            dayImecas.save()
            print str(dayImecas.fecha)
            # Continue whit the next day
            pollantDay += datetime.timedelta(days=1)
            pollantDayData = MonitoringData.objects.filter(fecha__icontains=pollantDay).filter(idStation__pk=station.serialNumber)
        else:
            # Just continue whit the next day
            pollantDay += datetime.timedelta(days=1)
            pollantDayData = MonitoringData.objects.filter(fecha__icontains=pollantDay).filter(idStation__pk=station.serialNumber)

for station in allStations:

    # Put the oldest month of monitoring 
    pollantMonth = dateutil.parser.parse(str(station.dateOldestRegister.year) + "-" + number2ZeroBeforeDigit(station.dateOldestRegister.month) + "-" + "01").date()
    # Making sure that the query will compare only the year and month
    pollantMonthString = str(pollantMonth.year) + "-" + number2ZeroBeforeDigit(pollantMonth.month)
    pollantMonthData = MonitoringData.objects.filter(fecha__icontains=pollantMonthString).filter(idStation__pk=station.serialNumber)
    
    # 
    while pollantMonth <= station.dateNewestRegister:
        
        monthImecas = ImecaDataMonth()
        pollantMonthDataSize = len(pollantMonthData)
        print pollantMonthString
        if not(pollantMonthDataSize == 0):
            # Save the data on the system
            arrayIMECA = imecaMean(pollantMonthData, pollantMonthDataSize)
            monthImecas.setFecha(str(pollantMonth.year), number2ZeroBeforeDigit(pollantMonth.month))
            monthImecas.idStation = station
            monthImecas.imecaO3 = arrayIMECA[0]
            monthImecas.imecaNO = arrayIMECA[1]
            monthImecas.imecaNO2 = arrayIMECA[2]
            monthImecas.imecaNOX = arrayIMECA[3]
            monthImecas.imecaSO2 = arrayIMECA[4]
            monthImecas.imecaCO = arrayIMECA[5]
            monthImecas.imecaPM10 = arrayIMECA[6]
            monthImecas.imecaPM25 = arrayIMECA[7]
            monthImecas.save()

            # Continue whit the next month, if month == 12, continue whit the next month of the next year
            if pollantMonth.month < 12:
                pollantMonth = pollantMonth.replace(month=pollantMonth.month + 1)
            else:
                pollantMonth = pollantMonth.replace(month=1, year=pollantMonth.year + 1)
            
            pollantMonthString = str(pollantMonth.year) + "-" + number2ZeroBeforeDigit(pollantMonth.month)
            pollantMonthData = MonitoringData.objects.filter(fecha__icontains=pollantMonthString).filter(idStation__pk=station.serialNumber)
        else:
            # Just continue whit the next month
            if pollantMonth.month < 12:
                pollantMonth = pollantMonth.replace(month=pollantMonth.month + 1)
            else:
                pollantMonth = pollantMonth.replace(month=1, year=pollantMonth.year + 1)
            pollantMonthString = str(pollantMonth.year) + "-" + number2ZeroBeforeDigit(pollantMonth.month)
            pollantMonthData = MonitoringData.objects.filter(fecha__icontains=pollantMonthString).filter(idStation__pk=station.serialNumber)

# For ImecaDataHour

for station in allStations:

    # Put the oldest month of monitoring 
    pollantHour = dateutil.parser.parse(str(station.dateOldestRegister.year) + "-" + number2ZeroBeforeDigit(station.dateOldestRegister.month) + "-" + str(station.dateOldestRegister.hour))
    # Making sure that the query will compare only the year and month
    pollantHourString = str(pollantHour.year) + "-" + number2ZeroBeforeDigit(pollantHour.month) + "-" + number2ZeroBeforeDigit(pollantHour.day) + " " + number2ZeroBeforeDigit(pollantHour.hour)
    pollantHourData = MonitoringData.objects.filter(fecha__icontains=pollantHourString).filter(idStation__pk=station.serialNumber)
    
    # 
    while pollantHour <= station.dateNewestRegister:
        
        monthImecas = ImecaDataHour()
        pollantHourDataSize = len(pollantHourData)
        print pollantHourString
        if not(pollantHourDataSize == 0):
            # Save the data on the system
            arrayIMECA = imecaMean(pollantHourData, pollantHourDataSize)
            monthImecas.setFecha(str(pollantHour.year), number2ZeroBeforeDigit(pollantHour.month),number2ZeroBeforeDigit(pollantHour.day), number2ZeroBeforeDigit(pollantHour.hour) )
            monthImecas.idStation = station
            monthImecas.imecaO3 = arrayIMECA[0]
            monthImecas.imecaNO = arrayIMECA[1]
            monthImecas.imecaNO2 = arrayIMECA[2]
            monthImecas.imecaNOX = arrayIMECA[3]
            monthImecas.imecaSO2 = arrayIMECA[4]
            monthImecas.imecaCO = arrayIMECA[5]
            monthImecas.imecaPM10 = arrayIMECA[6]
            monthImecas.imecaPM25 = arrayIMECA[7]
            monthImecas.save()

            
            
            pollantHour += datetime.timedelta(hours=1)
            pollantHourString = str(pollantHour.year) + "-" + number2ZeroBeforeDigit(pollantHour.month) + "-" + number2ZeroBeforeDigit(pollantHour.day) + " " + number2ZeroBeforeDigit(pollantHour.hour)
            pollantHourData = MonitoringData.objects.filter(fecha__icontains=pollantHourString).filter(idStation__pk=station.serialNumber)
        else:
            pollantHour += datetime.timedelta(hours=1)
            pollantHourString = str(pollantHour.year) + "-" + number2ZeroBeforeDigit(pollantHour.month) + "-" + number2ZeroBeforeDigit(pollantHour.day) + " " + number2ZeroBeforeDigit(pollantHour.hour)
            pollantHourData = MonitoringData.objects.filter(fecha__icontains=pollantHourString).filter(idStation__pk=station.serialNumber)

