$("button.eliminar").click(function () {
    resultado_eliminar($(this));
});

function resultado_eliminar(evento) {
    /**
     * llamado ajax para eliminar un resultado
     */

    var boton = evento;
    $.ajax({
        url: '/planificacion/resultado/eliminar/' + evento.data('id'),
        type: 'DELETE',
        success: function () {
            mensaje_exito("El elemento ha sido eliminado");
            $(evento).parents('tr').fadeOut(300, function () {
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
