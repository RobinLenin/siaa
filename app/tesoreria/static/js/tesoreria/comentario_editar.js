$(document).ready(function () {
    $("#buscar").on("keyup", function () {
        var value = $(this).val().toLowerCase();
        $("#pensums-list .programa").filter(function () {
            $(this).toggle($(this).data("carrera").toLowerCase().indexOf(value) > -1)
        });
    });
    $(document).on("click", ".agregar-pensum", function () {
        if (!$(this).hasClass("disabled")) {
            oferta_pensum_guardar($(this));
        }

    });
    $("#fecha_inicio").change();
});



function oferta_pensum_guardar(evento) {
    /**
     * llamado ajax para guardar una oferta pensum
     */
    $.ajax({
        url: "/academico/oferta-pensum/guardar",
        data: {
            "oferta_academica": evento.data("oferta-academica-id"),
            "pensum": evento.data("pensum-id"),
        },
        type: "POST",
        success: function (data) {
            mensaje_exito("Pensum agregado");
            $(evento).addClass("disabled");

            var tr_row = "<tr>";
            var row = tr_row +
                '<td>' + evento.data("programa") + '</td>' +
                '<td>' + evento.data("pensum") + '</td>' +
                '<td><button data-oferta-pensum-id="'+ data.id + '" data-pensum-id="'+evento.data("pensum-id")+'"' +
                ' title="Eliminar" class="btn btn-outline-danger eliminar-oferta-pensum"' +
                ' onclick="return confirm(\'¿Está seguro de eliminar el registro?\')" >' +
                ' <i class="fa fa-trash-o"></i></button></td>'+
                "</tr>";
            var table = $("#tabla-pensums");
            //var index = table.find("tbody tr:last-child").index();
            table.append(row);


        },
        error: function (xhr) {
            mensaje_error(xhr.statusText);

        },
        complete: function () {
        }
    });
}


$(document).on("click", ".eliminar-oferta-pensum", function () {
    oferta_pensum_eliminar($(this));
});

function oferta_pensum_eliminar(evento) {
    /**
     * llamado ajax para eliminar una oferta pensum
     */
    $.ajax({
        url: "/academico/oferta-pensum/eliminar/" + evento.data("oferta-pensum-id"),
        type: "DELETE",
        success: function (data) {
            mensaje_exito("Eliminado!");
            $("#pensum_" + evento.data("pensum-id")).removeClass("disabled");
            evento.parents("tr").remove();
        },
        error: function (xhr) {
            mensaje_error(xhr.statusText);
        },
        complete: function () {
        }
    });
}

$(document).on("click", ".periodo-matricula-crear", function () {
    /**
     * Abre el modal editar periodo matrícula invocado desde detalle de oferta academica para crear.
     * Limpia los valores de los campos
     */
    document.getElementById("periodo-matricula-tipo").value = '';
    document.getElementById("periodo-matricula-fecha-inicio").value = '';
    document.getElementById("periodo-matricula-fecha-fin").value = '';
});


$(document).on("click", ".periodo-matricula-editar", function () {
    /**
     * Abre el modal editar periodo matrícula invocado desde detalle de oferta academica para editar. Se realiza desde
     * javascript por lo que la acción editar esta en la misma interfaz de detalle oferta academica.
     */
    var data = $(this);
    document.getElementById("periodo-matricula-oferta-academica").value = data.attr("data-oferta-academica-id");
    document.getElementById("periodo-matricula-id").value = data.attr("data-periodo-matricula-id");
    document.getElementById("periodo-matricula-tipo").value = data.attr("data-periodo-matricula-tipo");
    document.getElementById("periodo-matricula-fecha-inicio").value = data.attr("data-periodo-matricula-fecha-inicio");
    document.getElementById("periodo-matricula-fecha-fin").value = data.attr("data-periodo-matricula-fecha-fin");
    $("#modal-periodo-matricula-editar").modal("show");
});


$(".fecha").change(function () {
    /**
     * Calcula de acuerdo a las fechas ininio y fin el estado de la oferta académica, INACTIVO, ACTIVO, CERRADO
     */
    let f_inicio = $("#fecha_inicio").val();
    let f_fin = $("#fecha_fin").val();
    let estado = 'INACTIVO';

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
                    estado = 'ACTIVO';
                }else if(fin < hoy){
                     estado = 'CERRADO';
                }
            }
        }
    }
    $("#label_estado").html(estado);
    $("#estado").val(estado);
});
