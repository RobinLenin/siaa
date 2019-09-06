$(".editar-inscripcion").click(function () {
    $("#modal-inscripcion-id").val($(this).data('id')).attr('name', 'inscripcion_id');
    $("input[name='inscripcion_producto']").val($(this).data('producto'));
    $("input[name='inscripcion_presentacion']").val($(this).data('presentacion'));
    $("input[name='inscripcion_dosis_base']").val($(this).data('dosis-base'));
    $("input[name='inscripcion_via']").val($(this).data('via'));
    $("input[name='inscripcion_dosificacion']").val($(this).data('dosificacion'));
    $("input[name='inscripcion_frecuencia']").val($(this).data('frecuencia'));
    $("input[name='inscripcion_duracion']").val($(this).data('duracion'));
    $("#modal-inscripcion-tratamiento").modal();
});

$('#modal-inscripcion-tratamiento').on('hidden.bs.modal', function () {
    $("#modal-inscripcion-id").val("").removeAttr("name");
    $("input[name='inscripcion_producto']").val("");
    $("input[name='inscripcion_presentacion']").val("");
    $("input[name='inscripcion_dosis_base']").val("");
    $("input[name='inscripcion_via']").val("");
    $("input[name='inscripcion_dosificacion']").val("");
    $("input[name='inscripcion_frecuencia']").val("");
    $("input[name='inscripcion_duracion']").val("");
    
   
    $("form2").trigger('reset');
});