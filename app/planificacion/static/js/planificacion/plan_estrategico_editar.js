$(document).ready(function () {
    $.validator.addClassRules({
        periodos: {
            maxperiodos: 5
        },
    });
    $.validator.addMethod('maxperiodos', function(value, element) {
        return value.length <=5;
    },"Selecciones 5 o menos")
});
