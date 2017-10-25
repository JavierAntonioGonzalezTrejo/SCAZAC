# -*- coding: utf-8 -*-
# Modified 20170930: Added the requirment F2-3
# Modified 20141003: Save of a generated graph
from __future__ import unicode_literals
import os                       # Remove the Graphs photos from harddisk
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django import forms        # Added 20171001 Make 
from investigacion.models import MonitoringStation, MonitoringData, GraphsRecord
from investigacion.forms import GraphsForm, NormForm
from django.views.generic import TemplateView
from bokeh.plotting import figure, ColumnDataSource
from bokeh.embed import components
from bokeh.models import HoverTool
from bokeh.io import export_png # Added 20171002
import dateutil.parser
import numpy
from math import isnan
from scipy.stats import pearsonr, linregress
from functools import reduce
import datetime                 # Added 20171001: Time for the requirment F2-04
import json                    # Added 20171001: To send information to the javascript side
import cStringIO as StringIO   # Added 20171003; Generate on memory the pdf reports.
from tex import latex2pdf
GRAPHSDIR = settings.PROJECT_ROOT + "/static/graphsFolder/" # Added 2017103 directory where the graphs will be saved
class Principal(TemplateView):
    """Class that holds the requirment F2-3"""
    dataModel = MonitoringData
    M = 6                       # M value nesesary to remove graphs outliners
    

    def get(self, request):
        """Initial Function"""
        
        station = MonitoringStation.objects.all()[0]
        formInitialValues = { 'graph_type':"1", 'airMeasureY':"1", 'airMeasureX':"0", 'initialDate':str(station.dateNewestRegister), 'finalDate':str(station.dateNewestRegister),'monitoringStation':str(station.serialNumber), 'glyph_type':"2",'name':"Grafica de Prueba"}
        graphForm = GraphsForm(formInitialValues)
        
        plot, std_err, statistics = createAGraph(formInitialValues)
        script, div = components(plot)
        
        return render(request, "investigacion/homepage.djhtml",
                      {'graphForm': graphForm,
                       "the_script":script,
                       "the_div":div,
                       "mean":statistics[0],
                       "median":statistics[1],
                       "std":statistics[2],
                       "var":statistics[3],
                       "corrcoef":statistics[4][0],
                       "max":statistics[5],
                       "min":statistics[6],
                       "std_err":std_err})
    
    def post(self, request):
        """Function that recives the petitions to graph"""
        graphForm = GraphsForm(request.POST)
        
        if graphForm.is_valid():
            save_function = ""
            plot, std_err, statisticsData = createAGraph(request.POST)
            if plot == 2:
                return render(request, "investigacion/homepage.djhtml",{'graphForm': graphForm, 'the_div': "<h1>NO SE ENCONTRO NINGUN REGISTRO CON LAS FECHAS ESPESIFICADAS!</h1>"})
            elif plot == 1:
                return render(request, "investigacion/homepage.djhtml",
                              {'graphForm': graphForm,
                               'the_div': "<h1>LA FECHA INICIAL DEBE DEL PRIMER REGISTRO DEBE DE SER MENOR QUE LA DEL ULTIMO REGISTRO!</h1>"})
            script, div = components(plot)
            
            if 'save_graph' in request.POST:
                total_Graphs = GraphsRecord.objects.filter(author=request.user)
                if len(total_Graphs) > 200:
                    save_function = "alert(\"Exedio el limite de 200 graficas, borre una antes de continuar!!!!\");"
                else:
                    save_function = "alert(\"La grafica se ha guardado con exito.!!!!\");"
                    newGraph = GraphsRecord()
                    newGraph.author = request.user
                    if "name" in request.POST:
                        newGraph.name = request.POST["name"]
                    newGraph.date = datetime.datetime.now()
                    newGraph.graph_type = int(request.POST["graph_type"])
                    newGraph.airMeasureY = int(request.POST["airMeasureY"])
                    newGraph.airMeasureX = int(request.POST["airMeasureX"])
                    newGraph.initialDate =  datetime.datetime.strptime(request.POST["initialDate"], '%Y-%m-%d').date()
                    newGraph.finalDate =  datetime.datetime.strptime(request.POST["finalDate"], '%Y-%m-%d').date()
                    newGraph.monitoringStation = MonitoringStation.objects.get(pk=request.POST["monitoringStation"])
                    newGraph.glyph_type = int(request.POST["glyph_type"])
                    newGraph.eliminate_error_sampling = "eliminate_error_sampling" in request.POST
                    newGraph.script = script
                    newGraph.div = div
                    newGraph.photo = str(request.user.id) + datetime.datetime.now().strftime("%Y%M%d%H%M%S%f") +".png" # Not saving the root makes the database more suitable to transfer between servers: Error corrected, used strftime to eliminate the point which latex wrongly ses as another formar diferent from a png
                    photoPath =  GRAPHSDIR + newGraph.photo
                    print (export_png(plot, filename=photoPath))
                    newGraph.mean = statisticsData[0]
                    newGraph.median = statisticsData[1]
                    newGraph.std = statisticsData[2]
                    newGraph.vari = statisticsData[3]
                    newGraph.corrcoef = statisticsData[4][0]
                    newGraph.maxValue = statisticsData[5]
                    newGraph.minValue = statisticsData[6]
                    if isinstance(std_err, float):
                        newGraph.std_err = std_err
                    newGraph.save()
                    

            return render(request, "investigacion/homepage.djhtml",
                          {'graphForm': graphForm,
                           "the_script":script,
                           "the_div":div,
                           "mean":statisticsData[0],
                           "median":statisticsData[1],
                           "std":statisticsData[2],
                           "var":statisticsData[3],
                           "corrcoef":statisticsData[4][0],
                           "max":statisticsData[5],
                           "min":statisticsData[6],
                           "std_err": std_err,
                           "save_function":save_function})
        return render(request, "investigacion/homepage.djhtml",
                          {'graphForm': graphForm})


class GraphsRecordView(TemplateView):
    """Part of the requirment F2-4"""
            
    def get(self, request):
        """Show all the information regarding the saved graphs from a particular user"""
        
        userGraphs = GraphsRecord.objects.filter(author__pk=request.user.id)
        # Send the description to a JavaScript program to show it on the webpage
        descriptionGraphs = { graph.id:jsonDescriptionGraphs(graph) for graph in userGraphs}
        HistoryForm = defineFormHistoryForm(userGraphs)
        form = HistoryForm()
        return render(request, "investigacion/history.djhtml",
                      {"historyForm": form,
                       "descriptionGraphs":json.dumps(descriptionGraphs)})
        
    def post(self, request):
        """Returns depending on the input given by the user"""
        # Send the description to a JavaScript program to show it on the webpage
        
        userGraphs = GraphsRecord.objects.filter(author__pk=request.user.id)
        # Send the description to a JavaScript program to show it on the webpage
        descriptionGraphs = { graph.id:jsonDescriptionGraphs(graph) for graph in userGraphs}
        HistoryForm = defineFormHistoryForm(userGraphs)
        form = HistoryForm(request.POST)
        if form.is_valid():

            # Graph an the first selection.
            if request.POST["actionHistory"] == "1":
                # The Form do not requir a graphs selected so in case non is selected an alert appers
                if not("graphsUser" in request.POST):
                    delateAlert = "alert(\"No se selecciono ninguna grafica!!!\");"
                    return render(request, "investigacion/history.djhtml",
                        {"historyForm": form,
                         "descriptionGraphs":json.dumps(descriptionGraphs),
                         "delateAlert":delateAlert})
                graph = GraphsRecord.objects.filter(author__pk=request.user.id).get(pk=request.POST["graphsUser"])
                graphForm = GraphsForm({ 'graph_type':str(graph.graph_type), 'airMeasureY':str(graph.airMeasureY), 'airMeasureX':str(graph.airMeasureX), 'initialDate':str(graph.initialDate), 'finalDate':str(graph.finalDate),'monitoringStation':str(graph.monitoringStation.serialNumber), 'glyph_type':str(graph.glyph_type),'name':graph.name, 'eliminate_error_sampling':graph.eliminate_error_sampling}
                )
                return render(request, "investigacion/homepage.djhtml",
                          {'graphForm': graphForm,
                           "the_script":graph.script,
                           "the_div":graph.div,
                           "mean":graph.mean,
                           "median":graph.median,
                           "std":graph.std,
                           "var":graph.vari,
                           "corrcoef":graph.corrcoef,
                           "max":graph.maxValue,
                           "min":graph.minValue,
                           "std_err": graph.std_err})
            elif request.POST["actionHistory"] == "2":
                if not("graphsUser" in request.POST):
                    delateAlert = "alert(\"No se selecciono ninguna grafica!!!\");"
                    return render(request, "investigacion/history.djhtml",
                        {"historyForm": form,
                         "descriptionGraphs":json.dumps(descriptionGraphs),
                         "delateAlert":delateAlert})
                eliminateARegister(GraphsRecord, form.cleaned_data["graphsUser"])
                remainingGraphs = GraphsRecord.objects.filter(author__pk=request.user.id)
                formGraph = defineFormHistoryForm(remainingGraphs)
                form = formGraph()
                delateAlert = "alert(\"Se han eliminado existosamente las graficas!!!\");"
                return render(request, "investigacion/history.djhtml",
                        {"historyForm": form,
                         "descriptionGraphs":json.dumps(descriptionGraphs),
                         "delateAlert":delateAlert})
            elif request.POST["actionHistory"] == "3":
                if not("graphsUser" in request.POST):
                    delateAlert = "alert(\"No se selecciono ninguna grafica!!!\");"
                    return render(request, "investigacion/history.djhtml",
                        {"historyForm": form,
                         "descriptionGraphs":json.dumps(descriptionGraphs),
                         "delateAlert":delateAlert})
                
                
                userGraphs = GraphsRecord.objects.filter(name__icontains=request.POST["name"]).filter(date__icontains=request.POST["initialDate"]).values_list('id', flat=True)
                userGraphs = [id for id in userGraphs]
                form = HistoryForm({"graphsUser":userGraphs, "name":request.POST["name"], "initialDate":request.POST["initialDate"]})
                
                delateAlert = "alert(\"Si se encontraron coincidencias, se mostraran remarcadas en la forma.\");"
                return render(request, "investigacion/history.djhtml",
                        {"historyForm": form,
                         "descriptionGraphs":json.dumps(descriptionGraphs),
                         "delateAlert":delateAlert})
            
            elif request.POST["actionHistory"] == "4":
                if not("graphsUser" in request.POST):
                    delateAlert = "alert(\"No se selecciono ninguna grafica!!!\");"
                    return render(request, "investigacion/history.djhtml",
                        {"historyForm": form,
                         "descriptionGraphs":json.dumps(descriptionGraphs),
                         "delateAlert":delateAlert})
                report = StringIO.StringIO()
                report.write(generateGraphReport(form.cleaned_data["graphsUser"]))
                report.seek(0)  # Rewind the pointer to the beggining of the file
                response = HttpResponse(report.getvalue(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename=report' + str(datetime.datetime.now()) + '.pdf'
        
                return response
        else:
            return render(request, "investigacion/history.djhtml",
                        {"historyForm": form,
                         "descriptionGraphs":json.dumps(descriptionGraphs)})
        

class NormativityView(TemplateView): # Added 20171001 Requirment F2-5
    """Function View for the normativity of the pollants infesting the monitored station areas"""

    def get(self, request):
        """Initial Function"""
        normForm = NormForm()
        
        return render(request, "investigacion/norm.djhtml",
                          {"normForm":normForm})
        
        return render(request, "investigacion/norm.djhtml",
                      {"normForm":normForm})
    def post(self, request):
        """Function that recives all the POST pettions"""
        normForm = NormForm(request.POST)
        if normForm.is_valid():
            normListData = normByStation(MonitoringStation.objects.get(pk=request.POST["monitoringStation"]))
            return render(request, "investigacion/norm.djhtml",
                          {"normForm":normForm,
                           "normListData":normListData})
        return render(request, "investigacion/norm.djhtml",
                          {"normForm":normForm})

def normByStation(station):     # Added 20171001
    """station: MonitoringStation Object. Generates a list consisting of 8 means of 1 to 8 hours intervals depending on the pollant over an avarage of the previus 6 monitored months of the given station which firt value is the name of the monitored place."""
    meanStationList = []
    last6MonthInitialDate = monthdelta(station.dateNewestRegister, -6)
    #######################################
    meanStationList.append(helperNormMean(last6MonthInitialDate,station.dateNewestRegister,GraphsRecord.O3_AIRMEASURE ,station.serialNumber, 8))
    
    meanStationList.append(helperNormMean(last6MonthInitialDate,station.dateNewestRegister,GraphsRecord.CO_AIRMEASURE ,station.serialNumber, 8))

    meanStationList.append(helperNormMean(last6MonthInitialDate,station.dateNewestRegister,GraphsRecord.NO_AIRMEASURE ,station.serialNumber, 1))

    meanStationList.append(helperNormMean(last6MonthInitialDate,station.dateNewestRegister,GraphsRecord.NO2_AIRMEASURE ,station.serialNumber, 1))
    
    meanStationList.append(helperNormMean(last6MonthInitialDate,station.dateNewestRegister,GraphsRecord.NOX_AIRMEASURE ,station.serialNumber, 1))

    # Do not pass over 0,110 ppm over 24 hours
    meanStationList.append(helperNormMean(last6MonthInitialDate,station.dateNewestRegister,GraphsRecord.SO2_AIRMEASURE ,station.serialNumber, 24))

    meanStationList.append(helperNormMean(last6MonthInitialDate,station.dateNewestRegister,GraphsRecord.PM10_AIRMEASURE ,station.serialNumber, 24))
    # Do not over pass 65
    
    meanStationList.append(helperNormMean(last6MonthInitialDate,station.dateNewestRegister,GraphsRecord.PM25_AIRMEASURE ,station.serialNumber, 24)) 
    

    return meanStationList

def helperNormMean(last6MonthInitialDate,dateNewestRegister,pollant,serialNumber, hour):
    """Helper function that wraps 3 preduceres on one. Returns the output of normByElement"""
    bufferList = setListElement(last6MonthInitialDate,dateNewestRegister,pollant ,serialNumber)
    outlierFunc = defineReject_outliers(bufferList, 6)
    return normByElement(reduce(outlierFunc, bufferList, []), hour)
    
def normByElement(listElement, hours):
    """elementList: A list consisted by values of the corresponging elements (Each value represents a 5 minutes of monitoring activitie on the station), hours: how much data will be taken to produce a mean (1 hour=12recordings). Returns a mean value corresponding to the given hour interval. """
    numberOfMeasurments = (hours * 60) / 5
    meanList = []
    for i in range(len(listElement)):
        meanList.append(numpy.mean(listElement[i:i+hours]))
    return numpy.mean(meanList)

def statisticsValues(dataY, dataX):
    """Obtain the mean, median, std, var, corrcoef, max and min of the selected data on this order"""
    if len(dataY) == 0:
        return ("Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos", "Sin Datos")
    return (numpy.nanmean(dataY), numpy.nanmedian(dataY), numpy.nanstd(dataY), numpy.nanvar(dataY), pearsonr(dataY, dataX), numpy.nanmax(dataY), numpy.nanmin(dataY))

# Provided by Benjamin Bannierstack overflow
def defineReject_outliers(data, m=2.):
    """Function to generate an reduce utilizable function in order to remove outliers of data and replace them by the mean of the previus filtered data"""
    d = numpy.abs(data - numpy.median(data))
    mdev = numpy.median(d)
    def reject_outliers(l, x):
        """Remove outliers and replacethem whit the mean of previous data"""
        s = x/mdev if mdev else 1.
        if s < m:
            return l + [x]
        else:
            if len(l) == 0:
                newX = 0
            else:
                newX = numpy.mean(l)
            return l + [newX]
    return reject_outliers    
        
    
def linearRegresionData(dataX, dataY):
    """DataX and Data Y must be a list whit float values: Returns the following variables newDataY and std_err"""

    slope, intercept, r_value, p_value, std_err = linregress(dataX, dataY)

    newDataY = [(lambda x: slope * x + intercept)(x) for x in dataX]
    
    return newDataY, std_err
    
def jsonDescriptionGraphs(graph):
    """Returns a dictionary whit the description of a graph"""
    return {'name':graph.name,
            'date':str(graph.date),
            'graph_type':graph.graph_type,
            'airMeasureY':GraphsRecord.AIRMEASURE_CHOICES[graph.airMeasureY][1],
            'airMeasureX':GraphsRecord.AIRMEASURE_CHOICES[graph.airMeasureX][1],
            'initialDate':str(graph.initialDate),
            'finalDate':str(graph.finalDate),
            'monitoringStation':graph.monitoringStation.nameMonitoringPlace,
            'glyph_type': GraphsRecord.GLYPH_TYPE_CHOICES[graph.glyph_type-1][1],
            'eliminate_error_sampling':graph.eliminate_error_sampling,
            'mean':graph.mean,
            'median':graph.median,
            'std':graph.std,
            'vari':graph.vari,
            'corrcoef':graph.corrcoef,
            'maxValue':graph.maxValue,
            'minValue':graph.minValue,
            'std_err':graph.std_err}

def defineFormHistoryForm(userGraphs):
    """Create a Form class depending on th user Graphs selected"""
    USERGRAPHS_CHOICES = tuple((graph.id, graph.name) if not(graph.name == "") else (graph.id, str(graph.date)) for graph in userGraphs)
    
    class HistoryForm(forms.Form):
        """Runtime defined class used to the requirment F2-3 form"""
        graphsUser = forms.MultipleChoiceField(label="Seleccione varias graficas para eliminar o solo una para graficar.", choices=USERGRAPHS_CHOICES,  help_text="Seleccione una opcion para graficar o multiples opciones para borrar (Si se seleccionaron varias opciones y se opto por graficar, solamente la opción que este mas arriba de la forma se graficara.)", required=False)
        name = forms.CharField(label="Busqueda mediante nombre.", empty_value=None, max_length=80, error_messages={'max_length': "Solo se aceptan cadenas de hasta 80 caracteres."},  required=False)
        initialDate = forms.DateTimeField(label="Busqueda mediante fecha.",help_text="Ingrese una fecha para buscar la grafica. (2006-10-25, 2006-10-25 14:30, 2006-10-25 14; donde el ultimo parametro es la hora de la consulta)", error_messages={'required':"Se necesita que ingrese una fecha de inicio!" , 'invalid':"Ingrese una fecha valida!"}, input_formats=['%Y-%m-%d', '%Y-%m-%d %H:%M', '%Y-%m-%d %H',], required=False )
    return HistoryForm

def eliminateARegister(model, list2Eliminate): # Modified 20171003 Eliminate the photo from harddrive
    """Returns a boolean list indicated which elements where eliminated.model of objects to eliminate form the database, list2Eliminate whit the primary keys to eliminate"""
    if len(list2Eliminate) == 0:
        return []
    photoObject = model.objects.get(pk=list2Eliminate[0])
    photoPath =  settings.PROJECT_ROOT + "/static/graphsFolder/" + photoObject.photo
    os.remove(photoPath)
    photoObject.delete()
    return [True] + eliminateARegister(model, list2Eliminate[1:])
        

def setListElement(firstDate,lastDate, element, stationID):
    """Sets the lists X and Y whit the respective air quality element depending on the user choices"""
    if element == GraphsRecord.FECHA_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('fecha', flat=True)
        listElement = [station for station in query]
    elif element == GraphsRecord.O3_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('o3', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.CO_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('co', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.NO_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('no', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.NO2_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('no2', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.NOX_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('nox', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.SO2_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('so2', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.TEMPAMB_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('temperaturaAmbiente', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.HUMEDAD_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('humedadRelativa', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.WS_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('ws', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.WD_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('wd', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.PRESBARO_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('presionBarometrica', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.RADSOLAR_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('radiacionSolar', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.PRECIPITACION_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('precipitacion', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.PM10_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('pm10', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.PM25_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('pm25', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]

    
    return listElement


def createAGraph(request):      # Created 20170930 Help to have a uniqe way to graph creation
    """Helper function to create graphs. Request is a dictionary holding the returned GraphsForm user responses"""
    std_err = "No Aplica" # In case that the user do not select regression, the std_error will show a non apply.
    firstDate = dateutil.parser.parse(request["initialDate"])
    lastDate = dateutil.parser.parse(request["finalDate"])

    # Get the data #####################################################################
    if firstDate > lastDate:
        return 1, 1, 1#render(request, "investigacion/homepage.djhtml",
                      #{'graphForm': graphForm,
                       #'the_div': "<h1>LA FECHA INICIAL DEBE DEL PRIMER REGISTRO DEBE DE SER MENOR QUE LA DEL ULTIMO REGISTRO!</h1>"})
    if firstDate == lastDate:
        listX = setListElementSameDate(request["initialDate"], int(request["airMeasureX"]), request["monitoringStation"])
        listY = setListElementSameDate(request["initialDate"], int(request["airMeasureY"]), request["monitoringStation"])
    else:
        listX = setListElement(request["initialDate"], request["finalDate"], int(request["airMeasureX"]), request["monitoringStation"])
        listY = setListElement(request["initialDate"], request["finalDate"], int(request["airMeasureY"]), request["monitoringStation"])
    if len(listX) == 0 or len(listY) == 0:
        return 2,2,2 #render(request, "investigacion/homepage.djhtml",{'graphForm': graphForm, 'the_div': "<h1>NO SE ENCONTRO NINGUN REGISTRO CON LAS FECHAS ESPESIFICADAS!</h1>"})

    ##########################################################
            
    # Utilice enhancement  if selected by the user
    if "eliminate_error_sampling" in request:
        if not(int(request["airMeasureX"]) == GraphsRecord.FECHA_AIRMEASURE):
            outlierFunc = defineReject_outliers(listX, 6)
            listX = reduce(outlierFunc, listX, [])
        if not(int(request["airMeasureY"]) == GraphsRecord.FECHA_AIRMEASURE):
            outlierFunc = defineReject_outliers(listY, 6)
            listY = reduce(outlierFunc, listY, [])
                
            
    # Obtain the statistics tuple
    if not(int(request["airMeasureY"]) == GraphsRecord.FECHA_AIRMEASURE):
        # The dates can be utilices as normal aritmet, and range() function is used insted
        if int(request["airMeasureX"]) == GraphsRecord.FECHA_AIRMEASURE:
            statisticsData = statisticsValues(listY, range(len(listX))) 
        else:
            statisticsData = statisticsValues(listY, listX)
    else:
        statisticsData = ("No aplica.", "No aplica.", "No aplica.","No aplica.", "No aplica.", "No aplica.", "No aplica.")

    # Apply customization for the plot
    if int(request["airMeasureX"]) == GraphsRecord.FECHA_AIRMEASURE:
        if int(request["airMeasureY"]) == GraphsRecord.FECHA_AIRMEASURE:
            plot = figure(responsive=True,  x_axis_type="datetime", output_backend="webgl", y_axis_type="datetime", )
        else:
            plot = figure(responsive=True,  x_axis_type="datetime", output_backend="webgl")
    else:
        if int(request["airMeasureY"]) == GraphsRecord.FECHA_AIRMEASURE:
            plot = figure(responsive=True, output_backend="webgl", y_axis_type="datetime")
        else:
            plot = figure(responsive=True, output_backend="webgl")
    if len(listY) >=  25920:
        glyphAlpha = 0.1
    else:
        glyphAlpha = 1
                
    # Put a little message for each point on the graph.
    dataSource = ColumnDataSource(data=dict(
        x=listX,
        y=listY,
    ))
    hoverTool = HoverTool(tooltips=[
        ("(" + GraphsRecord.AIRMEASURE_CHOICES[int(request["airMeasureX"])][1]+"," + GraphsRecord.AIRMEASURE_CHOICES[int(request["airMeasureY"])][1]+ ")", "($x, $y)"),
    ])
    plot.add_tools(hoverTool)

    # Check if the graphs uses points or lines
    if int(request["glyph_type"]) == GraphsRecord.LINE_GLYPH_TYPE:
        r = plot.line('x', 'y', legend=GraphsRecord.AIRMEASURE_CHOICES[int(request["airMeasureX"])][1]+ " vs " + GraphsRecord.AIRMEASURE_CHOICES[int(request["airMeasureY"])][1], line_width=glyphAlpha, source=dataSource)
    else:
        r = plot.scatter('x', 'y', legend=GraphsRecord.AIRMEASURE_CHOICES[int(request["airMeasureX"])][1]+ " vs " + GraphsRecord.AIRMEASURE_CHOICES[int(request["airMeasureY"])][1], alpha=glyphAlpha, source=dataSource)

    # Create the Regression line or not
    if int(request["graph_type"]) == GraphsRecord.REGRESION_GRAPH_TYPE:
        if int(request["airMeasureX"]) == GraphsRecord.FECHA_AIRMEASURE:
            if int(request["airMeasureY"]) == GraphsRecord.FECHA_AIRMEASURE:
                rango = range(len(listX))
                newDataY, std_err = linearRegresionData(rango, rango)
            else:
                newDataY, std_err = linearRegresionData(range(len(listX)), listY)
        else:
            if int(request["airMeasureY"]) == GraphsRecord.FECHA_AIRMEASURE:
                newDataY, std_err = linearRegresionData(listX, range(len(listX)))
            else:
                newDataY, std_err = linearRegresionData(listX, listY)
                
        dataSourceReg = ColumnDataSource(data=dict(
            xReg=listX,
            yReg=newDataY,
        ))
        
        r = plot.line('xReg', 'yReg', legend=GraphsRecord.AIRMEASURE_CHOICES[int(request["airMeasureX"])][1]+ " vs " + GraphsRecord.AIRMEASURE_CHOICES[int(request["airMeasureY"])][1] + "(Linea)", source=dataSourceReg, color='#ffb302', line_width=5)
        plot.legend.click_policy="hide"
    plot.title.text = 'Fecha correspondiente entre ' + request['initialDate'] + " y " + request['finalDate']

    return plot, std_err, statisticsData

def setListElementSameDate(date, element, stationID):
    """Sets the lists X and Y whit the respective air quality element depending on the user choices"""
    if element == GraphsRecord.FECHA_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__icontains=date).values_list('fecha', flat=True)
        listElement = [station for station in query]
    elif element == GraphsRecord.O3_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__icontains=date).values_list('o3', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.CO_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__icontains=date).values_list('co', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.NO_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__icontains=date).values_list('no', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.NO2_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__icontains=date).values_list('no2', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.NOX_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__icontains=date).values_list('nox', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.SO2_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__icontains=date).values_list('so2', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.TEMPAMB_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__icontains=date).values_list('temperaturaAmbiente', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.HUMEDAD_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__icontains=date).values_list('humedadRelativa', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.WS_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__icontains=date).values_list('ws', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.WD_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__icontains=date).values_list('wd', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.PRESBARO_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__icontains=date).values_list('presionBarometrica', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.RADSOLAR_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__icontains=date).values_list('radiacionSolar', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.PRECIPITACION_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__icontains=date).values_list('precipitacion', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.PM10_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__icontains=date).values_list('pm10', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif element == GraphsRecord.PM25_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=stationID).filter(fecha__icontains=date).values_list('pm25', flat=True)
        listElement = [float(station) if not(isnan(float(station))) else 0  for station in query]  

    return listElement
# Provided by Duncan on StackOverflow
def monthdelta(date, delta):
    m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
    if not m: m = 12
    d = min(date.day, [31,
        29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
    return date.replace(day=d,month=m, year=y)

def generateGraphReport(listGraphs):
    """Requirment F2-6. Returns a string whit pdf information to generate a report."""

    beginDocument = """
\\documentclass{article}
\\usepackage{graphicx}
\\begin{document}""".decode("utf-8")
    graphDocument = r'''
\begin{figure}[h]
\centering
\includegraphics[width=\textwidth]{GRAPHDIR}
\end{figure}'''.decode("utf-8")
    tableDocument = r'''
\begin{center}
\begin{tabular}{|c|c|}
\hline
\textbf{Estadisticas} & \textbf{Valor}  \\
\hline
Media & MEAN\\
\hline
Mediana & MEDIAN\\
\hline
Desviación Estándar & STDSTD\\
\hline
Varianza & VARI\\
\hline
Coeficiente de Correlación & CORRCOEF\\
\hline
Valor Máximo & MAXVALUE\\
\hline
Valor Minimo & MINVALUE\\
\hline
Error Estándar & STD_ERR\\
\hline
\end{tabular}
\end{center}'''.decode("utf-8")
    endDocument = r'''
\end{document}'''.decode("utf-8")
    def joinGraphs(latexDocument, graphID):
        """Join the Graphs photo and tables."""
        if len(listGraphs) == 0:
            return listGraphs + endDocument
        graph = GraphsRecord.objects.get(pk=graphID)
        graphPhotoDir = GRAPHSDIR + graph.photo
        graphLatex = graphDocument.replace("GRAPHDIR", graphPhotoDir)
        tableLatex = tableDocument.replace("MEAN", str(graph.mean)).replace("MEDIAN", str(graph.median)).replace("STDSTD", str(graph.std)).replace("VARI", str(graph.vari)).replace("CORRCOEF", str(graph.corrcoef)).replace("MAXVALUE", str(graph.maxValue)).replace("MINVALUE", str(graph.minValue)).replace("STD_ERR", str(graph.std_err))
        return latexDocument + graphLatex + tableLatex

    completReport = beginDocument + reduce(joinGraphs, listGraphs, "") + endDocument

    return latex2pdf(completReport)
