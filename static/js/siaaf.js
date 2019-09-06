//Inicializa componentes, variables, controles de forma automática
$(function () {
    $('[data-toggle="popover"]').popover();
    $('.select2').select2({'width': "100%"});

    $(".datepicker").datepicker({
        changeMonth: true,
        changeYear: true
    });

    $('.auto-validate').each(
        function() {
              $(this).validate()
        }
    );
});


// Traducción al español
$(function ($) {
    $.datepicker.regional['es'] = {
        closeText: 'Cerrar',
        prevText: '<Ant',
        nextText: 'Sig>',
        currentText: 'Hoy',
        monthNames: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
        monthNamesShort: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
        dayNames: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
        dayNamesShort: ['Dom', 'Lun', 'Mar', 'Mié', 'Juv', 'Vie', 'Sáb'],
        dayNamesMin: ['Do', 'Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sá'],
        weekHeader: 'Sm',
        dateFormat: 'yy-mm-dd',
        firstDay: 1,
        isRTL: false,
        showMonthAfterYear: false,
        yearSuffix: '',
        minDate: -32874,
        maxDate: 0
    };
    $.datepicker.setDefaults($.datepicker.regional['es']);
});

// para Alertify
alertify.defaults.transition = "slide";
alertify.defaults.theme.ok = "btn btn-primary";
alertify.defaults.theme.cancel = "btn btn-danger";
alertify.defaults.theme.input = "form-control";

function mensaje_error(mensaje, segundos = 2) {
    alertify.error(mensaje, segundos);
}

function mensaje_exito(mensaje, segundos = 2) {
    alertify.success(mensaje, segundos);
}

function mensaje_notificacion(mensaje, segundos = 2) {
    alertify.notify(mensaje, 'notificacion', segundos);
}
