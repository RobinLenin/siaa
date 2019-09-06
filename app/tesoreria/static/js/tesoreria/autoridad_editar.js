$(document).ready(function () {
    $("#fecha_inicio").change();
    $("div.estado").hide();
});

$(".fecha").change(function () {
    let f_inicio = $("#fecha_inicio").val();
    let f_fin = $("#fecha_fin").val();
    let estado =  false;

    //No requerido referencia de salida
    $("#referencia_salida").prop("required", false);
    $("label[for=referencia_salida]").html("<label>Referencia de salida:</label>");
    $("#referencia_salida" ).blur();

    if (f_inicio !== "") {
        let inicio = new Date(f_inicio + "T05:00:00Z");
        let hoy = new Date();
        if (f_fin !== "") {
            let fin = new Date(f_fin + "T05:00:00Z");
            // aumento un dia para ser inclusivo
            fin.setDate(fin.getDate() + 1);
            if (Object.prototype.toString.call(inicio) === "[object Date]"
                && Object.prototype.toString.call(fin) === "[object Date]"
                && !isNaN(inicio.getTime())
                && !isNaN(fin.getTime())) {
                if (inicio <= hoy && hoy <= fin) {
                    estado = true;
                }
            }
            //Requerido referencia de salida
            $("#referencia_salida").prop("required", true);
            $("label[for=referencia_salida]").html("<label><span class='error'>(*) </span>Referencia de salida:</label>");

        } else if (Object.prototype.toString.call(inicio) === "[object Date]" && !isNaN(inicio.getTime()) && hoy >= inicio) {
            estado = true;
        }
    }
    $("#label_activo").html(estado ? " Activo":" Inactivo").toggleClass("text-success", estado);
    $("#activo").prop("checked", estado);
});
