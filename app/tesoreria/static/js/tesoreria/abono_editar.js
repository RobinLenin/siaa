



$(document).ready(function(){
    $("#referencia").hide();
    $("#labelreferencia").hide();
    $("#forma_pago").change(function(){

    var selectedCountry = $(this).children("option:selected").val();
    if(selectedCountry == "E"){
    $("#referencia").hide();
    $("#labelreferencia").hide();
    }else{
    $("#referencia").show();
    $("#labelreferencia").show();
    }
    });

});

