-- View: sri_servicios.vista_comprobante_detalle

-- DROP VIEW sri_servicios.vista_comprobante_detalle;

CREATE OR REPLACE VIEW sri_servicios.vista_comprobante_detalle AS
 SELECT tributacion_comprobantedetalle.comprobante_id,
    tributacion_comprobantedetalle.id AS comprobantedetalle_id,
    tributacion_comprobante.numero_documento,
    tributacion_comprobantedetalle.codigo AS codigo_producto,
    tributacion_comprobantedetalle.detalle AS detalle_producto,
    tributacion_comprobantedetalle.detalle_adicional AS detalle_adicional_producto,
    tributacion_comprobantedetalle.cantidad AS cantidad_producto,
    tributacion_comprobantedetalle.precio AS precio_unitario_producto,
    tributacion_comprobantedetalle.descuento AS descuento_producto,
    tributacion_comprobantedetalle.subtotal AS precio_total_sin_impuestos,
    tributacion_comprobantedetalle.subtotal AS base_imponible,
    tributacion_comprobantedetalle.codigo_impuesto AS tarifa_codigo,
    (CASE
	WHEN tributacion_comprobantedetalle.codigo_impuesto = 'IVA_0' THEN 0
	WHEN tributacion_comprobantedetalle.codigo_impuesto = 'IVA_12' THEN 2
	WHEN tributacion_comprobantedetalle.codigo_impuesto = 'IVA_14' THEN 3
	WHEN tributacion_comprobantedetalle.codigo_impuesto = 'NO_OBJETO_IMPUESTO' THEN 6
	WHEN tributacion_comprobantedetalle.codigo_impuesto = 'EXENTO_IVA' THEN 7
	ELSE -1
    END) AS tarifa_sri,
    configuracion_detalleparametrizacion.valor::numeric * 100::numeric AS impuesto_tarifa,
    tributacion_comprobantedetalle.impuesto AS impuesto_valor,
    tributacion_comprobantedetalle.total AS valor_total
   FROM tributacion_comprobantedetalle,
    tributacion_comprobante,
    configuracion_detalleparametrizacion,
    core_catalogoitem
  WHERE tributacion_comprobantedetalle.tipo_impuesto_id = configuracion_detalleparametrizacion.id AND tributacion_comprobantedetalle.comprobante_id = tributacion_comprobante.id AND tributacion_comprobante.tipo_documento_id = core_catalogoitem.id AND core_catalogoitem.codigo_th::text = 'FACTURA'::text
  ORDER BY tributacion_comprobante.fecha_emision, tributacion_comprobante.numero_documento;


GRANT SELECT ON sri_servicios.vista_comprobante_detalle to siaaf_sri_servicios;