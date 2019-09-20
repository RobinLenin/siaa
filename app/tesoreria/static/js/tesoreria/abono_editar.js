$(document).ready(function(){
    $("#referencia").hide();
    $("#labelreferencia").hide();
    $("#forma_pago").change(function(){

    var selectedCountry = $(this).children("option:selected").val();
    if(selectedCountry != "Efectivo"){
    $("#referencia").show();
    $("#labelreferencia").show();
    }else{
    $("#referencia").hide();
    $("#labelreferencia").hide();

    }
    });

});

