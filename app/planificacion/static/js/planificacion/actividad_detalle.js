$("#eliminar-presupuesto").click(function () {
    presupuesto_eliminar($(this));
});

function presupuesto_eliminar(evento) {
    /**
     * llamado ajax para eliminar un presupuesto
     */
    $.ajax({
        url: '/planificacion/presupuesto/eliminar/' + evento.data('id'),
        type: 'DELETE',
        success: function () {
            mensaje_exito("El presupuesto ha sido eliminado");
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