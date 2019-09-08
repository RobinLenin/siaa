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
            "url": "/tesoreria/cuenta_cobrar/lista-paginador",
            "type": "POST",
            "error": function (error) {
                mensaje_error(error.responseText, segundos=50 );
            }
        },

        "columns": [
        {"data": "id",},
        {"data": "ci", render: function ( data, type, row ) {
                return '<a href="/tesoreria/cuenta_cobrar/detalle/' + row.id +'">' + data + '</a>';
            }},
          {"data": "cliente"},
            {"data": "monto"},
            {"data": "saldo"},
            {"data":"estado"},
        ],
        "language": {"url": "/static/plugins/datatables/es.js"}
    });
}


