import {FormGroup} from "@angular/forms";

export class ValidacionService {

    static getValidadorMensajeError(validatorName: string, validatorValue?: any) {
        let config = {
            'required': 'Este campo es requerido!',
            'pattern': 'Formato incorrecto!',
            'emailInvalido': 'El email ingresado es incorrecto!',
            'campoNumerico': 'Campo númerico!',
            'campoAutocompletar': 'Seleccione un item!',
            'cantidadDesdeMenorHasta': 'El DESDE debe ser mayor al HASTA'
        };

        return config[validatorName];
    }

    static validadorEmail(control) {
        let valor= String(control.value);
        if (control.value==null || valor.length==0 || valor.match(/^[^@]+@[^@]+\.[a-zA-Z]{2,6}$/)) {
            return null;
        } else {
            return { 'emailInvalido': true };
        }
    }

    static validadorEsNumeroODecimal(control) {
        let valor= String(control.value);
        if (control.value==null || valor.length==0 || valor.match(/^[0-9]+(\.[0-9]+)?$/)) {
            return null;
        } else {
            return { 'campoNumerico': true };
        }
    }

    static validadorEsNumero(control) {
        let valor= String(control.value);
        if (control.value==null || valor.length==0 || valor.match(/^[0-9]+$/)) {
            return null;
        } else {
            return { 'campoNumerico': true };
        }
    }

    static validadorAutocompletar(control) {
        if (!control.value || typeof control.value === 'object') {
            return null;
        } else {
            return { 'campoAutocompletar': true };
        }
    }

    static validadorCantidadDesdeMenorHasta(control: FormGroup) {
        let nro_desde = control.get('nro_desde').value;
        let nro_hasta = control.get('nro_hasta').value;
        if (nro_desde==null || nro_hasta==null ||(parseInt(nro_desde)< parseInt(nro_hasta))) {
            return null;
        }else{
          return  {'cantidadDesdeMenorHasta': true };
        };
    }
}

