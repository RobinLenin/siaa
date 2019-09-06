CREATE OR REPLACE VIEW sri_servicios.vista_tarifa AS
 SELECT t.comprobante_id,
    t.subtotal,
    t.impuesto as valor,
    t.codigo_impuesto as codigo_tarifa,
    (CASE
	WHEN t.codigo_impuesto = 'IVA_0' THEN 0
	WHEN t.codigo_impuesto = 'IVA_12' THEN 2
	WHEN t.codigo_impuesto = 'IVA_14' THEN 3
	WHEN t.codigo_impuesto = 'NO_OBJETO_IMPUESTO' THEN 6
	WHEN t.codigo_impuesto = 'EXENTO_IVA' THEN 7
	ELSE -1
    END) AS codigo_sri

   FROM tributacion_comprobanteimpuesto AS t
   LEFT JOIN tributacion_comprobante AS c ON t.comprobante_id = c.id
   ORDER BY t.id, t.codigo_impuesto;

   GRANT SELECT ON sri_servicios.vista_comprobante_detalle to siaaf_sri_servicios;