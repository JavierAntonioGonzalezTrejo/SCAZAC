# Reports of change
# Modification 20170723: Adding the Class MonitoringMap
# Modification 20170807: Added idStation to the ImecaData.. models
# Modification 20170808: Added
# Added Class ImecaDataHour 20170812
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from investigacion.models import MonitoringStation
import datetime
import dateutil.parser

YEAR_CHOICES = []
for r in range(1980, (datetime.datetime.now().year+1)):
        YEAR_CHOICES.append((r,r))
# Create your models here.
class MonitoringReports(models.Model):
        """Class which will hols information about the air Quality Reports made by goverment"""
        idReport = models.IntegerField(primary_key=True)
        year = models.IntegerField(('year'),choices=YEAR_CHOICES, default=datetime.datetime.now().year) # Modified 201707
        fileLocation = models.FileField(upload_to='reports/%Y/%m/%d/') # Added Date of upload
        title = models.CharField(max_length=200) # Aproximate length of each title image
        cover = models.ImageField(upload_to='reImages/%Y/%m/%d/') # Added date of upload and folder
        def __str__(self):
                """The class whill be represented by the title"""
                return str(self.title)
    
class MonitoringMap(models.Model):
        """Holds Zoom and posistion information about the Map showed on the first view and developer String to use google maps"""
        idMap = models.IntegerField(primary_key=True)
        centerLatitude = models.DecimalField(max_digits=10, decimal_places=7)
        centerLength = models.DecimalField(max_digits=10, decimal_places=7)
        zoom = models.IntegerField();
        googleAPIKey = models.CharField(max_length=100)

        def __str__(self):
                """The representation of the class"""
                return self.googleAPIKey
        
class ImecaDataDay(models.Model):
        """Hold the IMECA value of each day on the system"""
        fecha = models.DateField() # Of each Day, Modificated 20170807: fecha no longer serves a the primary key, now the id django autogenerated field serves that porpuse
        idStation = models.ForeignKey(
        'investigacion.MonitoringStation',
        on_delete=models.CASCADE,
        )                       # Added 20170807 Added to have the same date for diferents stations register
        # IMECA Values
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
                return str(self.fecha)

        class Meta:# Added 20170807
                """Class to hold constraints of the database, espesificaly to enforce the rule of the unique convination of fecha and idStation: Have a unique date register per monitoring station"""
                unique_together = ("idStation", "fecha")
                
        
class ImecaDataMonth(models.Model):
        """Hold the IMECA data for each month """
        fecha = models.DateField() # Of each Month (will be handel by function, this is to not get bottered whit the day on the DateFIeld, Modificated 20170807: fecha no longer serves a the primary key, now the id django autogenerated field serves that porpuse
        idStation = models.ForeignKey(
        'investigacion.MonitoringStation',
        on_delete=models.CASCADE,
        )                       # Added 20170807 Added to have the same date for diferents stations register
        # IMECA Values
        imecaO3 = models.DecimalField(null=True, max_digits=6, decimal_places=2) # 0.00 For the imecas
        imecaNO = models.DecimalField(null=True, max_digits=6, decimal_places=2)
        imecaNO2 = models.DecimalField(null=True, max_digits=6, decimal_places=2)
        imecaNOX = models.DecimalField(null=True, max_digits=6, decimal_places=2)
        imecaSO2 = models.DecimalField(null=True, max_digits=6, decimal_places=2)
        imecaCO = models.DecimalField(null=True, max_digits=6, decimal_places=2)
        imecaPM10 = models.DecimalField(null=True, max_digits=6, decimal_places=2)
        imecaPM25 = models.DecimalField(null=True, max_digits=6, decimal_places=2)
        def setFecha(self, year, month):
                """Set the Date of the IMECA without the Day"""
                self.fecha = dateutil.parser.parse(year + "-" + month + "-" + "01") # Corrected Bug here 20170806

        def getFecha(self):
                return self.__str__()
        
        def __str__(self):
                """Function to represent the model"""
                return str(self.fecha.year) + "-" + str(self.fecha.month)
        class Meta:             # Added 20170807
                """Class to hold constraints of the database, espesificaly to enforce the rule of the unique convination of fecha and idStation: Have a unique date register per monitoring station"""
                unique_together = ("idStation", "fecha")


class  ImecaDataHour(models.Model): # Added 20170812
        """Hold the IMECA data for each Hour """ 
        fecha = models.DateTimeField() # Of each Hour 
        idStation = models.ForeignKey(
        'investigacion.MonitoringStation',
        on_delete=models.CASCADE,
        )                       
        # IMECA Values
        imecaO3 = models.DecimalField(null=True, max_digits=6, decimal_places=2) # 0.00 For the imecas
        imecaNO = models.DecimalField(null=True, max_digits=6, decimal_places=2)
        imecaNO2 = models.DecimalField(null=True, max_digits=6, decimal_places=2)
        imecaNOX = models.DecimalField(null=True, max_digits=6, decimal_places=2)
        imecaSO2 = models.DecimalField(null=True, max_digits=6, decimal_places=2)
        imecaCO = models.DecimalField(null=True, max_digits=6, decimal_places=2)
        imecaPM10 = models.DecimalField(null=True, max_digits=6, decimal_places=2)
        imecaPM25 = models.DecimalField(null=True, max_digits=6, decimal_places=2)
        def setFecha(self, year, month, day, hour):
                """Set the Date of the IMECA without the Day"""
                self.fecha = dateutil.parser.parse(year + "-" + month + "-" + day + " " + hour + ":00") # Parse the DateTimeField giving to each hour 0 minutes

        def getFecha(self):
                return self.__str__()
        
        def __str__(self):
                """Function to represent the model"""
                return str(self.fecha.year) + "-" + str(self.fecha.month) + "-" + str(self.fecha.day) + " " + str(self.fecha.hour) + ":00" # The last string is to give the number of each hour an hour format
        class Meta:             
                """Class to hold constraints of the database, espesificaly to enforce the rule of the unique combination of fecha and idStation: Have a unique date register per monitoring station"""
                unique_together = ("idStation", "fecha")
        
                
