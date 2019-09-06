$(".editar-oe").click(function () {
    $("#objetivo_estrategico_id").val($(this).data('id'));
    $("#objetivo_nombre").val($(this).data('nombre'));
    $("#objetivo_codigo").val($(this).data('codigo'));
    $("#modal-objetivo-estrategico").modal();
});
$(".eliminar-oe").click(function () {
    objetivo_estrategico_eliminar($(this));
});

$('#modal-objetivo-estrategico').on('hidden.bs.modal', function () {
    $("#objetivo_estrategico_id").val("");
    $("#objetivo_nombre").val("");
    $("#objetivo_codigo").val("");
});


function objetivo_estrategico_eliminar(boton) {
    $.ajax({
        url: '/planificacion/objetivo-estrategico/eliminar/'+boton.data('id'),
        type: 'DELETE',
        success: function () {
            mensaje_exito("Objetivo eliminado");
            $(boton).parents('tr').fadeOut(300, function () {
                $(this).remove();
            });
        },
        error: function () {
            mensaje_error("No se pudo eliminar el objetivo");
        },
        complete: function () {
        }
    });
}