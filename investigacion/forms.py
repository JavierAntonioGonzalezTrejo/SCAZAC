#!/usr/bin/python
# -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ValidationError
from investigacion.models import GraphsRecord, MonitoringStation
    
class GraphsForm(forms.Form):
    """Class that will hold the Form to handle the Graphing capabilities of the system"""
    graph_type = forms.ChoiceField(label="Tipo de Gráfica", choices=GraphsRecord.GRAPH_TYPE_CHOICES,  help_text="Escoga si desea comparar un elemento con otro o realizar un modelo basico de una grafica en particular.")
    airMeasureY = forms.ChoiceField(label="Elemento en Y", choices=GraphsRecord.AIRMEASURE_CHOICES,  help_text="Escoga que elemento estara en el eje de las Y.")
    airMeasureX = forms.ChoiceField(label="Elemento en X", choices=GraphsRecord.AIRMEASURE_CHOICES,  help_text="Escoga que elemento estara en el eje de las X.")
    initialDate = forms.DateField(label="Fecha del primer registro",help_text="Ingrese una fecha de donde se empieze a recolectar datos para la grafica. (2006-10-25, 10/25/2006, 10/25/06)", error_messages={'required':"Se necesita que ingrese una fecha de inicio!" , 'invalid':"Ingrese una fecha valida!"} )
    finalDate = forms.DateField(label="Fecha del ultimo registro",help_text="Ingrese una fecha de donde se termine de recolectar datos para la grafica. (2006-10-25, 10/25/2006, 10/25/06)", error_messages={'required':"Se necesita que ingrese una fecha de inicio!" , 'invalid':"Ingrese una fecha valida!"} )
    monitoringStation = forms.ChoiceField(label="Estación de monitoreo", choices=tuple((station.serialNumber, station.nameMonitoringPlace) for station in MonitoringStation.objects.all()), help_text="Escoga la estación de monitoreo de donde se obtendran los datos.")
    glyph_type = forms.ChoiceField(label="Representación de la Grafica", choices=GraphsRecord.GLYPH_TYPE_CHOICES, help_text="Escoga con que elemento grafico se representaran los datos (Linea o puntos).")
    eliminate_error_sampling = forms.BooleanField(label="¿Mejorar la calidad de los datos?", required=False, help_text="Se elminaran, en lo razonable, posibles errores de muestreo que se tengan en los datos (Aumenta timepo de espera)" )
    save_graph = forms.BooleanField(label="¿Salvar la grafica en el historico?", required=False, help_text="Cuando guarde la grafica puede asignarle un nombre a la misma. De cualquier manera se guardara con la fecha y hora de la peticion de la grafica.") # Modified 20170928 Match whit the SRS
    name = forms.CharField(label="Nombre de la grafica (Si se desea guardar en el historial)", empty_value=None, max_length=80, error_messages={'max_length': "Solo se aceptan cadenas de hasta 80 caracteres."},  required=False)
    
    

