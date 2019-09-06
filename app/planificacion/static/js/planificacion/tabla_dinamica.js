$('[data-toggle="tooltip"]').tooltip();
// guardo los botones agregar, editar ,eliminar de cada td, para utilizarlos
var actions = '<div class="btn-group">' +
              '<a class="add btn btn-outline-success btn-xs" title="Guardar" data-toggle="tooltip"><i class="fa fa-check"></i></a>' +
              '<a class="edit btn btn-outline-info btn-xs" title="Editar" data-toggle="tooltip"><i class="fa fa-edit"></i></a>' +
              '<a class="delete btn btn-outline-danger btn-xs" title="Eliminar" data-toggle="tooltip"><i class="fa fa-trash-o"></i></a>' +
              '</div>';

$(".add-new").click(function () {
    $(this).attr("disabled", "disabled");
    // creo un tr con el mismo tipo de dato
    var tr_row = '<tr>';
    var row = tr_row +
        '<td><input type="text" class="form-control"></td>' +
        '<td>' + actions + '</td>' + '</tr>';
    var table = $(this).parents('div.padre-item').first().find("table." + $(this).data('tipo'));
    var index = table.find("tbody tr:last-child").index();
    table.append(row).find("tbody tr").eq(index + 1).find(".add, .edit").toggle();
    $('[data-toggle="tooltip"]').tooltip();
});

$(document).on("click", ".add", function () {
    var empty = false;
    var input = $(this).parents("tr").find('input[type="text"]');
    input.each(function () {
        if (!$(this).val()) {
            $(this).addClass("error");
            empty = true;
        } else {
            $(this).removeClass("error");
        }
    });
    var fila = $(this).parents("tr");
    fila.find(".error").first().focus();
    if (!empty) {
        input.each(function () {
            var td_value = $(this).val();
            // si es tabla con links hago un link
            if ($(this).parents("table").hasClass('linked')) {
                td_value = '<a class="item_link">' + $(this).val().trim() + '</a>';
            }
            $(this).parent("td").html(td_value);
        });
        fila.find(".add, .edit").toggle();
        guardar_item(fila, input.val().trim());
    }
});
// POST para guardar el nombre de un item
function guardar_item(fila, nombre) {
    var parent = fila.parents(".padre-item").first();
    $.ajax({
        type: 'POST',
        url: parent.data('guardar-url'),
        data : {
            [parent.data('padre-tipo')] : parent.data('padre-id'),
            'id': fila.data('id'),
            'nombre': nombre
        },
        success: function (data) {
            $(fila).data("id", data.item_id); // guardo id en la fila correspondiente (cuando es nuevo)
            $(".add-new").removeAttr("disabled");
            var tabla =fila.parents("table");
            if ($(tabla).hasClass('linked')) {
                $(fila).find("a.item_link").attr('href', $(tabla).data('item_link') + data.item_id)
            }
            mensaje_exito("Item guardado correctamente");
        },
        error: function () {
            mensaje_error("No se pudo guardar el item");
        },
        complete: function () {
        }
    });
}

// Edit row on edit button click('
$(document).on("click", ".edit", function () {
    $(this).parents("tr").find("td:not(:last-child)").each(function () {
        $(this).html('<input type="text" class="form-control" value="' + $(this).text().trim() + '">');
    });
    $(this).parents("tr").find(".add, .edit").toggle();
    $(".add-new").attr("disabled", "disabled");
});
// Delete row on delete button click
$(document).on("click", ".delete", function () {
    var fila = $(this).parents("tr");
    if( typeof(fila.data('id')) !== 'undefined'){
        eliminar_item(fila);
    }
    fila.remove();
    $(".add-new").removeAttr("disabled");

});
function eliminar_item(fila) {
    var parent = fila.parents(".padre-item").first();
    $.ajax({
        type: 'DELETE',
        url: parent.data('eliminar-url') +fila.data('id'),
        success: function () {
            mensaje_exito("Item eliminado!");
        },
        error: function () {
            mensaje_error("No se pudo eliminar el item");
        },
        complete: function () {
        }
    });
}
