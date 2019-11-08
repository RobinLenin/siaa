/**
 * Esconde el modal de dirección editar, y muestra una alerta si la solicitud se ejecuto con éxito.
 * @param {string} message, el mensaje que se va a mandar en el alert.
 * @param {boolean} isGood, si es true se mostrara un success alert, caso contrario un danger alert.  
 */
function hideModal(message, isGood, idModal){
    operation = isGood ? 'success' : 'danger';
    
    $(`#${idModal}`).modal('hide');

    $('#message').append(`<div class='alert alert-${operation}' id='current_message' role='alert'> ${message} </div>`);               
    
    /* Eliminamos el mensaje de alerta luego de 3 segundos */
    setTimeout(function(){
        $('#current_message').remove();
    }, 3000);
}