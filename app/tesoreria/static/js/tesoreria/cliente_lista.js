$(function () {
    initDataTable();
});

function initDataTable(){
    table = $('#cliente').DataTable({
        "processing": true,
        "serverSide": true,
        "stateSave": true,
        "order": [[0, "asc"], [1, "asc"], [2, "asc"]],
        "ajax": {
            "url": "/tesoreria/cliente/lista-paginador",
            "type": "POST",
            "error": function (error) {
                mensaje_error(error.responseText);
            }
        },
        "columns": [
            {"data": 'numero_documento', render: function ( data, type, row ) {
                return '<a href="/tesoreria/cliente/informacion_detallada/' + row.id +'">' + data + '</a>';
            }},
            {"data": 'primer_apellido'},
            {'data': 'primer_nombre'},
            {'data': 'correo_electronico'},
        ],
        "language": {"url": "/static/plugins/datatables/es.js"}
    });
}
