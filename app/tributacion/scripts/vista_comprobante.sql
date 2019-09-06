-- View: sri_servicios.vista_comprobante

-- DROP VIEW sri_servicios.vista_comprobante;

CREATE OR REPLACE VIEW sri_servicios.vista_comprobante
AS
SELECT
  tributacion_comprobante.id as comprobante_id,
  --'UNIVERSIDAD NACIONAL DE LOJA'::text AS unl_razon_social,
  --'UNIVERSIDAD NACIONAL DE LOJA'::text AS unl_nombre_comercial,
  --'1160001720001'::text AS unl_ruc,
  --'AV. PIO JARAMILLO ALVARADO S/N'::text AS unl_direccion_matriz,
  'AV. PIO JARAMILLO ALVARADO S/N'::text AS direccion_establecimiento,
  --'+593 (7) 2547252'::text AS unl_telefono,
  tributacion_comprobante.numero_documento as numero_documento,
  to_char(tributacion_comprobante.fecha_emision,'YYYY-MM-DD') as fecha_emision,
  core_persona.primer_nombre || CASE WHEN core_persona.segundo_nombre='' THEN '' ELSE ' ' END ||core_persona.segundo_nombre||' '||
  core_persona.primer_apellido||CASE WHEN core_persona.segundo_apellido='' THEN '' ELSE ' ' END ||core_persona.segundo_apellido as cliente_razon_social,
  (select ci.nombre from core_catalogoitem ci where ci.id=core_persona.tipo_documento_id) as cliente_tipo_identificacion,
  core_persona.numero_documento as cliente_identificacion,
  (CASE WHEN core_persona.correo_electronico IS NOT NULL THEN core_persona.correo_electronico  ELSE core_persona.correo_electronico_alternativo END) as cliente_correo,
  core_direccion.calle_principal||' '||COALESCE(core_direccion.calle_secundaria,'')||' '||COALESCE(core_direccion.referencia,'') as cliente_direccion,
  core_direccion.celular as cliente_telefono,
  tributacion_comprobante.observacion as observacion,
  tributacion_comprobante.subtotal_descuento as total_descuento,
  tributacion_comprobante.subtotal_sin_impuesto as total_sin_impuesto,
  --(Select sum(timp.subtotal) from public.tributacion_comprobanteimpuesto timp where timp.comprobante_id = tributacion_comprobante.id and timp.codigo_impuesto='IVA_12') as base_12,
  --(Select sum(timp.subtotal) from public.tributacion_comprobanteimpuesto timp where timp.comprobante_id = tributacion_comprobante.id and timp.codigo_impuesto='IVA_0') as base_0,
  --(Select sum(timp.subtotal) from public.tributacion_comprobanteimpuesto timp where timp.comprobante_id = tributacion_comprobante.id and timp.codigo_impuesto='NO_OBJETO_IVA') as base_noobjetoiva,
  --(Select sum(timp.impuesto) from public.tributacion_comprobanteimpuesto timp where timp.comprobante_id = tributacion_comprobante.id and timp.codigo_impuesto='IVA_12') as iva_12,
  tributacion_comprobante.total as total
FROM
  public.tributacion_comprobante,
  public.core_persona,
  public.core_direccion,
  public.core_catalogoitem
WHERE
  tributacion_comprobante.persona_id = core_persona.id AND
  tributacion_comprobante.direccion_id = core_direccion.id AND
  tributacion_comprobante.tipo_documento_id = core_catalogoitem.id AND
  core_catalogoitem.codigo_th = 'FACTURA' -- Tipo específico de ordenes de pago

ORDER BY tributacion_comprobante.fecha_emision asc, tributacion_comprobante.numero_documento asc;

GRANT SELECT ON sri_servicios.vista_comprobante to siaaf_sri_servicios;
