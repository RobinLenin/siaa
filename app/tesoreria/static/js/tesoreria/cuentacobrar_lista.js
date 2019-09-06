$(function () {
    initDataTable();
});

function initDataTable(){
    table = $('#cuenta_cobrar').DataTable({
        "processing": false,
        "serverSide": true,
        "stateSave": true,
        "order": [[0, "asc"], [1, "asc"], [2, "asc"]],
        "ajax": {
            "url": "/tesoreria/cuenta_cobrar/cuenta_cobrar_lista_paginador",
            "type": "POST",
            "error": function (error) {
                mensaje_error(error.responseText);
            }
        },
        "columns": [
            {"data": "id", render: function ( data, type, row ) {
                return '<a href="/tesoreria/cuenta_cobrar/detalle/' + row.id +'">' + data + '</a>';
            }},
            {"data": "cliente"},
            {"data": "monto"},
            {"data": "saldo"},
        ],
        "language": {"url": "/static/plugins/datatables/es.js"}
    });
}


