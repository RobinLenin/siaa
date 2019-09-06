$(function(){
    $('#form-vincular').validate();

    $('#numero_documento').on('keyup blur', function () {
        $('#verificar').prop('disabled', this.value.trim().length < 5);
        // $('#guardar-cuenta').attr('disabled', 'disabled');
    });

    $('#numero_documento').change(function(){
        verificar();
    });

    $('#verificar').click(function () {
        verificar();
    });

    $('#vincular-cuenta').click(function () {
        vincular();
    });

    initDataTable();

});

function verificar(){
    $('#verificar i').addClass('fa fa-refresh fa-spin');
    $('#guardar-cuenta').attr('disabled', 'disabled');

    var numero_documento = $('#numero_documento').val();
    if (numero_documento.length === 10){
        $.ajax({
        url: '/seguridad-informacion/cuenta-correo/consultar-numero-documento/'+numero_documento,
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        type: 'GET',
        success: function (data) {
                $("#nombres").val(data.nombres);
                $("#apellidos").val(data.apellidos);
                if (data.email_institucional !== false){
                    $("#email_institucional").val(data.email_institucional);
                }else{
                    mensaje_notificacion(data.mensaje);
                }

                if (data.crear === true){
                    $('#guardar-cuenta').removeAttr('disabled');
                }

        },error: function (xhr) {
            mensaje_error("No se cargó la información" + xhr.responseText);

        },
        complete: function () {
             //$('#guardar-cuenta').removeAttr('disabled');
             $('#verificar i').removeClass('fa fa-refresh fa-spin');
        }

        });
    }
    else {
        mensaje_notificacion('Al parecer no es un numero de cédula, ingrese manualmente la información.', 5)
    }
}

function vincular(){
    var v = $('#form-vincular').valid();
    if (v){
        $('#form-vincular').submit();
    }
}

function dividir_nombres_completos(nombres_completos) {
    concatenadores = ["de", "del", "la", "las", "los", "san", "mac", "mc", "van", "von", "y", "i"];
    compuesto = '';
    nueva_cadena = '';
    nombres_s = nombres_completos.trim().split(' ');
    for (var k = 0; k < nombres_s.length; k++) {
        i = nombres_s[k];
        if (concatenadores.includes(i.toLowerCase())) {


            compuesto = compuesto + i + ' ';
        } else {
            if (nueva_cadena === '') {
                nueva_cadena = compuesto + i
            } else {
                nueva_cadena = nueva_cadena + '|' + compuesto + i;
            }
            compuesto = '';
        }
    }
    nueva_cadena = nueva_cadena.split('|');
    segundo_nombre = '';
    segundo_apellido = '';
    if (nueva_cadena.length >= 3) {
        primer_apellido = nueva_cadena[0];
        segundo_apellido = nueva_cadena[1];
        primer_nombre = nueva_cadena[2];
        segundo_nombre = nombres_completos.replace(primer_apellido, '').replace(segundo_apellido,
            '').replace( primer_nombre, '').trim();
        } else{
        primer_apellido = nombres_completos[0];
        primer_nombre = nombres_completos[1];
    }
    return [primer_apellido, segundo_apellido, primer_nombre, segundo_nombre];

};

function initDataTable(){
    table = $('#cuentas').DataTable({
        "processing": true,
        "serverSide": true,
        "stateSave": true,
        "order": [[2, "asc"]],
        "ajax": {
            "url": "/seguridad-informacion/cuenta-correo/lista-paginador/",
            "type": "POST",
            "data": function ( d ) {
                d.sTipo = "otroFiltro";
            }
        },
        "columns": [
            {"data": "numero_documento"},
            {"data": "apellidos"},
            {"data": "nombres"},
            {"data": "email_institucional", render: function ( data, type, row ) {
                return '<a href="/seguridad-informacion/cuenta-correo/detalle/'+ row.id + '">' + data + '</a>';
            }},
            {"data": "tipo"},
        ],
        "language": {"url": "/static/plugins/datatables/es.js"}
    });
}