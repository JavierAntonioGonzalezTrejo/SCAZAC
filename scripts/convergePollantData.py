import math
import sys
import pandas
def appendColumn(index, nonValue, goodColumn, badColumn, newColumn):
    """The file has 2 columns for a spesific pollant or atmosferic value, each column has valueble information in the form of Integers but when a register has the error mesurment value (144 or 0) the other column on the same register has the good value. This function will put all the 'good values' on one column"""
    if goodColumn[index] == nonValue:
        newColumn.append(badColumn[index])
    elif math.isnan(goodColumn[index]):
        newColumn.append(0)
    else:
        newColumn.append(goodColumn[index])


        
data = pandas.read_csv(sys.argv[1], low_memory=False)
sizeData = len(data["Date_Time"])    
Temp= []
O3= []
CO = []
NO = []
NO2 =[]
NOX = []
SO2 = []
TempAmbiente = []
RH = []
WS = []
WD = []
PresionBaro = []
RadSolar = []
Precipitacion = []
PM10 = []
PM25 = [] 


for i in range(0, sizeData):
    appendColumn(i, 144, data["Temp"], data["Temp Estado"], Temp)
    appendColumn(i, 144, data["O3 Estado"], data["O3"], O3)
    appendColumn(i, 144, data["CO"], data["CO Estado"], CO)
    appendColumn(i, 0, data["NO Estado"], data["NO"], NO)
    appendColumn(i, 144, data["NO2 Estado"], data["NO2"], NO2)
    appendColumn(i, 144, data["NOX"], data["NOX Estado"], NOX)
    appendColumn(i, 144, data["SO2 Estado"], data["SO2"], SO2)
    appendColumn(i, 144, data["Temp  Ambiente Estado"], data["Temp  Ambiente"], TempAmbiente)
    appendColumn(i, 144, data["R/H"], data["R/H Estado"], RH)
    appendColumn(i, 144, data["WS"], data["WS Estado"], WS)
    appendColumn(i, 144, data["WD Estado"], data["WD"], WD)
    appendColumn(i, 144, data["Presion Baro Estado"], data["Presion Baro"], PresionBaro)
    appendColumn(i, 144, data["Rad Solar Estado"], data["Rad Solar"], RadSolar)
    appendColumn(i, 144, data["Precipitacion"], data["Precipitacion Estado"], Precipitacion)
    appendColumn(i, 144, data["PM10 Estado"], data["PM10"], PM10)
    appendColumn(i, 144, data["PM2.5 Estado"], data["PM2.5"], PM25)

total = 0
for i in range(0, sizeData):
    O3[i] = O3[i] / 1000
    CO[i] = CO[i] / 1000
    NO[i] = NO[i] / 10000
    NO2[i] = NO2[i] / 1000
    NOX[i] = NOX[i] / 1000
    SO2[i] = SO2[i] / 1000
    PM10[i] = PM10[i] / 10.0
    PM25[i] = PM25[i] /10.0

cantidad = range(sizeData)
newData = pandas.DataFrame(
    {'Fecha' : data["Date_Time"],
     'Temp' : Temp,
     'O3' : O3,
     'CO' : CO,
     'NO' : NO,
     'NO2' : NO2,
     'NOX' : NOX,
     'SO2' : SO2,
     'TempAmbiente' : TempAmbiente,
     'RH' : RH,
     'WS' : WS,
     'WD' : WD,
     'PresionBaro' : PresionBaro,
     'RadSolar' : RadSolar,
     'Precipitacion' : Precipitacion,
     'PM10' : PM10,
     'PM2.5': PM25}, index = cantidad)
newData[['Fecha', 'Temp', 'O3', 'CO', 'NO', 'NO2', 'NOX', 'SO2', 'TempAmbiente', 'RH', 'WS', 'WD', 'PresionBaro', 'RadSolar', 'Precipitacion', 'PM10', 'PM2.5']].to_csv('out.csv', index=False)
