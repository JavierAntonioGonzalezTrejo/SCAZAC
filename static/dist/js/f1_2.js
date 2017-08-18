// Created 20170807
/* Added 20170725 */
/* Used to hide day or month depending of which range of time the user whants to show imecas for. 
   Dia: All select Active.
   Mes: Only Year and Month active.
   Year: Only Year select acvite.
*/
function hideRangeForm(){
    switch($("#range").val()){
    case "1" : $("#day").show();
	$("#day").val("01");
	$("#idDay").show();
	$("#month").show();
	$("#month").val("01");
	$("#idMonth").show();
	break;
    case "2" : $("#day").hide();
	$("#idDay").hide();
	$("#day").val("");
	$("#month").show();
	$("#idMonth").show();
	$("#month").val("01");
	break;
    case "3" : $("#day").hide();
	$("#day").val("");
	$("#idDay").hide();
	$("#month").hide();
	$("#month").val("");
	$("#idMonth").hide();
	break;
    }
}

/* Funcion para seleccionar cuantos dias dependiendo del mes */
function hideDaysMonth(){
    switch($("#month").val()){
    case "01" :
    case "03" :
    case "05" : 
    case "07" :
    case "08" :
    case "10" :
    case "12" : $("#feb29").show();
	$("#feb30").show();
	$("#all31").show();
	break;
    case "04" :
    case "06" :
    case "09" :
    case "11" : $("#feb29").show();
	$("#feb30").show();
	$("#all31").hide();
	break;
    case "02": var numberYear = Number($("#year").val());
	if(numberYear % 4 == 0 && numberYear % 100 != 0 || numberYear % 400 == 0)
	{
	    $("#feb29").show();
	    $("#feb30").hide();
	    $("#all31").hide();
	}
	else
	{
	    $("#feb29").hide();
	    $("#feb30").hide();
	    $("#all31").hide();
	}
	break;
    }
}
/* Color the imeca celds depending on the holded value */
$(function(){
    
    for(i = 0; i < $(".imeca-data").length; i++){
	
	$(".imeca-data").eq(i).css("background",airQuality($(".imeca-data").eq(i).text()).color );
    }
});
$(hideDaysMonth);
$(hideRangeForm);

$("#range").change(hideRangeForm);
$("#month").change(hideDaysMonth);

function airQuality(imeca){/* Rewrited the function in order to use colors more nice to the eye 20170807*/
    if(0 <= imeca && imeca <= 50)	// Buena calidad del aire
	return {color : '#61FF3D', quality: "Buena"};
    else if(50 < imeca && imeca <= 100) // Calidad regular del aire
	return {color : 'yellow', quality: "Regular"};
    else if(100 < imeca && imeca <= 150) // Calidad mala del aire
	return {color : 'orange', quality: "Mala"};
    else if(150 < imeca && imeca <= 200) // Calidad muy mala del aire
	return {color : '#FF5B5B', quality: "Muy Mala"};
    else if(200 < imeca)
	return {color : '#BC84F0', quality: "Extremadamente Mala"};
    return {color : 'white', quality: "Mantenimiento"};
};
