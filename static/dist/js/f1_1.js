//Localition of the first Monitoring station: 22.774808, -102.574710
// Crea un mapa 
//Refactorizar esta funcion para usar Jquery
function initMap() {
    var map;
    map = new google.maps.Map(document.getElementById('map'), {
	zoom: ampliacion,
	center: new google.maps.LatLng(22.7744958,-102.5770257), 
    })   
    for (var st in station) {
	// Añade cada circulo de cada estación.
	createMonitoringPlace(st, station, map);
    }

    
};


// Crea circulos y funciones de evente mediante cerraduras.
// Los eventos contendra al contaminante mas grande solamente.
// LOG: BUG 001 CORREGIDO: TODOS LOS MENSAJES EN EL MAPA REDIRECCIONABAN A LA MISMA ESTACION (20170705)
function createMonitoringPlace(st, station, map){
    var maxPollantIndex, colorInfoPollant, namePolant, stationCircle, airQualityDesc, monitoringPlaceName, opacity, map, weight, fOpacity, scolor, infoWindow;
    opacity = 0.8;		// Opacidad de la linea limitante del circulo
    weigth = 2;			// Peso de la linea delimitante del circulo 
    fOpacity = 0.35;			// Opacidad del relleno del circulo
    scolor = 'white';			// Color de la linea delimitante del circulo
    infoWindow = new google.maps.InfoWindow(); // PopUp que aparecer cada que se acerque algun centro de monitoreo
    maxPollantIndex = getHigherImecaIndex(station[st].pollantImeca);
    colorInfoPollant = airQuality(station[st].pollantImeca[maxPollantIndex]).color;
    
    stationCircle = new google.maps.Circle({
	strokeColor: scolor,
	strokeOpacity: opacity,
	strokeWeight: weight,
	fillColor: colorInfoPollant,
	fillOpacity: fOpacity,
	map: map,
	center: station[st].center,
	radius: station[st].radius,
    });
  
    
    // Crea un cuadro de informacion con los siguientes datnos:
    // Nombre del lugar que se monitorea, nombre del contaminante que afecta el luagar, descripcion del estado que aflije a ese lugar, imeca del contaminante
    google.maps.event.addListener(stationCircle, 'mouseover', function(event){
	infoWindow.setContent("<p> " + station[st].nameMonitoringPlace + "<br />Contaminante: " + station[st].pollantName[maxPollantIndex] + "<br />Estado del aire: " + airQuality(station[st].pollantImeca[maxPollantIndex]).quality + "<br />IMECA: " + station[st].pollantImeca[maxPollantIndex] + "<br /> Fecha: " + station[st].day + "/" + station[st].month + "/" + station[st].year); // Usando un tag p y un br se pueden insertar multiples lineas. Modificado el 20170708
	infoWindow.setPosition(new google.maps.LatLng(station[st].center.lat, station[st].center.lng));
	infoWindow.open(map, this);
    });
    // Cierra el cuadro de información
    google.maps.event.addListener(stationCircle, 'mouseout', function(){
	infoWindow.close();
    });
}

// Calcula el estado de la calidad del aire de la zona de monitoreo con respecto al contaminante
// mas peligroso (Con el imaca mas grande)
function airQuality(imeca){
    if(0 <= imeca && imeca <= 50)	// Buena calidad del aire
	return {color : 'green', quality: "Buena"};
    else if(50 < imeca && imeca <= 100) // Calidad regular del aire
	return {color : 'yellow', quality: "Regular"};
    else if(100 < imeca && imeca <= 150) // Calidad mala del aire
	return {color : 'orange', quality: "Mala"};
    else if(150 < imeca && imeca <= 200) // Calidad muy mala del aire
	return {color : 'red', quality: "Muy Mala"};
    else if(200 < imeca)			// Calidad extremadamente Mala del aire
	return {color : 'purple', quality: "Extremadamente Mala"};
    return {color : 'black', quality: "Mantenimiento"};
};

var ArrayMath = {
    max: function(values) {
	var i, maxValue;
	maxValue = 0;
	for(i = 0; i < values.length; i++)
	    if(maxValue < values[i])
		maxValue = values[i];
	return maxValue;

    }
}

// Obtener la localización del contaminante mas grande
// Para utilizarlo en En la pagina respectivamente
function getHigherImecaIndex(arrayImeca){
    var max = ArrayMath.max(arrayImeca);
    return arrayImeca.indexOf(max);
}

//Requerimento funcional F1-1-03
$(function(){
    var highestPollant;
    highestPollant = getHighestPollant(station);
    $("#descAir").text("Calidad del aire: " + highestPollant.description.toUpperCase());
    $("#pollant").text("Contaminante: " + highestPollant.pollant);
    $("#imeca").text("Índice: " + highestPollant.imeca);
    $("#place").text("Estación: " + highestPollant.place);
    $("#registerDate").text("Fecha: " + highestPollant.day + "/" + highestPollant.month + "/" + highestPollant.year); // Agregado el 20170708
});

//Funcion diseñada para obtener el contaminante mas peligroso que es monitoreado por todos las estaciones
//administradas
function getHighestPollant(jsonStation){
    var pollantIndex, pollantStation, i, highPollantImeca, airQualityDesc;
    highPollantImeca = 0;
    for(var st in jsonStation){
	for(i = 0; i < jsonStation[st].pollantImeca.length; i++){
	    if(highPollantImeca < jsonStation[st].pollantImeca[i]){
		highPollantImeca = jsonStation[st].pollantImeca[i];
		pollantIndex = i;
		pollantStation = st;
	    }
	}
    }
    airQualityDesc = airQuality(highPollantImeca);
    return {description: airQualityDesc.quality, pollant: jsonStation[pollantStation].pollantName[pollantIndex],imeca: highPollantImeca,
	    place: jsonStation[pollantStation].nameMonitoringPlace, year: jsonStation[pollantStation].year, month: jsonStation[pollantStation].month, day: jsonStation[pollantStation].day}; // Modificado el 20170708
}
