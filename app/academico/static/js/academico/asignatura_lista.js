$(function () {
    initDataTable();
});

function initDataTable(){
    table = $('#asignatura').DataTable({
        "processing": true,
        "serverSide": true,
        "stateSave": true,
        "order": [[0, "asc"], [1, "asc"], [2, "asc"]],
        "ajax": {
            "url": "/academico/asignatura/lista-paginador",
            "type": "POST",
            "error": function (error) {
                mensaje_error(error.responseText);
            }
        },
        "columns": [
            {"data": "nombre", render: function ( data, type, row ) {
                return '<a href="/academico/asignatura/detalle/' + row.id +'">' + data + '</a>';
            }},
            {"data": "codigo_unesco"},
            {"data": "tipo"},
        ],
        "language": {"url": "/static/plugins/datatables/es.js"}
    });
}


