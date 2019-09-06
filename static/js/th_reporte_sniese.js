$('#tipo_reporte').change(function() {
    var str = "";
    $( "#tipo_reporte option:selected" ).each(function() {
      str = $( this ).val();
    });
        if(str === 'docentes contratados'){
            $('.tipo_relacion').fadeIn();
        }else{
            $('.tipo_relacion').fadeOut();
        }
    });
