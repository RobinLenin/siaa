MÓDULO DE RECAUDACIÓN
==========================================================

Proyecto desarrollado por la **Subdirección de Desarrollo de Software** que pertenece
a la **Unidad de Telecomunicaciones e Información** de la [Universidad Nacional de Loja](http://www.unl.edu.ec)

Descripción
-----------
El módulo permitira manejar las ventas que se emiten a los clientes, el mismo que tiene siguientes funcionalidaes:

* Administrar Productos (crear, editar, eliminar productos asi como agregar Unidades Academicas Administrativas (UAA) al producto)
* Administrar Puntos de Emisión (crear, editar, eliminar Puntos de emisión asi como asignar Funcionarios por cada Punto de emisión UAA)
* Generación de Ordenes de Pago (emitir, anular ordenes de pago)
* Generación de facturas (generar facturas de acuerdo a las ordenes de pago emitidas)
* Reportes para tesoreria y recaudadora

Requisitos
----------
1. Crear las siguientes **Funcionalidades**:

    **Recaudación**
        padre: None
        
    **Productos**
        padre: Recaudación,
        formulario: recaudacion-producto-list,
        codigo: FUNC_RECAUDACION_PRODUCTO
        
    **Puntos de Emisión**
        padre: Recaudación,
        formulario: recaudacion-punto-emision-list
        codigo: FUNC_RECAUDACION_PUNTOS_EMISION
        
    **Ordenes de Pago**
        padre: Recaudación,
        formulario: recaudacion-orden-pago-list
        codigo: FUNC_RECAUDACION_ORDEN_PAGO
        
    **Emisión de Facturas**
        padre: Recaudación
        formulario: recaudacion-factura-emision-list
        codigo: FUNC_RECAUDACION_GENERAR_FACTURAS
        
    **Reportes Recaudadora**
        padre: Recaudación
        formulario: recaudacion-reportes-uaa
        codigo: FUNC_RECAUDACION_REPORTES_UAA
        
    **Reportes Tesoreria**
        padre: Recaudación
        formulario: recaudacion-reportes-admin
        codigo: FUNC_RECAUDACION_REPORTES_ADMIN

2. Crear dos grupos **recaudacion_administrador** y **recaudacion_usuarios** y agrega las funcionalidades groups

    **recaudacion_administrador**: tiene acceso a todas las funcionalidades, representa a tesorería
    
    **recaudacion_usuarios**: tiene acceso a ordenes de pago y reportes recaudadora, representa a recaudadores


3. Agregar el **usuario** al **grupo** que compete.

4. Crear persona de **Consumidor Final** (9999999999999) con su **dirección**

5. Cargar **Catalogo y sus detalles** 

        TIPO_DOCUMENTO,TIPO_FACTURA,,1
            TIPO_FACTURA,CONSUMIDOR FINAL,Factura sin datos,CF
            TIPO_FACTURA,INDIVIDUAL,Factura con datos,IND
            TIPO_FACTURA,INDIVIDUAL-ARRIENDOS,Factura con datos,IND_ARRIENDOS
        
        TIPO_UNIDAD,TIPO_UNIDAD,,1
            TIPO_UNIDAD,Caja,,TPU_CAJA
            TIPO_UNIDAD,Galones,,TPU_GALONES
            TIPO_UNIDAD,Litros,,TPU_LITRO
            TIPO_UNIDAD,Metros,,TPU_METRO
            TIPO_UNIDAD,Unitario,,TPU_UNITARIO
            
        ESTADO_ORDEN_PAGO,ESTADO_ORDEN_PAGO,,1
            ESTADO_ORDEN_PAGO,ANULADA,La orden de pago esta anulada,EST_ORDEN_PAGO_ANULADA
            ESTADO_ORDEN_PAGO,EMITIDA,La orden de pago esta emitida,EST_ORDEN_PAGO_EMITIDA
        
        TIPO_DOCUMENTO_CONTABLE,,1
            TIPO_DOCUMENTO_CONTABLE, FACTURA, Factura generada y es enviada electronicamente al SRI, FACTURA


6. Cargar **Parametrizaciones y sus detalles**
        
        PARAMETRIZACION
            CODIGO: TIPO_IMPUESTO, NOMBRE: IMPUESTOS, DESCRIPCIÓN: Tipo de impuestos para emisión de facturas
        DETALLE PARAMETRIZACIÓN
            CODIGO: IVA_10, NOMBRE: IVA 10%, VALOR: 0.10
        	CODIGO: EXCEPTO_IVA, NOMBRE: EXCEPTO DE IVA, VALOR:0
        
        PARAMETRIZACION
            CODIGO: RECAUDACION, NOMBRE: RECAUDACION, DESCRIPCIÓN: Datos de Recaudación
        DETALLE PARAMETRIZACIÓN
            CODIGO: URL_IMPRESION_DERECHO_WCP, 
            NOMBRE: Impresión Derecho WCP (ids & token), 
            VALOR: http://url_servicio_wcp
        	