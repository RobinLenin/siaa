$(".eliminar-oo").click(function () {
    objetivo_operativo_eliminar($(this));
});

function objetivo_operativo_eliminar(evento) {
    /**
     * llamado ajax para eliminar un resultado
     */
    $.ajax({
        url: '/planificacion/objetivo-operativo/eliminar/' + evento.data('id'),
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