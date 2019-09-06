CREATE TABLE sri_servicios.comprobante_electronico
(
  id serial NOT NULL,
  comprobante_id integer NOT NULL,
  numero_documento character varying(17) NOT NULL,
  clave_acceso character varying(49),
  numero_autorizacion character varying(49),
  fecha_autorizacion timestamp without time zone,
  estado varchar(1),
  tipo varchar(1),
  error_autorizacion text,
  fecha_envia timestamp without time zone,
  CONSTRAINT pk_comprobante_electronico PRIMARY KEY (id),
  CONSTRAINT fk_tributacion_comprobante_id FOREIGN KEY (comprobante_id) REFERENCES public.tributacion_comprobante (id) MATCH SIMPLE ON UPDATE NO ACTION ON DELETE NO ACTION
);

ALTER TABLE sri_servicios.comprobante_electronico OWNER TO siaaf;
GRANT ALL ON TABLE sri_servicios.comprobante_electronico TO siaaf;
GRANT SELECT, UPDATE ON TABLE sri_servicios.comprobante_electronico TO siaaf_sri_servicios;