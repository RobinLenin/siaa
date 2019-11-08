from enum import Enum

class MensajesEnum(Enum):
    ACCION_GUARDAR = "Datos actualizados correctamente..."
    ACCION_ELIMINAR= "Datos eliminados correctamente..."
    ACCION_ELIMINAR_ERROR = "No se puede eliminar el registro..."
    DATOS_INCOMPLETOS = "Por favor ingrese todos los datos..."
    METODO_NO_VALIDO = "Método no válido..."
