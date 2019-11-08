$(function () {
    saveDirection();
});

/**
 * Guarda una nueva dirección para una persona, solo si el formulario es valido
 */
function saveDirection() {
    
    let formDireccion = $('#formDireccion');

    $('#btn_modal_direccion').click((e)=>{
        /* Verifica que el formulario sea válido */
        if(formDireccion.valid()){
            e.preventDefault();
            /* Petición AJAX para guardar la dirección de la persona */
            $.ajax({
                type : 'POST',
                url : `/core/direccion/basico_guardar/${get_id_persona()}`,
                /* Se manda como data la información del form */
                data : formDireccion.serialize(),
                success : function(data){    
                        if(data['reload_page']){
                            hideModal(data['mensaje'], data['success'], 'modal-direccion-editar');
                        }
                }
            });
        }
    });
}

/**
 * Obtiene el Id de la persona a guardar la dirección.
 */
function get_id_persona(){
    let idPersona = $('#idPersona').val();
    return idPersona;
}

