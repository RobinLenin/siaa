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

    /*$("#fecha_pago").change(function(){
    var fecha_pago = $("#fecha_pago").val();
    var aux_f = String(fecha_pago).split("-");
    var anio_f = aux_f[0];
    var mes_f = aux_f[1];
    var dias_f = aux_f[2];
    var saldo = parseFloat($("#saldo").html());
    var interes = 0.0;
    var dias_interes = 0.0;
    $('#tabla tr').each(function(){

        var celdas = $(this).find('td');
        //alert("algo es"+ $(celdas[2].html()));

        fecha_int_mensual  =  $(celdas[1]).html();
        aux = String(fecha_int_mensual).split("-");
        anio = aux[0];
        mes = aux[1];

        valor = $(celdas[3]).html();

        if (anio <= anio_f && mes < mes_f) {
            interes = parseFloat(interes) + parseFloat(valor);

        }

        if (anio == anio_f && mes == mes_f){


                var dias_mes = daysInMonth(mes, anio);
                dias_interes = (parseFloat(valor) / parseFloat(dias_mes)) *  parseFloat(dias_f);
                dias_interes = parseFloat(dias_interes.toFixed(2));
         }



    });
    var saldo_total = interes + saldo + dias_interes;
    $("input").attr({
       "max" : saldo_total
    });
    $("#deuda").val(saldo_total);



    });

    function daysInMonth(humanMonth, year) {
    return new Date(year || new Date().getFullYear(), humanMonth, 0).getDate();
    }
 */
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








