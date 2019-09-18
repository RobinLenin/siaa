$(function () {
    savePerson();
});

/**
 * Guarda una nueva Persona
 */
function savePerson(){
    $('#formPersona').submit(function(e){
        e.preventDefault();
        
        $.ajax({
            type : 'POST',
            url : '/core/persona/guardar_nuevo',
            data : {
                numero_documento: $('#numero_documento').val(),
                primer_nombre : $('#primer_nombre').val(),
                segundo_nombre : $('#segundo_nombre').val(),
                primer_apellido : $('#primer_apellido').val(),
                segundo_apellido : $('#segundo_apellido').val(),
                correo_electronico : $('#correo_electronico').val(),
                csrfmiddlewaretoken : $('input[name=csrfmiddlewaretoken]').val()
            },
            success : function(data){      
 
                hideModal(data['mensaje'], true);
            },
            error : function(data){
                hideModal(data['mensaje'], false);
            }
        });
    });
}

/**
 * Esconde el modal, y muestra un mensaje de información con un alert, si la solicitud
 * se ha ejecutado con éxito o no. 
 * @params isGood --> True si la operación se ha ejecutado con éxito.
 */

 function hideModal(message, isGood){
    operation = isGood ? 'success' : 'danger';
    
    $('#modal-persona-editar').modal('hide');
    $('#message').append(`<div class='alert alert-${operation}' id='current_message' role='alert'> ${message} </div>`);
 
    setTimeout(function(){
        $('#current_message').remove();
    }, 3000);
}

