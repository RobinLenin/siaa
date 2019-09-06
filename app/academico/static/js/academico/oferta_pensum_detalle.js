$(document).ready(function () {
    $(document).on("click", ".agregar-oferta-asignatura", function () {
        if( ! $(this).hasClass("disabled")){
            oferta_asignatura_guardar($(this));
        }
    });
    $("a.agregar-oferta-asignatura:not(.disabled)>span").hide();
    $("a.agregar-oferta-asignatura>span").text("Ofertada"); // muestro aqui el texto para que no parpadee al renderizar
});



function oferta_asignatura_guardar(evento) {
    /**
     * llamado ajax para guardar una oferta-asignatura-nivel
     */
    $.ajax({
        url: "/academico/oferta-asignatura-nivel/guardar",
        data: {
            "asignatura_nivel": evento.data("asignatura-nivel-id"),
            "oferta_pensum": evento.data("oferta-pensum-id"),
        },
        type: "POST",
        success: function (data) {
            mensaje_exito("Asignatura ofertada");
            var tr_row = "<tr>";
            var row = tr_row +
                '<td>' + evento.data("asignatura-nombre") + '</td>' +
                '<td>' + evento.data("nivel-nombre") + '</td>' +
                '<td><button data-oferta-asignatura-nivel-id="'+ data.id + '" data-asignatura-nivel-id="'+evento.data("asignatura-nivel-id")+'"' +
                ' title="Eliminar" class="btn btn-outline-danger eliminar-oferta-asignatura"' +
                ' onclick="return confirm(\'¿Está seguro de eliminar el registro?\')" >' +
                ' <i class="fa fa-trash-o"></i></button></td>'+
                "</tr>";
            var table = $("#tabla-ofertadas");
            table.append(row);
            $(evento).addClass("disabled").find("span").fadeIn("slow");
        },
        error: function (xhr) {
            mensaje_error(xhr.statusText);
        },
        complete: function () {
        }
    });
}

$(document).on("click", ".eliminar-oferta-asignatura", function () {
    oferta_asignatura_eliminar($(this));
});

function oferta_asignatura_eliminar(evento) {
    /**
     * llamado ajax para eliminar una oferta pensum
     */
    $.ajax({
        url: "/academico/oferta-asignatura-nivel/eliminar/"+ evento.data("oferta-asignatura-nivel-id"),
        type: "DELETE",
        success: function (data) {
            mensaje_exito("Eliminado!");
            $("#asignatura-nivel-"+evento.data("asignatura-nivel-id")).removeClass("disabled").find("span").fadeOut("slow");
            evento.parents("tr").remove();
        },
        error: function (xhr) {
            mensaje_error(xhr.statusText);
        },
        complete: function () {
        }
    });
}