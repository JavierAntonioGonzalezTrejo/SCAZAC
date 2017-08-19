


> Written with [StackEdit](https://stackedit.io/)
## Scripts ##

1. Scripts temporales.
 Los siguietes scripts son temporales y representan funcionalidades que seran implementadas en la aplicación de administración, por lo que se funcionalidad puede ser incompleta o vaga.
 - convergePollantData.py: Caso de uso muy espesifico usado en la creacióndel sistema.
 - temporaryIMECAf1_2Insertion.py: Utilizado para calcular promedios para unidades de dia y hora para el requerimento descrito.
 - temporaryIMECAf1_6Insertion.py: Utilizado para calcular promedios para la unidad de hora para el requerimiento descrito.
 - temporaryInsertDataScazac.py: Utilizado para insertar datos provenientes de un archivo csv a la base de datos de la aplicación. Debe de entregarse como unico argumento el id de la estación a la que pertenecen los datos. A continuacion se mostrara el nombre de las columnas y la estructura de los datos que debe de contener.
	 - fecha: YYYY/MM/DD HH:MM:SS, por lo regular se recuperan datos en multiplos de 5 (Cada 5, 10, 20 y 30 minutos)
	 - Temp: En grados centigrados, se refiere a la temperatura interna de la estación de monitoreo
	 - O3: Medido en ppm
	 - CO: Medido en ppm
	 - NO: Medido en ppm
	 - NO2: Medido en ppm
	 - NOX: Medido en ppm
	 - SO2: Medido en ppm
	 - TempAmbiente: En grados centigrados, se refiere a la temperatura a fuera de la estación de monitoreo
	 - RH: 
	 - WS: TBD
	 - WD: TBD
	 - PresionBaro: Presion Barometrica, medido en Pa (N/m²)
	 - RadSolar: TBD
	 - Precipitacion: Cantidad de agua que cae al llover, medido en mm
	 - PM10: Partículas Menores a 10 Micras, medido en µg/m3
	 - PM2.5: Partículas Menores a 2.5 Micras µg/m3
 - temporaryInsertStations.py: Datos de la estación dentro del script con excepcion del id (Entero), el cual debe ser entregado como parte del unico argumento del script.
 - Se recomienda la utilización de los scripts en el siguiente orden:
  temporaryInsertStations.py, temporaryInsertDataScazac.py, temporaryIMECAf1_2Insertion.py y temporaryIMECAf1_6Insertion.py 
 ----------
2. Los siguientes scripts son para la automaticación de instalación y utilización del sistema en OS's Windows utilizando Cywing aunque pueden ser utiliados en cualquier otro sistema operativo.
 - windowsScazac.sh: Utilizado para preparar e instalar el sistema, localizar en el directorio home del usuario para su utilización.
 - updateMigrateRunScazac.sh: Utilizado para iniciar el sistema de forma automatica al abrir una terminal de cualquier sistema operativo, para esto primero actualiza la base de datos del sistema con cambios realizados en git por el desarrollador del mismo y finalmente inicializar el mismo. Localizar el script en el directorio del sistema.
 