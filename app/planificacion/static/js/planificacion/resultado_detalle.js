$("button.editar").click(function () {
    /**
     * al hacer clic en el boton editar de un resultado,
     * lleno el modal con los datos
     * @type {*|jQuery}
     */
    var fila = $(this).parents('td');
    $("#resultado-id").val(fila.data('id')).attr('name', 'id');
    $("#nombre").val(fila.data("nombre"));
    $("#codigo").val(fila.data("codigo"));
    $("#select-puestos").val(fila.data('responsables')).change();
    $("#agregar-resultado").modal();
});

$('#agregar-resultado').on('hidden.bs.modal', function () {
    /**
     * al cerrar modal limpio sus campos
     * si se agrega nuevo resultado, éstos estarán vacíos
     */
    $("#nombre").val("");
    $("#codigo").val("");
    $("#resultado-id").val('').removeAttr('name');
    $("#select-puestos").val('').change();
});


function resultado_eliminar(evento) {
    /**
     * llamado ajax para eliminar un resultado
     */

    var boton = evento;
    $.ajax({
        url: '/planificacion/resultado/eliminar/' + boton.data('id'),
        type: 'DELETE',
        success: function (mensaje) {
            mensaje_exito(mensaje);
            $(boton).parents('.div-resultado').fadeOut(300, function () {
                $(this).remove();
            });
        },
        error: function (xhr) {
            mensaje_error(xhr.statusText);
        },
        complete: function () {
        }
    });
}
