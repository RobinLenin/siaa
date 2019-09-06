$(document).ready(function () {
    $("#tipo-programa").change();
    $("#regimen").change();
});

$("#tipo-programa").change(function () {
    let es_curso_apoyo = $(this).data("tipo-apoyo") === $(this).val();

    if (es_curso_apoyo) {
        $("#tipo_formacion").val("");
        $("#campo_detallado").val("").trigger('change');
    }

    $("#tipo_formacion").prop("disabled", es_curso_apoyo);
    $("#campo_detallado").prop("disabled", es_curso_apoyo);

    $("#tipo_formacion").prop("required", !es_curso_apoyo);
    $("#campo_detallado").prop("required", !es_curso_apoyo);

});

$("#regimen").change(function () {
    let tipo_formacion_id =  $("#tipo_formacion").data('tipo-formacion-id');
    $('#tipo_formacion').children('option:not(:first)').remove();

    if ($(this).val()) {
        $.ajax({
            type: 'GET',
            url: '/academico/tipo-formacion/' + $(this).val(),
            success: function (data) {
                for (let i in data) {
                    let item = data[i];
                    $("#tipo_formacion").append(new Option(item['display_nombre'], item['id']));
                    if (tipo_formacion_id == item['id']){
                        $("#tipo_formacion").val(tipo_formacion_id);
                    }
                }
            },
            error: function () {
                mensaje_error("No se pudo consultar los tipos de formación");
                $(this).addClass("error");
            }
        });
    }
});

$(function () {
    $('#form-programa-estudio').validate(
        {
            rules: {
                "codigo_institucional": {
                    remote: {
                        url: '/core/validar/campo-unico/',
                        type: 'POST',
                        data: {
                            'app': 'academico',
                            'modelo': 'ProgramaEstudio',
                            'atributo': 'codigo_institucional',
                            'valor': function () {
                                return $('#codigo_institucional').val();
                            },
                            'id': function () {
                                return $('#id').val();
                            }
                        }
                    }
                },
                "codigo_senescyt": {
                    remote: {
                        url: '/core/validar/campo-unico/',
                        type: 'POST',
                        data: {
                            'app': 'academico',
                            'modelo': 'ProgramaEstudio',
                            'atributo': 'codigo_senescyt',
                            'valor': function () {
                                return $('#codigo_senescyt').val();
                            },
                            'id': function () {
                                return $('#id').val();
                            }
                        }
                    }
                },
            },
            messages: {
                "codigo_institucional": {
                    remote: "Código institucional duplicado"
                },
                "codigo_senescyt": {
                    remote: "Código Senescyt duplicado"
                }
            }
        });
});