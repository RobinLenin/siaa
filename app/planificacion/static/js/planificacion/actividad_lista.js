$(".eliminar-actividad").click(function () {
    actividad_eliminar($(this));
});

function actividad_eliminar(evento) {
    /**
     * llamado ajax para eliminar una meta
     */
    $.ajax({
        url: '/planificacion/actividad/eliminar/' + evento.data('id'),
        type: 'DELETE',
        success: function () {
            mensaje_exito("La actividad ha sido eliminada");
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