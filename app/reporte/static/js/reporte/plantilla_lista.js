$('[data-toggle="tooltip"]').tooltip();
// guardo los botones agregar, editar ,eliminar de cada td, para utilizarlos
var actions = '<button class="btn btn-success btn-xs guardar" data-toggle="tooltip"><i class="fa fa-check"></i></button>' +
    ' <button class="btn btn-primary btn-xs editar" data-toggle="tooltip"><i class="fa fa-pencil"></i></button>' +
    ' <button class="btn btn-warning btn-xs duplicar" data-toggle="tooltip"><i class="fa fa-copy"></i></button>' +
    ' <button class="btn btn-danger btn-xs eliminar" data-toggle="tooltip"><i class="fa fa-trash-o"></i></button>' +
    '<a class="btn btn-default btn-xs exportar" data-toggle="tooltip" href="/reporte/plantilla/exportar" ' +
    ' <i class="fa fa-download "></i></a>';

$(".agregar_fila").click(function () {
    $(this).attr("disabled", "disabled");
    // creo un tr con el mismo tipo de dato
    var tr_row = '<tr>';
    var row = tr_row +
        '<td class="plantilla_descripcion"><input type="text" class="form-control"></td>' +
        '<td class="plantilla_codigo"><input type="text" class="form-control"></td>' +
        '<td>' + actions + '</td>' + '</tr>';
    var table = $("#lista_plantillas");
    var index = table.find("tbody tr:last-child").index();
    table.append(row).find("tbody tr").eq(index + 1).find(".guardar, .editar").toggle();
    $('[data-toggle="tooltip"]').tooltip();
    table.find("tbody tr:last-child input").first().focus();
});


// Edit row on edit button click('
$(document).on("click", ".editar", function () {
    $(this).parents("tr").find("td:not(:last-child)").each(function () {
        $(this).html('<input type="text" class="form-control" value="' + $(this).text().trim() + '">');
    });
    $(this).parents("tr").find(".guardar, .editar").toggle();
    $(".agregar_fila").attr("disabled", "disabled");
});

// eliminar fila, si no tiene id se elimina directamente.
$(document).on("click", ".eliminar", function () {
    var fila = $(this).parents("tr");
    if (typeof (fila.data('plantilla_id')) === "undefined") {
        fila.remove();
        $(".agregar_fila").removeAttr("disabled")
    } else {
        var mensaje = '<div class="card card-box">\n' +
            '    <div class="card-head">\n' +
            '        <header>\n' +
            '            Seguro desea eliminar la plantilla?\n' +
            '        </header>\n' +
            '    </div>\n' +
            '    <div class="card-body">' +
            '       Confirme si no está siendo utilizada.!!' +
            '   </div></div>';
        alertify.confirm('Advertencia', mensaje, function () {
            eliminar_item(fila);
            $(".agregar_fila").removeAttr("disabled");
        }, function () {
            alertify.notify('Cancelado', 'notificacion', 2);
        }).set({labels: {ok: 'Acceptar', cancel: 'Cancelar'}, padding: false});

    }
});

function eliminar_item(fila) {
    $.ajax({
        type: 'DELETE',
        url: '/reporte/plantilla/eliminar/' + fila.data('plantilla_id'),
        success: function () {
            fila.remove();
            alertify.success("Item eliminado!");
        },
        error: function () {
            alertify.error("No se pudo eliminar el item");
        },
        complete: function () {
        }
    });
}

/**
 * Metodo para guardar los cambios en los input al editar un elemento.
 */
$(document).on("click", ".guardar", function () {
    var empty = false;
    var fila = $(this).parents("tr");
    var input = fila.find('input[type="text"]');
    input.each(function () {
        if (!$(this).val()) {
            $(this).addClass("error");
            empty = true;
        } else {
            $(this).removeClass("error");
        }
    });

    fila.find(".error").first().focus();
    if (!empty) {
        input.each(function () {
            var td_value = $(this).val();
            var celda = $(this).parent("td");
            // si es tabla con links hago un link
            if (celda.hasClass('plantilla_descripcion')) {
                td_value = '<a class="item-link">' + $(this).val().trim() + '</a>';
            }
            celda.html(td_value);
        });
        fila.find(".guardar, .editar").toggle();
        guardar_item(fila);
    }
});

/**
 * Realizar POST cuando se edita la descripcion o codigo de un reporte
 * @param fila
 */
function guardar_item(fila) {
    $.ajax({
        type: 'POST',
        url: '/reporte/plantilla/guardar-datos',
        data: {
            'plantilla_id': fila.data('plantilla_id'),
            'descripcion': fila.find('td.plantilla_descripcion a').text(),
            'codigo': fila.find('td.plantilla_codigo').text(),
            'origen_id': fila.data('origen_id'),
        },
        success: function (data) {
            $(fila).data("plantilla_id", data.id); // guardo id en la fila correspondiente (cuando es nuevo)
            $(".agregar_fila").removeAttr("disabled");
            $(fila).find("a.item-link").attr('href', "/reporte/plantilla/detalle/" + data.id);
            $(fila).find("a.exportar").attr('href', "/reporte/plantilla/exportar/" + data.id);
            alertify.success("Item guardado correctamente.");
        },
        error: function (xhr) {
            fila.find('.editar').click();
            alertify.error(xhr.responseText);
        },
        complete: function () {
        }
    });
}


$(document).on("click", ".duplicar", function () {
    var fila = $(this).parents("tr");
    $(".agregar_fila").click();
    var duplicada = $("tbody tr:last-child");
    duplicada.data('origen_id', fila.data('plantilla_id'));
});
