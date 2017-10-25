# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Modification 20171022: Requirment F3-3 finished.
# Modification 20171025: Requirment F3 finished.
import datetime
from django.db.models import Max
import json
import pandas
import dateutil.parser
from django import forms
from decimal import Decimal
from administracionScazac.forms import MonitoringMapForm
from investigacion.models import MonitoringStation, MonitoringData
from calidadAire.models import MonitoringReports, MonitoringMap, ImecaDataMonth, ImecaDataDay, ImecaDataHour
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView
from django.shortcuts import render

# Create your views here.
class MonitoringMapAdminView(TemplateView): # Added 20171016
    """Requirment F3-2"""
    def get(self, request):
        """Preview of the current map settings"""
        if not(request.user.is_superuser):
            raise PermissionDenied
        try:
            mapSettings = MonitoringMap.objects.get(pk=1) # Get the initial map Settings, only the first register is used on the System
            formInitialValues = {'centerLatitude':mapSettings.centerLatitude, 'centerLength':mapSettings.centerLength, 'zoom':mapSettings.zoom, 'googleAPIKey':mapSettings.googleAPIKey}
            mapSettingsForm = MonitoringMapForm(formInitialValues)
            return render(request, 'administracionScazac/homepage.djhtml',
                          {'mapSettingsForm':mapSettingsForm,
                           'keyGoogleMap':mapSettings.googleAPIKey,
                           'centerLatitude':mapSettings.centerLatitude,
                           'centerLength':mapSettings.centerLength,
                           'zoom':mapSettings.zoom})
        except:
            mapSettingsForm = MonitoringMapForm(formInitialValues)
            return render(request, 'administracionScazac/homepage.djhtml',
                          {'mapSettingsForm':mapSettingsForm})

    def post(self, request):
        """Modifie the current map settings"""
        
        if not(request.user.is_superuser):
            raise PermissionDenied
        mapSettingsForm = MonitoringMapForm(request.POST)
        if mapSettingsForm.is_valid():
            try:
                mapSettings = MonitoringMap.objects.get(pk=1) # Get the initial map Settings, only the first register is used on the 
            except:
                mapSettings = MonitoringMap()
                mapSettings.idMap = 1
            mapSettings.centerLatitude = mapSettingsForm.cleaned_data['centerLatitude']
            mapSettings.centerLength = mapSettingsForm.cleaned_data['centerLength']
            mapSettings.zoom = mapSettingsForm.cleaned_data['zoom']
            mapSettings.googleAPIKey = mapSettingsForm.cleaned_data['googleAPIKey']
            mapSettings.save()
            
            alertModified = "alert(\"Se ah modificado la configuración con exito!!!\");"
            return render(request, 'administracionScazac/homepage.djhtml',
                      {'mapSettingsForm':mapSettingsForm,
                       'keyGoogleMap':mapSettings.googleAPIKey,
                       'centerLatitude':mapSettings.centerLatitude,
                       'centerLength':mapSettings.centerLength,
                       'zoom':mapSettings.zoom,
                       'alertModified':alertModified})
        else:
            return render(request, 'administracionScazac/homepage.djhtml',
                      {'mapSettingsForm':mapSettingsForm,
                       'keyGoogleMap':mapSettingsForm.cleaned_data['googleAPIKey'],
                       'centerLatitude':mapSettingsForm.cleaned_data['centerLatitude'],
                       'centerLength':mapSettingsForm.cleaned_data['centerLength'],
                       'zoom': mapSettingsForm.cleaned_data['zoom']})


class MonitoringStationViewAdd(TemplateView):
    """Requerimento F3-?"""

    title = "Agregar Estación de Monitoreo"
    def get(self, request):
        """Principal view"""
        if not(request.user.is_superuser):
            raise PermissionDenied
        monitoringStationForm = generateMonitoringStationFormAddOrModify(True)()
        try:
            mapSettings = MonitoringMap.objects.get(pk=1)
        except:
            return HttpResponseRedirect("/admin/adminmapa")
        return render(request, 'administracionScazac/monitoringStation.djhtml',
                      {'monitoringStationForm':monitoringStationForm,
                       'keyGoogleMap':mapSettings.googleAPIKey,
                       'centerLatitude':mapSettings.centerLatitude,
                       'centerLength':mapSettings.centerLength,
                       'zoom':mapSettings.zoom,
                       'titulo':MonitoringStationViewAdd.title,
                       'isAdd':True})
    
    def post(self, request):
        """Save the Monitoring Station"""
        if not(request.user.is_superuser):
            raise PermissionDenied
        monitoringStationForm = generateMonitoringStationFormAddOrModify(True)(request.POST)
        try:
            mapSettings = MonitoringMap.objects.get(pk=1) # Get the initial map Settings, only the first register is used on the System
        except:
            return HttpResponseRedirect("/admin/adminmapa")
        if monitoringStationForm.is_valid():
            savedMonitoringStation = MonitoringStation()
            lastSerialNumber = MonitoringStation.objects.latest('serialNumber').serialNumber
            
            if lastSerialNumber == 0:
                savedMonitoringStation.serialNumber = 1
            else:
                savedMonitoringStation.serialNumber = lastSerialNumber + 1
            savedMonitoringStation.nameMonitoringPlace = monitoringStationForm.cleaned_data['nameMonitoringPlace']
            savedMonitoringStation.latitude = monitoringStationForm.cleaned_data['latitude']
            savedMonitoringStation.length = monitoringStationForm.cleaned_data['length']
            savedMonitoringStation.monitoringRadius = monitoringStationForm.cleaned_data['monitoringRadius']
            
            datePlaceHolder = datetime.datetime.now().date() # The newest and oldest date will be calculated when the data is summited
            savedMonitoringStation.dateNewestRegister = datePlaceHolder
            savedMonitoringStation.dateOldestRegister = datePlaceHolder
            savedMonitoringStation.save()
            alertSaved = "alert(\"Se ah guardado la estación con exito!!!\");"
            return render(request, 'administracionScazac/monitoringStation.djhtml',
                      {'monitoringStationForm':monitoringStationForm,
                       'keyGoogleMap':mapSettings.googleAPIKey,
                       'centerLatitude':mapSettings.centerLatitude,
                       'centerLength':mapSettings.centerLength,
                       'zoom':mapSettings.zoom,
                       'alertSaved':alertSaved,
                       'titulo':MonitoringStationViewAdd.title,
                       'isAdd':True})
        else:
            return render(request, 'administracionScazac/monitoringStation.djhtml',
                      {'monitoringStationForm':monitoringStationForm,
                       'keyGoogleMap':mapSettings.googleAPIKey,
                       'centerLatitude':mapSettings.centerLatitude,
                       'centerLength':mapSettings.centerLength,
                       'zoom':mapSettings.zoom,
                       'titulo':MonitoringStationViewAdd.title,
                       'isAdd':True})

class MonitoringStationViewModify(TemplateView):
    """Requerimento F3-?"""
    title = "Modificar Estación de Monitoreo"
    def get(self, request):
        """Principal view"""
        if not(request.user.is_superuser):
            raise PermissionDenied
        monitoringStationForm = generateMonitoringStationFormAddOrModify(False)()
        try:
            mapSettings = MonitoringMap.objects.get(pk=1)
        except:
            return HttpResponseRedirect("/admin/adminmapa")
        jsonStation = generateJsonStationModifyView()
        alertForErase = "alert(\"Se borrara la estación especificada, si desea no borrarla porfavor presione atras en su navegador.!!!\");"
        return render(request, 'administracionScazac/monitoringStation.djhtml',
                      {'monitoringStationForm':monitoringStationForm,
                       'keyGoogleMap':mapSettings.googleAPIKey,
                       'centerLatitude':mapSettings.centerLatitude,
                       'centerLength':mapSettings.centerLength,
                       'zoom':mapSettings.zoom,
                       'titulo': MonitoringStationViewModify.title,
                       'jsonStation':json.dumps(jsonStation),
                       'stationID':1,
                       'alertForErase': alertForErase,
                       'isAdd':False}) # Because allways the first station will be showed.
    
    def post(self, request):
        """Save the Monitoring Station"""
        if not(request.user.is_superuser):
            raise PermissionDenied
        monitoringStationForm = generateMonitoringStationFormAddOrModify(False)(request.POST)
        try:
            mapSettings = MonitoringMap.objects.get(pk=1) # Get the initial map Settings, only the first register is used on the System
        except:
            return HttpResponseRedirect("/admin/adminmapa")
        if monitoringStationForm.is_valid():
            alertForErase = "alert(\"Se borrara la estación especificada, si desea no borrarla porfavor presione atras en su navegador.!!!\");"
            if request.POST["actionPerform"] == "1": # Save the data on the Monitoring Station exept the dates because they are calculed only one time when the data is inserted.
                savedMonitoringStation = MonitoringStation.objects.get(pk=request.POST["nameMonitoringPlace"])
                savedMonitoringStation.latitude = monitoringStationForm.cleaned_data['latitude']
                savedMonitoringStation.length = monitoringStationForm.cleaned_data['length']
                savedMonitoringStation.monitoringRadius = monitoringStationForm.cleaned_data['monitoringRadius']
                savedMonitoringStation.save()
                alertSaved = "alert(\"Se ah modificado la estación con exito!!!\");"
                stationID = request.POST["nameMonitoringPlace"]
            else:
                savedMonitoringStation = MonitoringStation.objects.get(pk=request.POST["nameMonitoringPlace"]).delete()
                monitoringStationForm = generateMonitoringStationFormAddOrModify(False)()
                alertSaved = "alert(\"Se ah borrado la estación con exito!!!\");"
                stationID = 1
            jsonStation = generateJsonStationModifyView()
            return render(request, 'administracionScazac/monitoringStation.djhtml',
                      {'monitoringStationForm':monitoringStationForm,
                       'keyGoogleMap':mapSettings.googleAPIKey,
                       'centerLatitude':mapSettings.centerLatitude,
                       'centerLength':mapSettings.centerLength,
                       'zoom':mapSettings.zoom,
                       'titulo': MonitoringStationViewModify.title,
                       'stationID':stationID,
                       'alertSaved':alertSaved,
                       'jsonStation':json.dumps(jsonStation),
                       'alertForErase': alertForErase,
                       'isAdd':False}) # Because allways the first station will be showed.
           
        else:
            return render(request, 'administracionScazac/monitoringStation.djhtml',
                      {'monitoringStationForm':monitoringStationForm,
                       'keyGoogleMap':mapSettings.googleAPIKey,
                       'centerLatitude':mapSettings.centerLatitude,
                       'centerLength':mapSettings.centerLength,
                       'zoom':mapSettings.zoom,
                       'titulo': MonitoringStationViewModify.title,
                       'stationID':request.POST["nameMonitoringPlace"],
                       'alertForErase': alertForErase,
                       'isAdd':False})

class MonitoringDataViewAdd(TemplateView):
    """View for the requirment F3-4"""
    def get(self, request):
        """Initial view"""
        if not(request.user.is_superuser):
            raise PermissionDenied
        dataForm = generateMonitoringDataForm()
        return render(request, 'administracionScazac/monitoringData.djhtml',{'dataForm': dataForm,
                                                                             'title':"Subir datos de calidad del aire"})
    def post(self, request):
        """Where the file is uploaded"""
        if not(request.user.is_superuser):
            raise PermissionDenied
        dataForm = generateMonitoringDataForm()(request.POST, request.FILES)
        if dataForm.is_valid():
            # Test the type
            name = request.FILES['archivoCSV'].name
            if not(name.endswith('.csv')):
                return render(request, 'administracionScazac/monitoringData.djhtml',{'dataForm': dataForm,
                                                                             'title':"El archivo no es CSV."})
            # Test if pandas can open the file
            #try:
            data = pandas.read_csv(request.FILES['archivoCSV'], low_memory=False)
            #except:
             #   return render(request, 'administracionScazac/monitoringData.djhtml',{'dataForm': dataForm,
                                                                                    # 'title':"El archivo no es CSV."})
            
            # Test if the file contains all the columns    
            try:
                test = data["Temp"][0]
                test = data["O3"][0]
                test = data["CO"][0]
                test = data["NO"][0]
                test = data["NO2"][0]
                test = data["NOX"][0]
                test = data["SO2"][0]
                test = data["TempAmbiente"][0]
                test = data["RH"][0]
                test = data["WS"][0]
                test = data["WD"][0]
                test = data["PresionBaro"][0]
                test = data["RadSolar"][0]
                test = data["Precipitacion"][0]
                test = data["PM10"][0]
                test = data["PM2.5"][0]
            except:
                return render(request, 'administracionScazac/monitoringData.djhtml',{'dataForm': dataForm,
                                                                             'title':"El archivo no contiene las columnas solicitadas"})
            monitoringStation = MonitoringStation.objects.get(pk=dataForm.cleaned_data['nameMonitoringPlace'])
            try:
                oldDate, newDate = saveMonitoringData(data, monitoringStation)
                saveImecaDataHour(monitoringStation, oldDate, newDate)
                saveImecaDataDay(monitoringStation, oldDate, newDate)
                saveImecaDataMonth(monitoringStation, oldDate, newDate)
                monitoringStation.dateOldestRegister = MonitoringData.objects.filter(idStation__pk=dataForm.cleaned_data['nameMonitoringPlace']).order_by('fecha')[0].fecha.date()
                monitoringStation.dateNewestRegister = MonitoringData.objects.filter(idStation__pk=dataForm.cleaned_data['nameMonitoringPlace']).order_by('-fecha')[0].fecha.date()
                monitoringStation.save()
            except:
                return render(request, 'administracionScazac/monitoringData.djhtml',{'dataForm': dataForm,
                                                                                 'title':"Datos ya existentes. Elimine los datos que desea reemplazar."})
            return render(request, 'administracionScazac/monitoringData.djhtml',{'dataForm': dataForm,
                                                                                 'title':"Subir datos de calidad del aire",
                                                                                 'alertSaved': "alert(\"Se guardaron los datos en la estación de forma exitosa!!!\");"})
        else:
            return render(request, 'administracionScazac/monitoringData.djhtml',{'dataForm': dataForm,
                                                                                 'title':"Subir datos de calidad del aire"})


class MonitoringDataViewDelete(TemplateView):
    """Requirment F3-4 *Delate*"""
    def get(self, request):
        """Initial view"""
        if not(request.user.is_superuser):
            raise PermissionDenied
        dataForm = generateMonitoringDataFormDelete()()
        return render(request, 'administracionScazac/monitoringDataDelete.djhtml',{'dataForm': dataForm,
                                                                                 'title':"Eliminar datos de calidad del aire"})
    def post(self, request):
        """Procesing function"""
        if not(request.user.is_superuser):
            raise PermissionDenied
        dataForm = generateMonitoringDataFormDelete()(request.POST)
        if dataForm.is_valid():
            if dataForm.cleaned_data['initialDate'] > dataForm.cleaned_data['finalDate']:
                return render(request, 'administracionScazac/monitoringDataDelete.djhtml',{'dataForm': dataForm,
                                                                                           'title':"La fecha inicial debe de ser menor que la final"})
            elif dataForm.cleaned_data['initialDate'] == dataForm.cleaned_data['finalDate']:
                MonitoringData.objects.filter(idStation__pk=request.POST['nameMonitoringPlace']).filter(fecha__icontains=dataForm.cleaned_data['initialDate'])
                ImecaDataHour.objects.filter(idStation__pk=request.POST['nameMonitoringPlace']).filter(fecha__icontains=dataForm.cleaned_data['initialDate'])
                ImecaDataDay.objects.filter(idStation__pk=request.POST['nameMonitoringPlace']).filter(fecha__initial=dataForm.cleaned_data['initialDate'])
                ImecaDataMonth.objects.filter(idStation__pk=request.POST['nameMonitoringPlace']).filter(fecha__icontains=dataForm.cleaned_data['initialDate'])
                saveImecaDataMonth(request.POST['nameMonitoringPlace'], dataForm.cleaned_data['initialDate'], dataForm.cleaned_data['initialDate'])
                return render(request, 'administracionScazac/monitoringDataDelete.djhtml',{'dataForm': dataForm,
                                                                                           'title':"Eliminar datos de calidad del aire",
                                                                                           'alertDelete':"alert(\"Se ah borrado la estación con exito!!!\");"})
            
            MonitoringData.objects.filter(idStation__pk=request.POST['nameMonitoringPlace']).filter(fecha__gte=dataForm.cleaned_data['initialDate']).filter(fecha__lte=dataForm.cleaned_data['finalDate'])
            ImecaDataHour.objects.filter(idStation__pk=request.POST['nameMonitoringPlace']).filter(fecha__gte=dataForm.cleaned_data['initialDate']).filter(fecha__lte=dataForm.cleaned_data['finalDate'])
            ImecaDataDay.objects.filter(idStation__pk=request.POST['nameMonitoringPlace']).filter(fecha__gte=dataForm.cleaned_data['initialDate']).filter(fecha__lte=dataForm.cleaned_data['finalDate'])
            ImecaDataMonth.objects.filter(idStation__pk=request.POST['nameMonitoringPlace']).filter(fecha__gte=dataForm.cleaned_data['initialDate']).filter(fecha__lte=dataForm.cleaned_data['finalDate'])
            saveImecaDataMonth(request.POST['nameMonitoringPlace'], dataForm.cleaned_data['initialDate'], dataForm.cleaned_data['finalDate'])
            return render(request, 'administracionScazac/monitoringDataDelete.djhtml',{'dataForm': dataForm,
                                                                                           'title':"Eliminar datos de calidad del aire",
                                                                                           'alertDelete':"alert(\"Se ah borrado la estación con exito!!!\");"})
        else:
            return render(request, 'administracionScazac/monitoringDataDelete.djhtml',{'dataForm': dataForm,
                                                                                       'title':"Eliminar datos de calidad del aire"})
            

        
def generateMonitoringDataForm():
    """If is on the form file, it does not load all the new geneerated monitoring stations."""
    class MonitoringDataFormAdd(forms.Form):
        """Form for the requierment F3-4"""
        nameMonitoringPlace = forms.ChoiceField(label="Estación de monitoreo.", help_text="Estación de monitoreo a la cual se le asignaran los datos.", choices=tuple((station.serialNumber, station.nameMonitoringPlace) for station in MonitoringStation.objects.all()))
        archivoCSV = forms.FileField(label="Subir archivo con datos.",  help_text="Subir archivos a la estación de monitoreo correspondiente. Archivo máximo de 70 MB. Se deben de tener las siguientes columnas: Temp, O3, CO, NO, NO2, NOX, SO2, TempAmbiente, RH, WS, WD, PresionBaro, RadSolar, Precipitacion, PM10, PM2.5. Si la estación de monitoreo no incluyo datos de una columna en especifico (excepto Fecha), favor de incluir como a la columna con un unico dato con el contenido de None." , max_length=70)
    return MonitoringDataFormAdd

def generateMonitoringDataFormDelete():
    """If is on the form file, it does not load all the new geneerated monitoring stations."""
    class MonitoringDataFormDelete(forms.Form):
        """Form for the requierment F3-4"""
        nameMonitoringPlace = forms.ChoiceField(label="Estación de monitoreo.", help_text="Estación de monitoreo a la cual se le borraran los datos.", choices=tuple((station.serialNumber, station.nameMonitoringPlace) for station in MonitoringStation.objects.all()))
        initialDate = forms.DateField(label="Fecha del primer registro",help_text="Ingrese una fecha apartir de donde se eliminaran datos. (2006-10-25)", error_messages={'required':"Se necesita que ingrese una fecha de inicio!" , 'invalid':"Ingrese una fecha valida!"}, input_formats=['%Y-%m-%d'] ) # Modified 20171001: Only on type of date will be accepted to reduce complexity converting to type date
        finalDate = forms.DateField(label="Fecha del ultimo registro",help_text="Ingrese una fecha de donde se termine de eliminar datos.(2006-10-25)", error_messages={'required':"Se necesita que ingrese una fecha de inicio!" , 'invalid':"Ingrese una fecha valida!"}, input_formats=['%Y-%m-%d'])
    return MonitoringDataFormDelete

def generateMonitoringStationFormAddOrModify(isAdd):
    """Be able to have call only once the definition of the form."""
    if isAdd:
        class MonitoringStationForm(forms.Form):
            """Form for the requirment F3-3"""
            nameMonitoringPlace = forms.CharField(label="Nombre del lugar que se monitorea.", help_text="El lugar donde se localiza la estación de monitoreo.", max_length=125)
            latitude = forms.DecimalField(label="Latitud", help_text="Latitud con la que se posiciona la estación de monitoreo.", max_digits=10, decimal_places=7, max_value=Decimal(90), min_value=Decimal(-90))
            length = forms.DecimalField(label="Longitud", help_text="Longitud con la que se posiciona la estación de monitoreo.", max_digits=10, decimal_places=7, max_value=Decimal(180), min_value=Decimal(-180))
            monitoringRadius = forms.DecimalField(label="Radio de monitoreo", help_text="Que tanto terreno la estación de monitoreo puede monitorear. (En metros)", max_digits=10, decimal_places=2)
    else:
        class MonitoringStationForm(forms.Form):
            """Form for the requirment F3-3"""
            nameMonitoringPlace = forms.ChoiceField(label="Nombre del lugar que se monitorea.", help_text="El lugar donde se localiza la estación de monitoreo.", choices=tuple((station.serialNumber, station.nameMonitoringPlace) for station in MonitoringStation.objects.all()))
            latitude = forms.DecimalField(label="Latitud", help_text="Latitud con la que se posiciona la estación de monitoreo.", max_digits=10, decimal_places=7, max_value=Decimal(90), min_value=Decimal(-90))
            length = forms.DecimalField(label="Longitud", help_text="Longitud con la que se posiciona la estación de monitoreo.", max_digits=10, decimal_places=7, max_value=Decimal(180), min_value=Decimal(-180))
            monitoringRadius = forms.DecimalField(label="Radio de monitoreo", help_text="Que tanto terreno la estación de monitoreo puede monitorear. (En metros)", max_digits=10, decimal_places=2)
            
    return MonitoringStationForm    
    
def generateJsonStationModifyView():
    """Generate Json data to be parsed on the Modify view. 
    Will be used o both post and get function."""
    jsonStation = {}
    allStations = MonitoringStation.objects.all()
    for station in allStations:
        jsonStation[station.serialNumber] = {'nameMonitoringPlace':station.nameMonitoringPlace, 'latitude':float(station.latitude), 'length':float(station.length), 'monitoringRadius':float(station.monitoringRadius)}
    return jsonStation

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
    return old,  new 

def saveMonitoringData(data, monitoringStation):
    """First save the raw data, calculate raw IMECA data, then the avarage IMECA for hours, days and month. Returns the oldest an newest date respectible."""
    sizeData = len(data["Fecha"])
    if "nulo" == data["Temp"][0]:
        temp = None
    else:
        temp = 1
    if data["O3"][0] == "nulo":
        o3 = None
    else:
        o3 = 1
    if "nulo" == data["CO"][0]:
        co = None
    else:
        co = 1
    if "nulo" == data["NO"][0]:
        no = None
    else:
        no = 1
    if "nulo" == data["NO2"][0]:
        no2 = None
    else:
        no2 = 1
    if "nulo" == data["NOX"][0]:
        nox = None
    else:
        nox = 1
    if "nulo" == data["SO2"][0]:
        so2 = None
    else:
        so2 = 1
    if "nulo" == data["TempAmbiente"][0]:
        tempAmb = None
    else:
        tempAmb = 1
    if "nulo" == data["RH"][0]:
        rh = None
    if "nulo" == data["WS"][0]:
        ws = None
    else:
        ws = 1
    if "nulo" == data["WD"][0]:
        wd = None
    else:
        wd = 1
    if "nulo" == data["PresionBaro"][0]:
        presBaro = None
    else:
        presBaro = 1
    if "nulo" == data["RadSolar"][0]:
        radSolar = None
    else:
        radSolar = 1
    if "nulo" == data["Precipitacion"][0]:
        precip = None
    else:
        precip = 1
    if "nulo" == data["PM10"][0]:
        pm10 = None
    else:
        pm10 = 1
    if "nulo" == data["PM2.5"][0]:
        pm25 = None
    else:
        pm25 = 1
                
    for i in range(0, sizeData):
        pollant = MonitoringData()
        pollant.idStation = monitoringStation
        pollant.fecha = dateutil.parser.parse(data["Fecha"][i])
        try:
            temp = temp * 1
            pollant.temperatura = data["Temp"][i]
        except:
            pollant.temperatura = None
        try:
            o3 = o3 * 1
            pollant.o3 = data["O3"][i]
            pollant.imecaO3 = imecaO3(data["O3"][i])
        except:
            pollant.o3 = None
            pollant.imecaO3 = None
        try:
            co = co * 1
            pollant.co = data["CO"][i]
            pollant.imecaCO = imecaCO(data["CO"][i])
        except:
            pollant.co = None
            pollant.imecaCO = None
        try:
            no = no * 1
            pollant.no = data["NO"][i]
            pollant.imecaNO = imecaNO(data["NO"][i])
        except:
            pollant.no = None
            pollant.imecaNO = None
        try:
            no2 = no2 * 1
            pollant.no2 = data["NO2"][i]
            pollant.imecaNO2 = imecaNO(data["NO2"][i])
        except:
            pollant.no2 = None
            pollant.imecaNO2 = None
        try:
            nox = nox * 1 
            pollant.nox = data["NOX"][i]
            pollant.imecaNOX = imecaNO(data["NOX"][i])
        except:
            pollant.nox = None
            pollant.imecaNOX = None
        try:
            so2 = so2 * 1
            pollant.so2 = data["SO2"][i]
            pollant.imecaSO2 = imecaSO2(data["SO2"][i])
        except:
            pollant.so2 = None
            pollant.imecaSO2 = None
        try:
            tempAmb = tempAmb * 1
            pollant.temperaturaAmbiente = data["TempAmbiente"][i]
        except:
            pollant.temperaturaAmbiente = None
        try:
            rh = rh * 1
            pollant.humedadRelativa = data["RH"][i]
        except:
            pollant.humedadRelativa = None
        try:
            ws = ws * 1
            pollant.ws = data["WS"][i]
        except:
            pollant.ws = None
        try:
            wd = wd * 1
            pollant.wd = data["WD"][i]
        except:
            pollant.wd = None
        try:
            presBaro = presBaro * 1    
            pollant.presionBarometrica = data["PresionBaro"][i]
        except:
            pollant.presionBarometrica = None
        try:
            radSolar = radSolar * 1    
            pollant.radiacionSolar = data["RadSolar"][i]
        except:
            pollant.radiacionSolar = None
        try:
            precip = precip * 1    
            pollant.precipitacion = data["Precipitacion"][i]
        except:
            pollant.precipitacion = None
        try:
            pm10 = pm10 * 1
            pollant.pm10 = data["PM10"][i]
            pollant.imecaPM10 = imecaPM10(data["PM10"][i])
        except:
            pollant.pm10 = None
            pollant.imecaPM10 = None
        try:
            pm25 = pm25 * 1
            pollant.pm25 = data["PM2.5"][i]
            pollant.imecaPM25 = imecaPM25(data["PM2.5"][i])
        except:
            pollant.pm25 = None
            pollant.imecaPM25 = None
        
        pollant.save()
        print pollant.imecaO3
    return newstOldestDate(data["Fecha"])

def saveImecaDataHour(station, oldDate, newDate):
    """"""
    pollantHour = dateutil.parser.parse(str(oldDate.year) + "-" + number2ZeroBeforeDigit(oldDate.month) + "-" + number2ZeroBeforeDigit(oldDate.day) + " 00" )
    # Making sure that the query will compare only the year and month
    pollantHourString = str(pollantHour.year) + "-" + number2ZeroBeforeDigit(pollantHour.month) + "-" + number2ZeroBeforeDigit(pollantHour.day) + " " + number2ZeroBeforeDigit(pollantHour.hour)
    pollantHourData = MonitoringData.objects.filter(fecha__icontains=pollantHourString).filter(idStation__pk=station.serialNumber).values_list('imecaO3', 'imecaNO', 'imecaNO2', 'imecaNOX', 'imecaSO2', 'imecaCO', 'imecaPM10', 'imecaPM25')

    # Convert newDate to a DateTime type
    stationDateTimeNewestRegister = dateutil.parser.parse(str(newDate.year) + "-" + number2ZeroBeforeDigit(newDate.month) + "-" + number2ZeroBeforeDigit(newDate.day) + " 23" )
    # 
    while pollantHour <= stationDateTimeNewestRegister:
        
        monthImecas = ImecaDataHour()
        pollantHourDataSize = len(pollantHourData)
        
        if not(pollantHourDataSize == 0):
            # Save the data on the system
            print pollantHourString
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
            pollantHourData = MonitoringData.objects.filter(fecha__icontains=pollantHourString).filter(idStation__pk=station.serialNumber).values_list('imecaO3', 'imecaNO', 'imecaNO2', 'imecaNOX', 'imecaSO2', 'imecaCO', 'imecaPM10', 'imecaPM25')
        else:
            pollantHour += datetime.timedelta(hours=1)
            pollantHourString = str(pollantHour.year) + "-" + number2ZeroBeforeDigit(pollantHour.month) + "-" + number2ZeroBeforeDigit(pollantHour.day) + " " + number2ZeroBeforeDigit(pollantHour.hour)
            pollantHourData = MonitoringData.objects.filter(fecha__icontains=pollantHourString).filter(idStation__pk=station.serialNumber).values_list('imecaO3', 'imecaNO', 'imecaNO2', 'imecaNOX', 'imecaSO2', 'imecaCO', 'imecaPM10', 'imecaPM25')


def saveImecaDataDay(station, oldDate, newDate):
    """"""
    pollantDay = oldDate
    pollantDayData = ImecaDataHour.objects.filter(fecha__icontains=pollantDay).filter(idStation__pk=station.serialNumber).values_list('imecaO3', 'imecaNO', 'imecaNO2', 'imecaNOX', 'imecaSO2', 'imecaCO', 'imecaPM10', 'imecaPM25')
    
    
    while pollantDay <= newDate:
        
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
            pollantDayData = ImecaDataHour.objects.filter(fecha__icontains=pollantDay).filter(idStation__pk=station.serialNumber).values_list('imecaO3', 'imecaNO', 'imecaNO2', 'imecaNOX', 'imecaSO2', 'imecaCO', 'imecaPM10', 'imecaPM25')
        else:
            # Just continue whit the next day
            pollantDay += datetime.timedelta(days=1)
            pollantDayData = ImecaDataHour.objects.filter(fecha__icontains=pollantDay).filter(idStation__pk=station.serialNumber).values_list('imecaO3', 'imecaNO', 'imecaNO2', 'imecaNOX', 'imecaSO2', 'imecaCO', 'imecaPM10', 'imecaPM25')


def saveImecaDataMonth(station, oldDate, newDate):
    """"""
    # Put the oldest month of monitoring 
    pollantMonth = dateutil.parser.parse(str(oldDate.year) + "-" + number2ZeroBeforeDigit(oldDate.month) + "-" + "01").date()
    # Making sure that the query will compare only the year and month
    pollantMonthString = str(pollantMonth.year) + "-" + number2ZeroBeforeDigit(pollantMonth.month)
    pollantMonthData = ImecaDataDay.objects.filter(fecha__icontains=pollantMonthString).filter(idStation__pk=station.serialNumber).values_list('imecaO3', 'imecaNO', 'imecaNO2', 'imecaNOX', 'imecaSO2', 'imecaCO', 'imecaPM10', 'imecaPM25')
    
    # 
    while pollantMonth <= newDate.date():
        
        monthImecas = ImecaDataMonth()
        pollantMonthDataSize = len(pollantMonthData)
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
            pollantMonthData = ImecaDataDay.objects.filter(fecha__icontains=pollantMonthString).filter(idStation__pk=station.serialNumber).values_list('imecaO3', 'imecaNO', 'imecaNO2', 'imecaNOX', 'imecaSO2', 'imecaCO', 'imecaPM10', 'imecaPM25')
        else:
            # Just continue whit the next month
            if pollantMonth.month < 12:
                pollantMonth = pollantMonth.replace(month=pollantMonth.month + 1)
            else:
                pollantMonth = pollantMonth.replace(month=1, year=pollantMonth.year + 1)
            pollantMonthString = str(pollantMonth.year) + "-" + number2ZeroBeforeDigit(pollantMonth.month)
            pollantMonthData = ImecaDataDay.objects.filter(fecha__icontains=pollantMonthString).filter(idStation__pk=station.serialNumber).values_list('imecaO3', 'imecaNO', 'imecaNO2', 'imecaNOX', 'imecaSO2', 'imecaCO', 'imecaPM10', 'imecaPM25')



def imecaMean(monitoringStation, sizeData): 
    """Determines the mean of each IMECA. If the IMECA does contains information. Pollant data is on this orden as folows: o3, no, no2, nox, so2, co, pm10, pm25"""
    imecas = [0 for i in range(0, 8)]

    for imeca in monitoringStation:
        try:
            imecas[0] += imeca[0]
        except:
            imecas[0] = None

        try:
            imecas[1] += imeca[1]
        except:
            imecas[1] = None
        try:
            imecas[2] += imeca[2]
        except:
            imecas[2] = None
        try:
            imecas[3] += imeca[3]
        except:
            imecas[3] = None
        try:
            imecas[4] += imeca[4]
        except:
            imecas[4] = None
        try:
            imecas[5] += imeca[5]
        except:
            imecas[5] = None
        try:
            imecas[6] += imeca[6]
        except:
            imecas[6] = None
        try:
            imecas[7] += imeca[7]
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

def number2ZeroBeforeDigit(number):
        """Returns a the digit whit a zero before if the number it is below 10"""
        if number < 10:
            return "0" + str(number)
        else:
            return str(number)
