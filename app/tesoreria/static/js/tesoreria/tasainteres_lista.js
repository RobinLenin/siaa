$(function () {
    initDataTable();
});

function initDataTable(){
    table = $('#tasainteres').DataTable({
        "processing": false,
        "serverSide": true,
        "stateSave": true,
        "order": [[0, "asc"], [1, "asc"], [2, "asc"]],
        "ajax": {
            "url": "/tesoreria/tasa_interes/lista-paginador",
            "type": "POST",
            "error": function (error) {
                mensaje_error(error.responseText, segundos=5 );
            }
        },
        "columns": [
            {"data": "id", render: function ( data, type, row ) {
                return '<a href="/tesoreria/tasa_interes/detalle/' + row.id +'">' + data + '</a>';
            }},
            {"data": "fecha"},
            {"data": "tasa"},
        ],
        "language": {"url": "/static/plugins/datatables/es.js"}
    });
}


