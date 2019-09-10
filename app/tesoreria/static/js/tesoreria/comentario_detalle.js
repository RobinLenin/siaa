$(function () {
    $('#formComentario').validate(
        {
            rules: {
                "concepto": {
                    remote: {
                        url: '/core/validar/campo-unico/',
                        type: 'POST',
                        data: {
                            'app': 'tesoreria',
                            'modelo': 'Comentario',
                            'atributo': 'concepto',
                            'valor': function () {
                                return $('#concepto').val();
                            },
                            'id': function () {
                                return $('#id').val();
                            }
                        }
                    }
                },
                "fecha_creacion": {
                    remote: {
                        url: '/core/validar/campo-unico/',
                        type: 'POST',
                        data: {
                            'app': 'tesoreria',
                            'modelo': 'Comentario',
                            'atributo': 'fecha_creacion',
                            'valor': function () {
                                return $('#fecha_creacion').val();
                            },
                            'id': function () {
                                return $('#id').val();
                            }
                        }
                    }
                },
                "detalle": {
                    remote: {
                        url: '/core/validar/campo-unico/',
                        type: 'POST',
                        data: {
                            'app': 'tesoreria',
                            'modelo': 'Comentario',
                            'atributo': 'detalle',
                            'valor': function () {
                                return $('#detalle').val();
                            },
                            'id': function () {
                                return $('#id').val();
                            }
                        }
                    }
                },
            },
            messages:{
                "concepto":{
                    remote: "Concepto duplicado"
                },
                "fecha_creacion":{
                    remote: "Fecha duplicado"
                }
                "detalle":{
                    remote: "Detalle duplicado"
                }
            }
        });
});