# -*- codoing: utf-8 -*-
# All Decimal Field will have 0.00000 this format.
# Register of Modifications:
# Modificated 20170713: Eliminated all methods to obtain IMECAS, will be remplaced whit static decimal values
# Modificated 20170715: To all imecas, the values max digit before the point where maximized by one.
# Modificated 20170721: Detected bug on the fecha field. It must be a DateTimeField in order to accept hours and minutes
# Modificates 20170722: Bug corrected on str for MonitoringData, now aoutputs an str using the DateTimeFild
# Modificated 20170807: On MonitoringData fecha no longer serves as the primary key (New primary key: id), make the combination of idStation and fecha unique for each register.
from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
import math

from django.db import models

class MonitoringStation(models.Model):
    """Model which will hold General information about the Monitoring Stations"""
    serialNumber = models.IntegerField(primary_key = True) # Primary key of the model, Will
    nameMonitoringPlace = models.CharField(max_length=125);            
    latitude = models.DecimalField(max_digits=10, decimal_places=7); # -102.0242795 This is a representation onhow many digits the lat an lenght can have
    length = models.DecimalField(max_digits=10, decimal_places=7);
    monitoringRadius = models.DecimalField(max_digits=7, decimal_places=2) # If the Administrator do not have a radius for the monitoring stations, assume a 1000 meters as the norm
    dateNewestRegister = models.DateField();
    dateOldestRegister = models.DateField();
    
    def __str__(self):
        """The function will be represented by the name of the placewhere the monitoring station is acting"""
        return self.nameMonitoringPlace

    # In order to have MonitoringStations having only a subset of the pollant described here, all pollant values will have null value option activated
class MonitoringData(models.Model):
    """Core of the sistem, will hold the information of all monitoring Systems"""
    idStation = models.ForeignKey(
        'MonitoringStation',
        on_delete=models.CASCADE,
        )
    fecha = models.DateTimeField() # BUG CORRECTED: DateField to DateTimeField, Modified 20170807: Fecha will not longer be the primary key for the database, now the id autogenerated primary key by Django will be the primary key.
    temperatura = models.DecimalField(null=True, max_digits=12, decimal_places=9) # Based on the data of Seriunus reports
    o3 =  models.DecimalField(null=True, max_digits=12, decimal_places=9)
    co = models.DecimalField(null=True, max_digits=12, decimal_places=9)
    no = models.DecimalField(null=True, max_digits=12, decimal_places=9)
    no2 = models.DecimalField(null=True, max_digits=12, decimal_places=9)
    nox = models.DecimalField(null=True, max_digits=12, decimal_places=9)
    so2 =  models.DecimalField(null=True, max_digits=12, decimal_places=9)
    temperaturaAmbiente = models.DecimalField(null=True, max_digits=12, decimal_places=9)
    humedadRelativa = models.DecimalField(null=True, max_digits=12, decimal_places=9)
    ws = models.DecimalField(null=True, max_digits=12, decimal_places=9)
    wd = models.DecimalField(null=True, max_digits=12, decimal_places=9)
    presionBarometrica =  models.DecimalField(null=True, max_digits=12, decimal_places=9)
    radiacionSolar = models.DecimalField(null=True, max_digits=12, decimal_places=9)
    precipitacion = models.DecimalField(null=True, max_digits=12, decimal_places=9)
    pm10 = models.DecimalField(null=True, max_digits=12, decimal_places=9)
    pm25 = models.DecimalField(null=True, max_digits=12, decimal_places=9)
    # Added 20170713
    # Modified 20170715
    imecaO3 = models.DecimalField(null=True, max_digits=6, decimal_places=2) # 0.00 For the imecas
    imecaNO = models.DecimalField(null=True, max_digits=6, decimal_places=2)
    imecaNO2 = models.DecimalField(null=True, max_digits=6, decimal_places=2)
    imecaNOX = models.DecimalField(null=True, max_digits=6, decimal_places=2)
    imecaSO2 = models.DecimalField(null=True, max_digits=6, decimal_places=2)
    imecaCO = models.DecimalField(null=True, max_digits=6, decimal_places=2)
    imecaPM10 = models.DecimalField(null=True, max_digits=6, decimal_places=2)
    imecaPM25 = models.DecimalField(null=True, max_digits=6, decimal_places=2)
    def __str__(self):
        """Function to represent the model"""
        return str(self.fecha)  # BUG CORRECTED: The srt function needs to output a String 

    class Meta:
        """Class to hold constraints of the database, espesificaly to enforce the rule of the unique convination of fecha and idStation: Have a unique date register per monitoring station"""
        unique_together = ("idStation", "fecha")
        
