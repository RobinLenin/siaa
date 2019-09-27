from enum import Enum

class MensajesEnum(Enum):
    ACCION_NUEVO_TASA = "Tasa ya creada"
    ACCION_GUARDAR = "Datos actualizados correctamente..."
    ACCION_ELIMINAR= "Datos eliminados correctamente..."
    ACCION_ELIMINAR_ERROR = "No se puede eliminar el registro..."
    DATOS_INCOMPLETOS = "Por favor ingrese todos los datos..."
    METODO_NO_VALIDO = "Método no válido..."
    ABONO_MAYOR_SALDO = "Tienes un abonoo que supera tu saldo por cobrar"
    ABONO_ERROR = "No puede ingresar este abono, fecha incorrecta"