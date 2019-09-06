$(function(){
    initDataTable();
});

function initDataTable(){
    table = $('#programas_estudio').DataTable({
        "processing": true,
        "serverSide": true,
        "stateSave": true,
        "order": [[0, "asc"], [1, "asc"], [2, "asc"]],
        "ajax": {
            "url": "/academico/programa-estudio/lista-paginador",
            "type": "POST",
            "error": function (error) {
                mensaje_error(error.responseText);
            }
        },
        "columns": [
            {"data": "facultad"},
            {"data": "nombre", render: function ( data, type, row ) {
                return '<a href="/academico/programa-estudio/detalle/'+ row.id + '">' + data + '</a>';
            }},
            {"data": "modalidad"},
        ],
        "language": {"url": "/static/plugins/datatables/es.js"}
    });
}