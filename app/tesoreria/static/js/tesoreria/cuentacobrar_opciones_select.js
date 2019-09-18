$(function () {
    loadSelect();
});

/**
 * Carga las opciones por defecto de los select2.
 */
function loadSelect(){
    $(".select2").select2(default_options_select());
}

/**
 * Muestra el modal, y esconde el select.
 * Método realizado porque al abrir el modal el select2 se quedaba abierto.
 */
function showModal(){
    $('#modal-persona-editar').modal('show'); 
    $('select.select2').select2("close");
}

/**
 * Opciones por defecto de los select2.
 */
function default_options_select(){
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
       },
       ajax: {
        url: '/core/persona/listar_momentaneo/',
        data: function (params) {
          var query = {
            search: params.term,
            page: params.page || 1
          }
          return query;
        },
        processResults : function(data, params){           

            params.page = params.page || 1;

            console.log(data);

            return {
              results : $.map(data.personas, function(persona){
                return {
                    id : persona.id,
                    text : persona.primer_nombre + ' ' + persona.primer_apellido
                }
              }),
              pagination: {
                more: (params.page) < data.limite
              }
            }
        }    
      }
    }   
    return opciones;
}

