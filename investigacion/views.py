# -*- coding: utf-8 -*-
# Modified 20170930: Added the requirment F2-3
from __future__ import unicode_literals
from django.shortcuts import render
from django.conf import settings
from django import forms        # Added 20171001 Make 
from investigacion.models import MonitoringStation, MonitoringData, GraphsRecord
from investigacion.forms import GraphsForm
from django.views.generic import TemplateView
from bokeh.plotting import figure, ColumnDataSource
from bokeh.embed import components
from bokeh.models import HoverTool
import dateutil.parser
import numpy
from math import isnan
from scipy.stats import pearsonr, linregress
from functools import reduce
import datetime                 # Added 20171001: Time for the requirment F2-04
import json                     # Added 20171001: To send information to the javascript side
class Principal(TemplateView):
    """Class that holds the requirment F2-3"""
    dataModel = MonitoringData
    M = 6                       # M value nesesary to remove graphs outliners
    

    def get(self, request):
        """Initial Function"""
        
        station = MonitoringStation.objects.all()[0]
        graphForm = GraphsForm({ 'graph_type':"1", 'airMeasureY':"1", 'airMeasureX':"0", 'initialDate':str(station.dateNewestRegister), 'finalDate':str(station.dateNewestRegister),'monitoringStation':str(station.serialNumber), 'glyph_type':"2",'name':"Grafica de Prueba"})
        
        retrivedData = Principal.dataModel.objects.filter(idStation__pk=station.serialNumber).filter(fecha__icontains=station.dateNewestRegister)
        time = [data.fecha for data in retrivedData]
        ozono = [float(data.o3) for data in retrivedData]

        plot = figure(responsive=True,  x_axis_type="datetime", output_backend="webgl")
        r = plot.scatter(time, ozono, legend="Ozono vs Tiempo")

        

        script, div = components(plot)

        # Statistics part
        statistics = statisticsValues(ozono, range(0,len(time)))
        
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
                       "min":statistics[6]})
    
    def post(self, request):
        """Function that recives the petitions to graph"""
        graphForm = GraphsForm(request.POST)
        
        if graphForm.is_valid():
            save_function = ""
            plot, std_err, statisticsData = createAGraph(request)
            
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
                return render(request, "investigacion/history.djhtml",
                          {"historyForm": form,
                           "descriptionGraphs":json.dumps(descriptionGraphs)})
        else:
            return render(request, "investigacion/history.djhtml",{"historyForm": form})
        

def createAGraph(request):      # Created 20170930 Help to have a uniqe way to graph creation
    """Helper function to create graphs"""
    std_err = "No Aplica" # In case that the user do not select regression, the std_error will show a non apply.
    firstDate = dateutil.parser.parse(request.POST["initialDate"])
    lastDate = dateutil.parser.parse(request.POST["finalDate"])

    # Get the data #####################################################################
    if firstDate > lastDate:
        return render(request, "investigacion/homepage.djhtml",
                      {'graphForm': graphForm,
                       'the_div': "<h1>LA FECHA INICIAL DEBE DEL PRIMER REGISTRO DEBE DE SER MENOR QUE LA DEL ULTIMO REGISTRO!</h1>"})
    if firstDate == lastDate:
        listX, listY = setListsXYSameDate(request)
    else:
        listX, listY = setListsXY(request.POST["initialDate"], request.POST["finalDate"], request)
    if len(listX) == 0:
        return render(request, "investigacion/homepage.djhtml",{'graphForm': graphForm, 'the_div': "<h1>NO SE ENCONTRO NINGUN REGISTRO CON LAS FECHAS ESPESIFICADAS!</h1>"})

    ##########################################################
            
    # Utilice enhancement  if selected by the user
    if "eliminate_error_sampling" in request.POST:
        if not(int(request.POST["airMeasureX"]) == GraphsRecord.FECHA_AIRMEASURE):
            outlierFunc = defineReject_outliers(listX, 6)
            listX = reduce(outlierFunc, listX, [])
        if not(int(request.POST["airMeasureY"]) == GraphsRecord.FECHA_AIRMEASURE):
            outlierFunc = defineReject_outliers(listY, 6)
            listY = reduce(outlierFunc, listY, [])
                
            
    # Obtain the statistics tuple
    if not(int(request.POST["airMeasureY"]) == GraphsRecord.FECHA_AIRMEASURE):
        # The dates can be utilices as normal aritmet, and range() function is used insted
        if int(request.POST["airMeasureX"]) == GraphsRecord.FECHA_AIRMEASURE:
            statisticsData = statisticsValues(listY, range(len(listX))) 
        else:
            statisticsData = statisticsValues(listY, listX)
    else:
        statisticsData = ("No aplica.", "No aplica.", "No aplica.","No aplica.", "No aplica.", "No aplica.", "No aplica.")

    # Apply customization for the plot
    if int(request.POST["airMeasureX"]) == GraphsRecord.FECHA_AIRMEASURE:
        if int(request.POST["airMeasureY"]) == GraphsRecord.FECHA_AIRMEASURE:
            plot = figure(responsive=True,  x_axis_type="datetime", output_backend="webgl", y_axis_type="datetime", )
        else:
            plot = figure(responsive=True,  x_axis_type="datetime", output_backend="webgl")
    else:
        if int(request.POST["airMeasureY"]) == GraphsRecord.FECHA_AIRMEASURE:
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
        ("(" + GraphsRecord.AIRMEASURE_CHOICES[int(request.POST["airMeasureX"])][1]+"," + GraphsRecord.AIRMEASURE_CHOICES[int(request.POST["airMeasureY"])][1]+ ")", "($x, $y)"),
    ])
    plot.add_tools(hoverTool)

    # Check if the graphs uses points or lines
    if int(request.POST["glyph_type"]) == GraphsRecord.LINE_GLYPH_TYPE:
        r = plot.line('x', 'y', legend=GraphsRecord.AIRMEASURE_CHOICES[int(request.POST["airMeasureX"])][1]+ " vs " + GraphsRecord.AIRMEASURE_CHOICES[int(request.POST["airMeasureY"])][1], line_width=glyphAlpha, source=dataSource)
    else:
        r = plot.scatter('x', 'y', legend=GraphsRecord.AIRMEASURE_CHOICES[int(request.POST["airMeasureX"])][1]+ " vs " + GraphsRecord.AIRMEASURE_CHOICES[int(request.POST["airMeasureY"])][1], alpha=glyphAlpha, source=dataSource)

    # Create the Regression line or not
    if int(request.POST["graph_type"]) == GraphsRecord.REGRESION_GRAPH_TYPE:
        if int(request.POST["airMeasureX"]) == GraphsRecord.FECHA_AIRMEASURE:
            if int(request.POST["airMeasureY"]) == GraphsRecord.FECHA_AIRMEASURE:
                rango = range(len(listX))
                newDataY, std_err = linearRegresionData(rango, rango)
            else:
                newDataY, std_err = linearRegresionData(range(len(listX)), listY)
        else:
            if int(request.POST["airMeasureY"]) == GraphsRecord.FECHA_AIRMEASURE:
                newDataY, std_err = linearRegresionData(listX, range(len(listX)))
            else:
                newDataY, std_err = linearRegresionData(listX, listY)
                
        dataSourceReg = ColumnDataSource(data=dict(
            xReg=listX,
            yReg=newDataY,
        ))
        
        r = plot.line('xReg', 'yReg', legend=GraphsRecord.AIRMEASURE_CHOICES[int(request.POST["airMeasureX"])][1]+ " vs " + GraphsRecord.AIRMEASURE_CHOICES[int(request.POST["airMeasureY"])][1] + "(Linea)", source=dataSourceReg, color='#ffb302', line_width=5)
        plot.legend.click_policy="hide"
    plot.title.text = 'Fecha correspondiente entre ' + request.POST['initialDate'] + " y " + request.POST['finalDate']

    return plot, std_err, statisticsData


def setListsXY(firstDate,lastDate, request):
    """Sets the lists X and Y whit the respective air quality element depending on the user choices"""
    if int(request.POST["airMeasureY"]) == GraphsRecord.FECHA_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('fecha', flat=True)
        listY = [station for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.O3_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('o3', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.CO_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('co', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.NO_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('no', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.NO2_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('no2', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.NOX_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('nox', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.SO2_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('so2', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.TEMPAMB_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('temperaturaAmbiente', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.HUMEDAD_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('humedadRelativa', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.WS_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('ws', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.WD_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('wd', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.PRESBARO_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('presionBarometrica', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.RADSOLAR_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('radiacionSolar', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.PRECIPITACION_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('precipitacion', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.PM10_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('pm10', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.PM25_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('pm25', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]

    # For the list X
    if int(request.POST["airMeasureX"]) == GraphsRecord.FECHA_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('fecha', flat=True)
        listX = [station for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.O3_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('o3', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.CO_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('co', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.NO_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('no', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.NO2_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('no2', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.NOX_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('nox', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.SO2_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('so2', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.TEMPAMB_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('temperaturaAmbiente', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.HUMEDAD_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('humedadRelativa', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.WS_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('ws', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.WD_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('wd', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.PRESBARO_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('presionBarometrica', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.RADSOLAR_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('radiacionSolar', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.PRECIPITACION_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('precipitacion', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.PM10_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('pm10', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.PM25_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate).values_list('pm25', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]

    

    return listX, listY

def setListsXYSameDate(request):
    """Sets the lists X and Y whit the respective air quality element depending on the user choices"""
    if int(request.POST["airMeasureY"]) == GraphsRecord.FECHA_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('fecha', flat=True)
        listY = [station for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.O3_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('o3', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.CO_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('co', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.NO_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('no', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.NO2_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('no2', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.NOX_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('nox', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.SO2_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('so2', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.TEMPAMB_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('temperaturaAmbiente', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.HUMEDAD_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('humedadRelativa', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.WS_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('ws', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.WD_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('wd', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.PRESBARO_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('presionBarometrica', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.RADSOLAR_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('radiacionSolar', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.PRECIPITACION_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('precipitacion', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.PM10_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('pm10', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.PM25_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('pm25', flat=True)
        listY = [float(station) if not(isnan(float(station))) else 0  for station in query]

    # For the list X
    if int(request.POST["airMeasureX"]) == GraphsRecord.FECHA_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('fecha', flat=True)
        listX = [station for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.O3_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('o3', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.CO_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('co', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.NO_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('no', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.NO2_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('no2', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.NOX_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('nox', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.SO2_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('so2', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.TEMPAMB_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('temperaturaAmbiente', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.HUMEDAD_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('humedadRelativa', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.WS_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('ws', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.WD_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('wd', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.PRESBARO_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('presionBarometrica', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.RADSOLAR_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('radiacionSolar', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.PRECIPITACION_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('precipitacion', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.PM10_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('pm10', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.PM25_AIRMEASURE:
        query = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST['initialDate']).values_list('pm25', flat=True)
        listX = [float(station) if not(isnan(float(station))) else 0  for station in query]

    

    return listX, listY

def statisticsValues(dataY, dataX):
    """Obtain the mean, median, std, var, corrcoef, max and min of the selected data on this order"""
    if None in dataY:
        print "hola"
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
        graphsUser = forms.MultipleChoiceField(label="Seleccione varias graficas para eliminar o solo una para graficar.", choices=USERGRAPHS_CHOICES,  help_text="Seleccione una opcion para graficar o multiples opciones para borrar (Si se seleccionaron varias opciones y se opto por graficar, solamente la opción que este mas arriba de la forma se graficara.)")
        name = forms.CharField(label="Busqueda mediante nombre.", empty_value=None, max_length=80, error_messages={'max_length': "Solo se aceptan cadenas de hasta 80 caracteres."},  required=False)
        initialDate = forms.DateTimeField(label="Busqueda mediante fecha.",help_text="Ingrese una fecha para buscar la grafica. (2006-10-25, 2006-10-25 14:30, 2006-10-25 14; donde el ultimo parametro es la hora de la consulta)", error_messages={'required':"Se necesita que ingrese una fecha de inicio!" , 'invalid':"Ingrese una fecha valida!"}, input_formats=['%Y-%m-%d', '%Y-%m-%d %H:%M', '%Y-%m-%d %H',], required=False )
    return HistoryForm
