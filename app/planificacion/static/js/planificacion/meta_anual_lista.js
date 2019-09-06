$(".eliminar-meta").click(function () {
    meta_anual_eliminar($(this));
});

function meta_anual_eliminar(evento) {
    /**
     * llamado ajax para eliminar una meta
     */
    $.ajax({
        url: '/planificacion/meta-anual/eliminar/' + evento.data('id'),
        type: 'DELETE',
        success: function () {
            mensaje_exito("La meta ha sido eliminada");
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