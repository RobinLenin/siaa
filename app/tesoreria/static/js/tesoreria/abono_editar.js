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

    $("#fecha_pago").change(function(){
    var cuenta_cobrar_id = $("#id_cuenta").val();
    var fecha = $("#fecha_pago").val();
    var saldo = 0.0;

        $.ajax({
            method: "GET",
            url: "/tesoreria/cuenta_cobrar/abonos/calcular",
            data: {cuenta_cobrar_id: cuenta_cobrar_id,
                    fecha : fecha}
        }).done(function (msg) {
            saldo = parseFloat(msg.saldo);
            saldo = saldo.toFixed(2);
            //alert(saldo);
            $(".monto").attr({
                "max" : saldo,
                "placeholder"  : saldo
            });
            $("#deuda").val(saldo);
         });

    });



});








