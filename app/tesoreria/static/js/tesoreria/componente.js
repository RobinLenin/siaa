$('[data-toggle="tooltip"]').tooltip();
// guardo los botones agregar, editar ,eliminar de cada td, para utilizarlos
var actions = '<div class="btn-group">' +
              '<a class="add btn btn-outline-success btn-xs" title="Guardar" data-toggle="tooltip"><i class="fa fa-check"></i></a>' +
              '<a class="edit btn btn-outline-info btn-xs" title="Editar" data-toggle="tooltip"><i class="fa fa-edit"></i></a>' +
              '</div>';
$(document).on("click", ".add", function () {
    var empty = false;
    var input = $(this).parents("tr").find('input[type="number"]');
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
        var td_value;
        input.each(function () {
            td_value = $(this).val();
            // si es tabla con links hago un link
            if ($(this).parents("table").hasClass('linked')) {
                td_value = $(this).val().trim();
            }
            //$(this).parent("td").html(td_value).addClass('duracion');
        });
        // fila.find(".add, .edit").toggle();
        guardar_item(fila, input.val().trim(),input);
    }
});
// POST para guardar la duracion de un item
function guardar_item(fila, duracion, input) {
    var parent = fila.parents(".padre-item").first();
    $.ajax({
        type: 'POST',
        url: parent.data('guardar-url'),
        data : {
            'id': fila.data('id'),
            'duracion': duracion
        },
        success: function (data) {
            mensaje_exito("Item guardado correctamente");
            $('#asignatura-nivel-duracion').html(data.asignatura_duracion);
            $('#duracion').val(data.asignatura_duracion);
            fila.find(".add, .edit").toggle();
            input.parent("td").html(input.val()).addClass('duracion');
            $(this).removeClass("error");
        },
        error: function () {
            mensaje_error("No se pudo guardar el item");
            $(this).addClass("error");
        },
        complete: function () {
        }
    });
}
// Edit row on edit button click('
$(document).on("click", ".edit", function () {
        $(this).parents("tr").find("td.duracion").each(function () {
        $(this).html('<input type="number" min="0" max="99" step="1" class="form-control" value="' + $(this).text().trim() + '">');
    });
    $(this).parents("tr").find(".add, .edit").toggle();
});