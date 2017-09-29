# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from investigacion.models import MonitoringStation, MonitoringData, GraphsRecord
from investigacion.forms import GraphsForm
from django.views.generic import TemplateView
from bokeh.plotting import figure, ColumnDataSource
from bokeh.embed import components
from bokeh.models import HoverTool
import dateutil.parser
import numpy
from math import isnan
from scipy.stats import pearsonr
from functools import reduce


class Principal(TemplateView):
    """Class that holds the requirment F2-3"""
    dataModel = MonitoringData
    M = 6                       # M value nesesary to remove graphs outliners
    

    def get(self, request):
        """Initial Function"""
        
        station = MonitoringStation.objects.all()[0]
        graphForm = GraphsForm({ 'graph_type':"1", 'airMeasureY':"2", 'airMeasureX':"1", 'initialDate':str(station.dateNewestRegister), 'finalDate':str(station.dateNewestRegister),'monitoringStation':str(station.serialNumber), 'glyph_type':"2",'name':"Grafica de Prueba"})
        
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

            firstDate = dateutil.parser.parse(request.POST["initialDate"])
            lastDate = dateutil.parser.parse(request.POST["finalDate"])

            if firstDate > lastDate:
                return render(request, "investigacion/homepage.djhtml",
                    {'graphForm': graphForm,
                     'the_div': "<h1>LA FECHA INICIAL DEBE DEL PRIMER REGISTRO DEBE DE SER MENOR QUE LA DEL ULTIMO REGISTRO!</h1>"})
            if firstDate == lastDate:
                dataQuery = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__icontains=request.POST["initialDate"])
            else:
                dataQuery = Principal.dataModel.objects.filter(idStation__pk=request.POST["monitoringStation"]).filter(fecha__gte=firstDate).filter(fecha__lte=lastDate)
            # TO NOT PERFORM OPERATIONS ON AN EMPTY ARRAY
            if len(dataQuery) == 0:
                return render(request, "investigacion/homepage.djhtml",{'graphForm': graphForm,
                                                                            'the_div': "<h1>NO SE ENCONTRO NINGUN REGISTRO CON LAS FECHAS ESPESIFICADAS!</h1>"})
            listX, listY = setListsXY(dataQuery, request)

            
            
            # Utilice enhancement  if selected by the user
            if "eliminate_error_sampling" in request.POST:
                if not(int(request.POST["airMeasureX"]) == GraphsRecord.FECHA_AIRMEASURE):
                    outlierFunc = defineReject_outliers(listX, 6)
                    listX = reduce(outlierFunc, listX, [])
                if not(int(request.POST["airMeasureY"]) == GraphsRecord.FECHA_AIRMEASURE):
                    outlierFunc = defineReject_outliers(listY, 6)
                    listY = reduce(outlierFunc, listY, [])

            print len(listX)
            print len(listY)
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
                    plot = figure(responsive=True,  x_axis_type="datetime", output_backend="webgl", y_axis_type="datetime")
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
                

            if int(request.POST["graph_type"]) == GraphsRecord.CORRELACIONAL_GRAPH_TYPE:
                # Put a little message for each point on the graph.
                dataSource = ColumnDataSource(data=dict(
                    x=listX,
                    y=listY,
                ))
                hoverTool = HoverTool(tooltips=[
                    ("(" + GraphsRecord.AIRMEASURE_CHOICES[int(request.POST["airMeasureX"])][1]+"," + GraphsRecord.AIRMEASURE_CHOICES[int(request.POST["airMeasureY"])][1]+ ")", "($x, $y)"),
                ])

                plot.add_tools(hoverTool)

                if int(request.POST["glyph_type"]) == GraphsRecord.LINE_GLYPH_TYPE:
                    r = plot.line('x', 'y', legend=GraphsRecord.AIRMEASURE_CHOICES[int(request.POST["airMeasureX"])][1]+ " vs " + GraphsRecord.AIRMEASURE_CHOICES[int(request.POST["airMeasureY"])][1], line_width=glyphAlpha, source=dataSource)
                else:
                    r = plot.scatter('x', 'y', legend=GraphsRecord.AIRMEASURE_CHOICES[int(request.POST["airMeasureX"])][1]+ " vs " + GraphsRecord.AIRMEASURE_CHOICES[int(request.POST["airMeasureY"])][1], alpha=glyphAlpha, source=dataSource)
        
            else:
                pass
                
            script, div = components(plot)

            if 'save_graph' in request.POST:
                print request.POST['user']

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
                           "min":statisticsData[6]})
        return render(request, "investigacion/homepage.djhtml",
                          {'graphForm': graphForm})
        
            

def setListsXY(query, request):
    """Sets the lists X and Y whit the respective air quality element depending on the user choices"""
    if int(request.POST["airMeasureY"]) == GraphsRecord.FECHA_AIRMEASURE:
        listY = [station.fecha for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.O3_AIRMEASURE:
        listY = [float(station.o3) if not(isnan(float(station.o3))) else 0  for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.CO_AIRMEASURE:
        listY = [float(station.co) if not(isnan(float(station.co))) else 0 for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.NO_AIRMEASURE:
        listY = [float(station.no) if not(isnan(float(station.no))) else 0 for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.NO2_AIRMEASURE:
        listY = [float(station.no2) if not(isnan(float(station.no2))) else 0 for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.NOX_AIRMEASURE:
        listY = [float(station.nox) if not(isnan(float(station.nox))) else 0 for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.SO2_AIRMEASURE:
        listY = [float(station.so2) if not(isnan(float(station.so2))) else 0 for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.TEMPAMB_AIRMEASURE:
        listY = [float(station.temperaturaAmbiente) if not(isnan(float(station.temperaturaAmbiente))) else 0 for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.HUMEDAD_AIRMEASURE:
        listY = [float(station.humedadRelativa) if not(isnan(float(station.humedadRelativa))) else 0 for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.WS_AIRMEASURE:
        listY = [float(station.ws) if not(isnan(float(station.ws))) else 0 for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.WD_AIRMEASURE:
        listY = [float(station.wd) if not(isnan(float(station.wd))) else 0 for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.PRESBARO_AIRMEASURE:
        listY = [float(station.presionBarometrica) if not(isnan(float(station.presionBarometrica))) else 0 for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.RADSOLAR_AIRMEASURE:
        listY = [float(station.radiacionSolar) if not(isnan(float(station.radiacionSolar))) else 0 for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.PRECIPITACION_AIRMEASURE:
        listY = [float(station.precipitacion) if not(isnan(float(station.precipitacion))) else 0 for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.PM10_AIRMEASURE:
        listY = [float(station.pm10) if not(isnan(float(station.pm10))) else 0 for station in query]
    elif int(request.POST["airMeasureY"]) == GraphsRecord.PM25_AIRMEASURE:
        listY = [float(station.pm25) if not(isnan(float(station.pm25))) else 0 for station in query]

    # For the list X

    if int(request.POST["airMeasureX"]) == GraphsRecord.FECHA_AIRMEASURE:
        listX = [station.fecha for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.O3_AIRMEASURE:
        listX = [float(station.o3) if not(isnan(float(station.o3))) else 0  for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.CO_AIRMEASURE:
        listX = [float(station.co) if not(isnan(float(station.co))) else 0 for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.NO_AIRMEASURE:
        listX = [float(station.no) if not(isnan(float(station.no))) else 0 for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.NO2_AIRMEASURE:
        listX = [float(station.no2) if not(isnan(float(station.no2))) else 0 for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.NOX_AIRMEASURE:
        listX = [float(station.nox) if not(isnan(float(station.nox))) else 0 for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.SO2_AIRMEASURE:
        listX = [float(station.so2) if not(isnan(float(station.so2))) else 0 for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.TEMPAMB_AIRMEASURE:
        listX = [float(station.temperaturaAmbiente) if not(isnan(float(station.temperaturaAmbiente))) else 0 for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.HUMEDAD_AIRMEASURE:
        listX = [float(station.humedadRelativa) if not(isnan(float(station.humedadRelativa))) else 0 for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.WS_AIRMEASURE:
        listX = [float(station.ws) if not(isnan(float(station.ws))) else 0 for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.WD_AIRMEASURE:
        listX = [float(station.wd) if not(isnan(float(station.wd))) else 0 for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.PRESBARO_AIRMEASURE:
        listX = [float(station.presionBarometrica) if not(isnan(float(station.presionBarometrica))) else 0 for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.RADSOLAR_AIRMEASURE:
        listX = [float(station.radiacionSolar) if not(isnan(float(station.radiacionSolar))) else 0 for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.PRECIPITACION_AIRMEASURE:
        listX = [float(station.precipitacion) if not(isnan(float(station.precipitacion))) else 0 for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.PM10_AIRMEASURE:
        listX = [float(station.pm10) if not(isnan(float(station.pm10))) else 0 for station in query]
    elif int(request.POST["airMeasureX"]) == GraphsRecord.PM25_AIRMEASURE:
        listX = [float(station.pm25) if not(isnan(float(station.pm25))) else 0 for station in query]
    

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
        
    
