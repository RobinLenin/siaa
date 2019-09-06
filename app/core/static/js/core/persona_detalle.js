$(function () {
    if (persona_validado_bsg == 'True') {
        $('#id_primer_apellido, #id_segundo_apellido, #id_primer_nombre, #id_segundo_nombre').attr('readonly', 'readonly');
    }
});

function etnia() {
    var opciones = document.getElementById("id_tipo_etnia");
    if (opciones.options[opciones.selectedIndex].text == "Indígena") {
        document.getElementById("id_nacionalidad_indigena").disabled = false;
    } else {
        document.getElementById("id_nacionalidad_indigena").disabled = true;
        document.getElementById("id_nacionalidad_indigena").selectedIndex = "0";
    }
}