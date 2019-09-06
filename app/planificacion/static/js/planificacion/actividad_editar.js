$(document).ready(function(){
    $("#peso-fijo").change();
});

$("#peso-fijo").change(function() {
    //$("#peso").attr('required', !$(this).is(':checked'));
   var div_avance = $("div.peso");
    if($(this).is(':checked')){
        div_avance.show();
        $("#peso").attr('required', true);
    } else {
        div_avance.hide();
        $("#peso").removeAttr('required');
    }
});