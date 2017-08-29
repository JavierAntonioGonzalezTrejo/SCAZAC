# -*- coding: utf-8 -*-
# Register of Change:
# Modified 20170721: Adde the function index. Left the query to retrive the information of the data 
# Modified 20170723: Information about the map zoom, google API key and position will be given to using a model
# Modified 20170828: Bug Eliminated: The Query shows all the Monitoring Station data on one single Monitoring Station Table on the Template. Eliminated get function redundant code aun fully utilized the showImeca function on all the cases for the f1_2 requirment.
from __future__ import unicode_literals
from django.shortcuts import render
from investigacion.models import MonitoringStation, MonitoringData
from calidadAire.models import MonitoringReports, MonitoringMap, ImecaDataMonth, ImecaDataDay, ImecaDataHour
from django.shortcuts import render
from django.views.generic import TemplateView # Added 20170730: Create Class based Views
from datetime import date       # Added to give the year date on the view f1-2
from wsgiref.util import FileWrapper # Added 20170814 To send httpReponsce files
from django.http import HttpResponse
import sys
import json
import pandas                   # Addes 20170814: Uses to the requirment f1-6
import cStringIO as StringIO                 # Added 20170814 To utilize strings as files, or to utilizes virtual files (not on hardisk)
# Create your views here.

def index(request):             # Rewritted 20170730: Replaced the Old for loop to obtain the mean of the imecas whit the imeca mean function.
    """SRS Requierment F1-01"""
    # Create variables as dictionary, and the variables which will hold the imecas
    monitoringInfo = {}
    imecas = []
    # First, We retrive all the Monitoring Stations
    allMonitors = MonitoringStation.objects.all()
    # A simple for on each monitor
    for monitor in allMonitors:
        # Create the JSON for each monitoring data which will hold a day of pollant information
        monitoringInfo[str(monitor.serialNumber)] = {'nameMonitoringPlace': monitor.nameMonitoringPlace, 'year': monitor.dateNewestRegister.year , 'month': monitor.dateNewestRegister.month, 'day': monitor.dateNewestRegister.day, 'center': {'lat': float(monitor.latitude), 'lng': float(monitor.length)}, 'radius': int(monitor.monitoringRadius), 'pollantName': [], 'pollantImeca': []}
        # Get the data form the newest day on the monitoring Station
        allMonitoringData = MonitoringData.objects.filter(fecha__icontains=monitor.dateNewestRegister).filter(idStation__pk=monitor.serialNumber)
        # Get the number of register from that Day
        numberData = len(allMonitoringData)
        # Obtain the Mean of all the imceas from the Newest Day specified on the Monitoring Station
        imecas = imecaMean(allMonitoringData, numberData)

        # Put the information on the Dictionary
        monitoringInfo[str(monitor.serialNumber)]['pollantName'] = ["Ozono", "Óxido de Nitrógeno", "Dióxido de Nitrógeno", "NOx", "Dióxido de Azufre", "Óxido de Carbono", "Particulas Contaminantes (10 Micrones)", "Particulas Contaminantes (2.5 Micrones)"]

        for imeca in imecas:
            monitoringInfo[str(monitor.serialNumber)]['pollantImeca'].append(imeca)

    # The information of the Map will be unique, so is safe to use the pk 1
    mapInformation = MonitoringMap.objects.get(pk=1)

    return render(request, "f1.djhtml", {
        "pollantData": json.dumps(monitoringInfo),
        "zoom": mapInformation.zoom,
        "centerMapLat": mapInformation.centerLatitude,
        "centerMapLng": mapInformation.centerLength,
        "keyGoogleMap": mapInformation.googleAPIKey})

class ImecaData(TemplateView):  # Added 20170730
    """Class that represents the View for the Requirment F1-2"""
    year_list = []
    station_list = {}
    tableStation_list = {}
    tableType = 1
    model = MonitoringStation   # Model of the Station
    dataModel = MonitoringData  # Model of Data
    monitoringStations  = model.objects.all() # Used to obtain the oldest year which have data stored on the sistem
    numberData2Show = 24        # Each time span have diferent number of data to show (Day: Hours, Month: Day, Year: Month. This variable tells the for loop how many loops can be obtained for the tyme span selectiones
    rangeTimeSpan = range(1, numberData2Show)         # Create the Time Span depending on the type of the Table
    try:
        dateShowed = str(monitoringStations[0].dateNewestRegister) + " " # DateShowed Have the time Span to be showed, example 2017-07-05, 2017-12, 2018, is here because it needs the be dynamic the first time that the page is loaded. 
    except:
        print "Out of the shelf system, ADD DATA"
        
    def __init__(self):
        """Common process to the view"""
        self.year_list = []
        self.station_list = {}
        self.tableStation_list = {}
        # First get the Year list, the year list will contain the oldest year of all the monitoring station to the current year
        self.year_list.append(int(self.monitoringStations.order_by('dateOldestRegister')[0].dateOldestRegister.year))
        # Obtian the diference in years between the oldest year and the current year
        numberYears = date.today().year - self.year_list[0]
    
        # Apend each year 
        for years in range(1, numberYears + 1):
            self.year_list.append(self.year_list[0] + years)

        # Give infotmation to the select form: Id for the internal identification of the system and nameMonitoringStation to give information about which monitoring station the User is selecting
        for station in self.monitoringStations:
            self.station_list[str(station.serialNumber)] = station.nameMonitoringPlace
             
    def get(self, request):
        """The Main Function"""
        if request.GET:
            # Set the variable True if the the date comes from the get request

            # Select the Monitoring stations depending on the selected form
            if not(request.GET['station'] == "A"):
                self.monitoringStations  = MonitoringStation.objects.filter(serialNumber=request.GET['station'])
            
            if request.GET['range'] == "1":
                self.dateShowed = request.GET['year'] + "-" + request.GET['month'] + "-" +  request.GET['day'] + " "
                return self.showImeca(request, ImecaDataHour)
                
            elif request.GET['range'] == "2":
                self.dateShowed = request.GET['year'] + "-" + request.GET['month'] + "-"
                self.numberData2Show = self.numberDaysMonth(request.GET['year'], request.GET['month'])
                self.rangeTimeSpan = range(1, self.numberData2Show)
                self.tableType = 2
                return self.showImeca(request, ImecaDataDay) # Modified to utilize the new method to retrive info from the server

            elif request.GET['range'] == "3":
                self.dateShowed = request.GET['year'] + "-"
                self.numberData2Show = 13
                self.rangeTimeSpan = range(1, self.numberData2Show)
                self.tableType = 3
                return self.showImeca(request, ImecaDataMonth)

        return self.showImeca(request, ImecaDataHour)
        

    def showImeca(self, request, modelImeca):
        """Function utilized to extract the IMECA values from the respective Model and not calculate the IMECA mean on the fly """
        #Index used the utilize the respective list for each station on the tableStation_list
        indexStation = 0
    
    
        for station in self.monitoringStations:
            self.tableStation_list[station.nameMonitoringPlace] = [self.dateShowed]

           # Append the list for each station on the dictionary
            self.tableStation_list[station.nameMonitoringPlace].append([])

           # Index indicating the list of the corresponding time span, example, the list for all the values on. The reason to no use numberData is beacause is posible that a dayy migth not exist and the following does, so the index must stay the same
            indexTimeSpan = 0
            
            # Pass throw the hours, days and months in the type table as day, month, year
            for numberData in self.rangeTimeSpan:
                # Get the Data of the respective range of time depending on the type of table
                imecaData = modelImeca.objects.filter(fecha__icontains=str(self.dateShowed) + self.number2ZeroBeforeDigit(numberData)).filter(idStation__pk=station.serialNumber)# Added 20170808 Added the filter of the monitor

                try:
                    
                    # Create a new list inside the list of this station (The current station) to hold the imecas   
                    self.tableStation_list[station.nameMonitoringPlace][1].append([])
                    
                    self.tableStation_list[station.nameMonitoringPlace][1][indexTimeSpan].append(self.stringTimeSpan(self.tableType,numberData))

                    if imecaData[0].imecaO3 == None:
                        self.tableStation_list[station.nameMonitoringPlace][1][indexTimeSpan].append("Inexistente.")
                    else:
                        self.tableStation_list[station.nameMonitoringPlace][1][indexTimeSpan].append(imecaData[0].imecaO3)

                    if imecaData[0].imecaNO == None:
                        self.tableStation_list[station.nameMonitoringPlace][1][indexTimeSpan].append("Inexistente.")
                    else:
                        self.tableStation_list[station.nameMonitoringPlace][1][indexTimeSpan].append(imecaData[0].imecaNO)

                    if imecaData[0].imecaNO2 == None:
                        self.tableStation_list[station.nameMonitoringPlace][1][indexTimeSpan].append("Inexistente.")
                    else:
                        self.tableStation_list[station.nameMonitoringPlace][1][indexTimeSpan].append(imecaData[0].imecaNO2)

                    if imecaData[0].imecaNOX == None:
                        self.tableStation_list[station.nameMonitoringPlace][1][indexTimeSpan].append("Inexistente.")
                    else:
                        self.tableStation_list[station.nameMonitoringPlace][1][indexTimeSpan].append(imecaData[0].imecaNOX)

                    if imecaData[0].imecaSO2 == None:
                        self.tableStation_list[station.nameMonitoringPlace][1][indexTimeSpan].append("Inexistente.")
                    else:
                        self.tableStation_list[station.nameMonitoringPlace][1][indexTimeSpan].append(imecaData[0].imecaSO2)

                    if imecaData[0].imecaCO == None:
                        self.tableStation_list[station.nameMonitoringPlace][1][indexTimeSpan].append("Inexistente.")
                    else:
                        self.tableStation_list[station.nameMonitoringPlace][1][indexTimeSpan].append(imecaData[0].imecaCO)

                    if imecaData[0].imecaPM10 == None:
                        self.tableStation_list[station.nameMonitoringPlace][1][indexTimeSpan].append("Inexistente.")
                    else:
                        self.tableStation_list[station.nameMonitoringPlace][1][indexTimeSpan].append(imecaData[0].imecaPM10)

                    if imecaData[0].imecaPM25 == None:
                        self.tableStation_list[station.nameMonitoringPlace][1][indexTimeSpan].append("Inexistente.")
                    else:
                        self.tableStation_list[station.nameMonitoringPlace][1][indexTimeSpan].append(imecaData[0].imecaPM25)
                except:
                    for i in range(0,8):
                        self.tableStation_list[station.nameMonitoringPlace][1][indexTimeSpan].append("Inexistente.")
                indexTimeSpan += 1

        return render(request, "calidadAire/f1_2.djhtml", 
                      {'year_list': self.year_list,
                       'station_list': self.station_list,
                       'tableStation_list': self.tableStation_list,
                       'tableType': self.tableType})

    def number2ZeroBeforeDigit(self,number):
        """Returns a the digit whit a zero before if the number it is below 10"""
        if number < 10:
            return "0" + str(number)
        else:
            return str(number)
        
    def stringTimeSpan(self,typeTable, number):
        """Return the corresponding string depending on the type of table selected"""
        if typeTable == 1:
            return self.number2ZeroBeforeDigit(number) + ":00"
        elif typeTable == 3:
            if number == 1:
                return "Enero"
            elif number == 2:
                return "Febrero"
            elif number == 3:
                return "Marzo"
            elif number == 4:
                return "Abril"
            elif number == 5:
                return "Mayo"
            elif number == 6:
                return "Junio"
            elif number == 7:
                return "Julio"
            elif number == 8:
                return "Agosto"
            elif number == 9:
                return "Septiembre"
            elif number == 10:
                return "Octubre"
            elif number == 11:
                return "Noviembre"
            elif number == 12:
                return "Diciembre"
        else:                   # Corrected 20170806: The Else belongs to the main if
                return str(number)
    def numberDaysMonth(self,year, month):
        """Calculate the number of days depending on the year and the month"""
        if month == "01" or month == "03" or month == "05" or month == "07" or month == "08" or month == "10" or month == "12" :
            return 32
        elif month == "04" or month == "06" or month == "09" or month == "11":
            return 31
        elif month == "02":
            if int(year) % 4 == 0 and not(int(year) % 100 == 0) or int(year) % 400 == 0:
                return 30
            else:
                return 29
        return None
        
def reportes(request):
    """Corousel to download Anual Air Quality Reports"""
    reports_List = []
    try:
        reports = MonitoringReports.objects.all()
        activeReport = reports[0] # This is the operation that will trigger the try 
        for report in reports:
            reports_List.append(report)
        del reports_List[0]    # Delete the first one because is stored on the activeReport variable
        return render(request, "calidadAire/f1_3.djhtml", {
            'activeReport' : activeReport,
            'reports_List' : reports_List
        })
    except:
        return render(request, "calidadAire/f1_3.djhtml", {
            'activeReport' : activeReport,
            'reports_List' : reports_List
        })

    
def descargaIMECA(request, stationID):
    """View for the requirment f1_6"""

    if not(stationID == ""):
        # Get the IMECA Data of the moniroting Station
        imecaData = ImecaDataHour.objects.filter(idStation__pk=stationID)
        # Set the temporary file on ram
        outPutCSV = StringIO.StringIO()
        # Write the string output to the virtualfile
        fecha = []
        imecaO3 = []
        imecaNO = []
        imecaNO2 = []
        imecaNOX = []
        imecaSO2 = []
        imecaCO = []
        imecaPM10 = []
        imecaPM25 = []

        # Append all the imecaData on the corresponging lists
        for imeca in imecaData:
            fecha.append(str(imeca.fecha))
            imecaO3.append(imeca.imecaO3)
            imecaNO.append(imeca.imecaNO)
            imecaNO2.append(imeca.imecaNO2)
            imecaNOX.append(imeca.imecaNOX)
            imecaSO2.append(imeca.imecaSO2)
            imecaCO.append(imeca.imecaCO)
            imecaPM10.append(imeca.imecaPM10)
            imecaPM25.append(imeca.imecaPM25)
        # Set the index
        cantidad = range(len(imecaData))
        # Append all the lists to a Pandas Object
        dataCsv = pandas.DataFrame({
            'Fecha': fecha,
            'IMECA O3': imecaO3,
            'IMECA NO': imecaNO,
            'IMECA NO2': imecaNO2,
            'IMECA NOX': imecaNOX,
            'IMECA SO2': imecaSO2,
            'IMECA CO' : imecaCO,
            'IMECA PM10' : imecaPM10,
            'IMECA PM25' : imecaPM25}, index=cantidad)
        # Sve the data on the virtual file
        dataCsv[['Fecha', 'IMECA O3','IMECA NO', 'IMECA NO2', 'IMECA NOX', 'IMECA SO2', 'IMECA CO', 'IMECA PM10', 'IMECA PM25']].to_csv(outPutCSV,index=False)
        
        # Set the httpRequest to send the file
        outPutCSV.seek(0)
        response = HttpResponse(outPutCSV.getvalue(), content_type='application/csv')
        response['Content-Disposition'] = 'attachment; filename=imecaDataStation' + stationID + '.csv'
        
        return response
        
    else:
        
        station_list= MonitoringStation.objects.all()
        return render(request, "calidadAire/f1_6.djhtml", {
            'station_list':station_list
        })
# Common Functions (Non-view Functions)

def minYear(monitoringStations): # DELETED 20170730: No longer on use. Decapretaded
    """Used to evaluate the evaluate the oldest year of the monitoring station"""
    yearMin = sys.maxint 
    for station in monitoringStations:
        if int(station.dateOldestRegister.year) < yearMin:
            yearMin = int(station.dateOldestRegister.year)
    return yearMin

    

        
def imecaMean(monitoringStation, sizeData): # Rewwited 20170730: Replaced Ifs on the for loop whit try to make them faster.
    """Determines the mean of each IMECA. If the IMECA does"""
    imecas = [0 for i in range(0, 8)]

    for imeca in monitoringStation:
        try:
            imecas[0] += float(imeca.imecaO3)
        except:
            imecas[0] = None
        try:
            imecas[1] += float(imeca.imecaNO)
        except:
            imecas[1] = None
        try:
            imecas[2] += float(imeca.imecaNO2)
        except:
            imecas[2] = None
        try:
            imecas[3] += float(imeca.imecaNOX)
        except:
            imecas[3] = None
        try:
            imecas[4] += float(imeca.imecaSO2)
        except:
            imecas[4] = None
        try:
            imecas[5] += float(imeca.imecaCO)
        except:
            imecas[5] = None
        try:
            imecas[6] += float(imeca.imecaPM10)
        except:
            imecas[6] = None
        try:
            imecas[7] += float(imeca.imecaPM25)
        except:
            imecas[7] = None
    # Calculate the mean of the imeca and converit to float
    for i in range(0, 8):
        try:
            imecas[i] /= sizeData
            imecas[i] = round(imecas[i],2)
        except:
            imecas[i] = None
    return imecas    
        

