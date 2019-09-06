$(function () {
    $('#formAsignatura').validate(
        {
            rules: {
                "codigo_institucional": {
                    remote: {
                        url: '/core/validar/campo-unico/',
                        type: 'POST',
                        data: {
                            'app': 'academico',
                            'modelo': 'Asignatura',
                            'atributo': 'codigo_institucional',
                            'valor': function () {
                                return $('#codigo_institucional').val();
                            },
                            'id': function () {
                                return $('#id').val();
                            }
                        }
                    }
                },
                "codigo_unesco": {
                    remote: {
                        url: '/core/validar/campo-unico/',
                        type: 'POST',
                        data: {
                            'app': 'academico',
                            'modelo': 'Asignatura',
                            'atributo': 'codigo_unesco',
                            'valor': function () {
                                return $('#codigo_unesco').val();
                            },
                            'id': function () {
                                return $('#id').val();
                            }
                        }
                    }
                },
            },
            messages:{
                "codigo_institucional":{
                    remote: "Código institucional duplicado"
                },
                "codigo_unesco":{
                    remote: "Código Unesco duplicado"
                }
            }
        });
});