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
                mensaje_error(error.responseText, segundos=20 );
            }
        },
        "columns": [
            {"data": "id"},
            {"data": "fecha"},
            {"data": "tasa"},
        ],
        "language": {"url": "/static/plugins/datatables/es.js"}
    });
}


