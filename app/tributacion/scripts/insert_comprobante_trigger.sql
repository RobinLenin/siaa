--Crea la función
CREATE OR REPLACE FUNCTION public.insert_comprobante_func()
  RETURNS trigger AS
$BODY$
BEGIN
 INSERT INTO sri_servicios.comprobante_electronico(
	comprobante_id,numero_documento,estado, tipo, fecha_envia)
 VALUES(NEW.id, NEW.numero_documento,'P', 'F', now());
 RETURN NEW;
END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;

--Creo el triger
CREATE TRIGGER insert_comprobante_trigger  AFTER    INSERT
    ON public.tributacion_comprobante FOR EACH ROW
    EXECUTE PROCEDURE public.insert_comprobante_func();