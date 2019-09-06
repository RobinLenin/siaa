$(document).ready(function(){
    $("#meta-medible").change();
    $("#meta-porcentaje").change();
});

$("#meta-medible").change(function() {
    var meta_v = $(".meta-valor");
    var meta_p = $(".meta-porcentaje");
    if($(this).is(':checked')){
        meta_p.show();
        meta_v.show();
        $("#meta-valor").attr('required', true);
    } else {
        meta_p.hide();
        meta_v.hide();
        $("#meta-valor").removeAttr('required');
    }
});

$("#meta-porcentaje").change(function() {
    var porcentaje_tag = $(".porcentaje-tag");
    var meta_v = $("#meta-valor");
    if($(this).is(':checked')){
        porcentaje_tag.show();
        meta_v.attr('max',100)
    } else {
        porcentaje_tag.hide();
        meta_v.removeAttr('max')
    }
});