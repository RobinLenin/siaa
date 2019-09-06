export var credentials = {
    client_id: 1234,
    client_secret: 'secret',
    host: 'http://127.0.0.1:8000'
};

export var appService = {

    /*
     * URLS relacionadas al modulo SEGURIDAD
     * Autenticación
     * Funcionalidad Group
     */
    ws_seguridad_loguin: credentials.host + "/api/v1/seguridad/token/",
    ws_seguridad_usuario_logueado: credentials.host + "/api/v1/seguridad/usuario-logueado",
    ws_seguridad_usuario_logueado_funcionalidades: credentials.host + "/api/v1/seguridad/usuario-logueado-funcionalidades",

    /*
     * URLS relacionadas al modulo LABORATORIO Y BIENES
     * CRUD Prestaciones
     */
    ws_bienes_prestacion_guardar: credentials.host + '/api/v1/bienes/prestacion-guardar',
    ws_bienes_detalle_prestacion_guardar: credentials.host + '/api/v1/bienes/detalle-prestacion-guardar',
    ws_bienes_detalle_prestacion_lista: credentials.host + '/api/v1/bienes/detalle-prestacion-lista',
    ws_bienes_detalle_prestacion_filtro: credentials.host + '/api/v1/bienes/detalle-prestacion-filtro',

    /*
     * URLS relacionadas al modulo RECAUDACIÓN
     * CRUD Productos
     * CRUD de Puntos de Emisión.
     * CRUD Ordenes de Pago
     * Generación y emisón de facturas
     */
    ws_recaudacion_productos: credentials.host + "/api/v1/recaudacion/productos",
    ws_recaudacion_productos_paginacion: credentials.host + "/api/v1/recaudacion/productos/get_productos_por_paginacion",
    ws_recaudacion_puntos_emision: credentials.host + "/api/v1/recaudacion/puntos-emision",
    ws_recaudacion_ordenes_pago: credentials.host + "/api/v1/recaudacion/ordenes-pago",
    ws_recaudacion_ordenes_pago_paginacion: credentials.host + "/api/v1/recaudacion/ordenes-pago/get_ordenes_pago_por_paginacion",
    ws_recaudacion_factura_reporte_detalle: credentials.host + "/api/v1/recaudacion/comprobante-reporte-detalle",
    ws_recaudacion_factura_reporte_generadas: credentials.host + "/api/v1/recaudacion/comprobante-reporte-generadas",
    ws_recaudacion_factura_reporte_guardadas: credentials.host + "/api/v1/recaudacion/comprobante-reporte-guardadas",
    ws_recaudacion_orden_pago_reporte_detalle: credentials.host + "/api/v1/recaudacion/orden-pago-reporte-detalle",
    ws_recaudacion_orden_pago_reporte_consolidado: credentials.host + "/api/v1/recaudacion/orden-pago-reporte-consolidado",
    ws_recaudacion_orden_pago_reporte_productos: credentials.host + "/api/v1/recaudacion/orden-pago-reporte-productos",

    /**
     * URLS relacionadas al modulo CORE
     * CRUD Catalogos Items
     * CRUD Personas
     * CRUD Direcciones
     */
    ws_core_catalogo_item_por_codigo: credentials.host + "/api/v1/core/catalogo-item-por-codigo",
    ws_core_catalogo_item_lista_por_catalogo: credentials.host + "/api/v1/core/catalogo-item-lista-por-catalogo",
    ws_core_persona_o_registrocivil: credentials.host + "/api/v1/core/persona-o-registrocivil",
    ws_core_persona_lista_paginacion: credentials.host + "/api/v1/core/persona-lista-paginacion",
    ws_core_persona_lista_direcciones: credentials.host + "/api/v1/core/persona-lista-direcciones",


    /**
     * URLS relacionadas al modulo ORGÁNICO
     * URLS relacionadas al modulo CURRICULAR
     * URLS relacionadas al modulo TALENTO HUMANO
     * URLS relacionadas al modulo CONFIGURACIÓN
     * URLS relacionadas al modulo ṔAGOS
     *
     */
    ws_organico_uaa_lista_padres: credentials.host + '/api/v1/organico/uaa-lista-padres',
    ws_organico_uaa_lista_hijas: credentials.host + '/api/v1/organico/uaa-lista-hijas',
    ws_curricular_carrera_lista_vigentes: credentials.host + '/api/v1/curricular/carrera-lista-vigentes',
    ws_talento_humano_funcionario_lista: credentials.host + "/api/v1/talento-humano/funcionario-lista",
    ws_configuracion_detalle_parametrizacion_lista_por_padre: credentials.host + '/api/v1/configuracion/detalle-parametrizacion-lista-por-padre',
    ws_configuracion_detalle_parametrizacion_por_codigo: credentials.host + '/api/v1/configuracion/detalle-parametrizacion-por-codigo',
    ws_pagos_pago_lista_paginacion: credentials.host + "/api/v1/pagos/pago-lista-paginacion",
    ws_pagos_pago_detalle: credentials.host + "/api/v1/pagos/pago-detalle",
    ws_pagos_pago_validar: credentials.host + "/api/v1/pagos/pago-validar",

}
