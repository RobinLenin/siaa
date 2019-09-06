$(".eliminar").click(function () {
    $(this).attr("disabled", "disabled");
    plan_estrategico_eliminar($(this));
});

function plan_estrategico_eliminar(boton) {
    $.ajax({
        url: '/planificacion/plan-estrategico/eliminar/' + boton.data('id'),
        type: 'DELETE',
        success: function (data) {
            $(boton).parents('tr').fadeOut(300, function () {
                $(this).remove();
            });
            mensaje_exito('El plan ha sido eliminado!');
        },
        error: function (xhr) {
            mensaje_error("Error al eliminar el plan " + xhr.responseText);
        },
        complete: function () {
            $(boton).removeAttr("disabled");
        }
    });
}

