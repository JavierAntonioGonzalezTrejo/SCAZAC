#!/usr/bin/python
# -*- coding: utf-8 -*-
# Created 20171015
from django import forms
from django.core.exceptions import ValidationError
from investigacion.models import MonitoringStation
from decimal import Decimal

class MonitoringMapForm(forms.Form): # Created 20171016
    """Form for the requirment F3-2"""
    centerLatitude = forms.DecimalField(label="Latitud", help_text="Latitud con la que se posiciona el centro del mapa en la pagina principal.", max_digits=10, decimal_places=7, max_value=Decimal(90), min_value=Decimal(-90))
    centerLength = forms.DecimalField(label="Longitud", help_text="Longitud con la que se posiciona el centro del mapa en la pagina principal.", max_digits=10, decimal_places=7, max_value=Decimal(180), min_value=Decimal(-180))
    zoom = forms.IntegerField(label="Zoom al mapa",  help_text="Cuanto terreno se mostrara en el mapa.", max_value=22, min_value=0)
    googleAPIKey = forms.CharField(label="Google API",  help_text="Codigo utilizado para identificar a los desarrolladores del API de google maps, necesario para poder utilizar el mapa." , max_length=100)


    
