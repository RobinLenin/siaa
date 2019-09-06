// Función inicilizadora y realiza la petición ajax para obtener los Países
$(function () {
    var myData = {};

    if ($('#parroquia_id').attr('value')) {
        $.ajax({
            method: "GET",
            url: window.location.origin + "/api/v1/core/parroquia-lista",
            data: {}
        }).done(function (msg) {
            myData.data = msg.data;
            var select = document.getElementById('parroquia_id');
            for (var i = 0; i < myData.data.length; i++) {
                var opt = document.createElement('option');
                opt.name = myData.data[i]['id'];
                opt.value = myData.data[i]['id'];
                opt.innerHTML = myData.data[i]['nombre'].concat(' (', myData.data[i]['canton__nombre'], '-', myData.data[i]['canton__provincia__nombre'], '-', myData.data[i]['canton__provincia__pais__nombre'], ')');
                if (myData.data[i]['id']==$('#parroquia_id').attr('value')){
                    opt.selected = true;
                }
                select.appendChild(opt);
            }
        });

    } else {

        limpiaSelect('#provincia_id');
        limpiaSelect('#canton_id');
        limpiaSelect('#parroquia_id');

        document.getElementById('provincia_id').disabled = true;
        document.getElementById('canton_id').disabled = true;
        document.getElementById('parroquia_id').disabled = true;

        $.ajax({
            method: "GET",
            url: window.location.origin + "/api/v1/core/pais-lista",
            data: {}
        })
            .done(function (msg) {
                myData.data = msg.data;
                var select = document.getElementById('pais_id');
                for (var i = 0; i < myData.data.length; i++) {
                    var opt = document.createElement('option');
                    opt.name = myData.data[i]['id'];
                    opt.value = myData.data[i]['id'];
                    opt.innerHTML = myData.data[i]['nombre'];
                    select.appendChild(opt);
                }
            });

    }
});

// Realiza la petición ajax para obtener las provincias de acuerdo al País
$("#pais_id").change(function () {

    limpiaSelect('#provincia_id');
    limpiaSelect('#canton_id');
    limpiaSelect('#parroquia_id');

    if ($('#pais_id').val().trim() != '') {

        document.getElementById('provincia_id').disabled = false;
        var pais_id = $("#pais_id option:selected").val();
        var myData = {};

        $.ajax({
            method: "GET",
            url: window.location.origin + "/api/v1/core/provincia-lista-por-pais",
            data: {pais_id: pais_id}
        }).done(function (msg) {
            myData.data = msg.data;
            var select = document.getElementById('provincia_id');
            for (var i = 0; i < myData.data.length; i++) {
                var opt = document.createElement('option');
                opt.value = myData.data[i]['id'];
                opt.innerHTML = myData.data[i]['nombre'];
                select.appendChild(opt);
            }
        });

    } else {
        document.getElementById('provincia_id').disabled = true;
        document.getElementById('canton_id').disabled = true;
        document.getElementById('parroquia_id').disabled = true;
    }
});

// Realiza la petición ajax para obtener los cantones de acuerdo a la Provincia
$("#provincia_id").change(function () {

    limpiaSelect('#canton_id');
    limpiaSelect('#parroquia_id');

    if ($('#provincia_id').val().trim() != '') {
        document.getElementById('canton_id').disabled = false;

        var provincia_id = $("#provincia_id option:selected").val();
        var myData = {};

        $.ajax({
            method: "GET",
            url: window.location.origin + "/api/v1/core/canton-lista-por-provincia",
            data: {provincia_id: provincia_id}
        }).done(function (msg) {
            myData.data = msg.data;
            var select = document.getElementById('canton_id');
            for (var i = 0; i < myData.data.length; i++) {
                var opt = document.createElement('option');
                opt.value = myData.data[i]['id'];
                opt.innerHTML = myData.data[i]['nombre'];
                select.appendChild(opt);
            }
        });

    } else {
        document.getElementById('canton_id').disabled = true;
        document.getElementById('parroquia_id').disabled = true;
    }
});

// Realiza la petición ajax para cargar los datos de la parroquia de acuerdo al País, Provincia, Cantón
$("#canton_id").change(function () {
    var canton_id = $("#canton_id option:selected").val();
    if (($('#canton_id').val().trim() !== '') && ($('#provincia_id').val().trim() !== '') && ($('#pais_id').val().trim() !== '')) {
        document.getElementById('parroquia_id').disabled = false;
    } else {
        document.getElementById('parroquia_id').disabled = true;
    }
    var myData = {};

    limpiaSelect('#parroquia_id');

    $.ajax({
        method: "GET",
        url: window.location.origin + "/api/v1/core/parroquia-lista-por-canton",
        data: {canton_id: canton_id}
    })
        .done(function (msg) {
            myData.data = msg.data;
            var select = document.getElementById('parroquia_id');
            for (var i = 0; i < myData.data.length; i++) {
                var opt = document.createElement('option');
                opt.value = myData.data[i]['id'];
                opt.innerHTML = myData.data[i]['nombre'];
                select.appendChild(opt);
            }
        });
});


// Limpia el campo alternativo de parroquia en caso de seleccionar una
$("#parroquia_id").change(function () {
    $("#id_parroquia_otro").val('');
});


// Limpia los select cuando existe un cambio
function limpiaSelect(id_select) {
    $(id_select)
        .find('option')
        .remove()
        .end()
        .append('<option value="">-----</option>')
        .val('')
    ;
}

// En caso de ingresar una parroquia diferente, el campo parroquia lo limpio y selecciona 'Otro' si existe
$("#id_parroquia_otro").keyup(function () {
    if ($("#parroquia_id").find('option:selected').text() != 'Otro') {
        document.form.parroquia.selectedIndex = "0";
        var select = document.getElementById('parroquia_id');
        for (var i = 0; i < select.length; i++) {
            var opt = select[i];
            if (opt.text === 'Otro') {
                $("#parroquia_id > option[value=" + opt.value + "]").attr("selected", "selected");
            }
        }
    }
});
