$(function () {
    loadSelect();
});

function loadSelect(){
    $(".select2").select2(default_options_select());
}


function showModal(){
    $('#modal-persona-editar').modal('show'); 
    $('select.select2').select2("close");
}

async function actualizar_data_select(current_id_select, idSelect){

    let data;
    let value_select = $(`#${idSelect}`).val();
    if(value_select !== ''){
        data = await obtener_personas(current_id_select, value_select);
    }
    else{
        data =  await obtener_personas(current_id_select);
    }

    data_personas = personsData(data.personas);

    return data_personas;
}

/**
 * Escuchar cambios en los select2
 */

 $('#administrador').on('select2:select', async function(e){
   
    let id_administrador_seleccionado = e.params.data.id;

    let new_data_personas = await actualizar_data_select(id_administrador_seleccionado, 'contratista');

    cambiar_data_select('fiscalizador', new_data_personas);

    new_data_personas = await actualizar_data_select(id_administrador_seleccionado, 'fiscalizador');

    cambiar_data_select('contratista', new_data_personas);
 });


$('#fiscalizador').on('select2:select', async function(e){
    let id_fiscalizador_seleccionado = e.params.data.id;
   
    let new_data_personas = await actualizar_data_select(id_fiscalizador_seleccionado, 'contratista');

    cambiar_data_select('administrador', new_data_personas);

    new_data_personas = await actualizar_data_select(id_fiscalizador_seleccionado, 'administrador');

    cambiar_data_select('contratista', new_data_personas);
});



$('#contratista').on('select2:select', async function(e){
    let id_contratista_seleccionado = e.params.data.id;

    let new_data_personas = await actualizar_data_select(id_contratista_seleccionado, 'fiscalizador');

    cambiar_data_select('administrador', new_data_personas);
    
    new_data_personas = await actualizar_data_select(id_contratista_seleccionado, 'administrador');

    cambiar_data_select('fiscalizador', new_data_personas);
});



async function obtener_personas(id1, id2 = null){

    let get_url = '';
    
    if(id1 === '' && id2 !== null){
        get_url =  `/poliza/poliza/persona_lista/?id1=${id2}`;
    }else{
        get_url = `/poliza/poliza/persona_lista/?id1=${id1}`;
    }
    get_url = id2 !== null ? `${get_url}&&id2=${id2}` : get_url;

     let data = await $.ajax({
        url : get_url,
        type: 'GET'
     });
     return data;
}

function cambiar_data_select(idSelect, data_personas){
    let current_value = $(`#${idSelect}`).val();

    $(`#${idSelect}`).empty();
    
    $(`#${idSelect}`).select2(default_options_select(data_personas)).val(current_value).trigger('change');    
}

function update_data_before_save(data_personas){

    cambiar_data_select('fiscalizador', data_personas);

    cambiar_data_select('contratista', data_personas);

    cambiar_data_select('administrador', data_personas);
}


function default_options_select(data_adicional = null){
    let opciones = {
        allowClear: true,
        closeOnSelect : true,
        escapeMarkup: function (markup) { return markup; },
        language: {
            noResults: function () {
                
                button = `No existe la persona
                            <button class='btn btn-block btn-sm btn-primary'
                            onclick='showModal()'>
                                <iclass='fa fa-save'>
                                </i>Ingresar Persona
                         </button>`
                
                return button;
           }
       }
    }

    if(data_adicional!== null){
        opciones.data = data_adicional;
    }
    return opciones;
}
