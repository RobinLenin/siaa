$(function () {
    savePerson();
});
/**
* Guarda una nueva Persona
*/
function savePerson() {

    let formPersona = $('#formPersona').validate(
        {
            rules: {
                "numero_documento": {
                    remote: {
                        url: '/core/validar/numero-documento/',
                        type: 'POST',
                        data: {
                            'numero_documento': function () {
                                return $('#numero_documento').val();
                            },
                            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
                        },
                        dataFilter: function (data) {
                            if (data === 'true') {
                                asignar_campos();
                                return '"true"';
                            } else {
                                limpiar_campos();
                                return "\"" + data + "\"";
                            }
                        }
                    }
                },
            }
        }
    );

    $('#modal_btn_guardar').click(function (e) {
        if (formPersona.valid() && $('#numero_documento').valid()) {
            e.preventDefault();
            $.ajax({
                type: 'POST',
                url: '/core/persona/basico_guardar',
                data: {
                    idPersona: $('#idPersona').val(),
                    next_persona: $('#next_persona').val(),
                    correo_electronico: $('#correo_electronico').val(),
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
                },
                success: function (data) {
                    $('#modal-persona-editar').modal('hide');
                }
            });
        }
    });
}

async function asignar_campos() {
    numero_documento_value = $('#numero_documento').val()
    let { persona } = await get_persona(numero_documento_value);

    $('#primer_nombre').val(persona.primer_nombre);
    $('#segundo_nombre').val(persona.segundo_nombre);
    $('#primer_apellido').val(persona.primer_apellido);
    $('#segundo_apellido').val(persona.segundo_apellido);
    $('#correo_electronico').val(persona.correo_electronico);
    $('#idPersona').val(persona.id);
}

function limpiar_campos() {
    $("#primer_nombre").val('');
    $("#segundo_nombre").val('');
    $("#primer_apellido").val('');
    $("#segundo_apellido").val('');
    $("#correo_electronico").val('');
    $('#idPersona').val('');
}

async function get_persona(cedula) {
    let persona = await $.ajax({
        type: 'GET',
        url: `/core/persona/crear_basico/${cedula}`
    });

    return persona;
}
