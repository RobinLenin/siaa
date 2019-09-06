import { Component, Input } from '@angular/core';
import { FormControl } from '@angular/forms';
import { ValidacionService } from '../../services/validacion.service';

@Component({
  selector: 'control-errores',
  template: `<div [ngClass]="'mensajeError'" *ngIf="mensajeError !== null">{{mensajeError}}</div>`
})
export class ValidadorComponent {
  @Input() control: FormControl;
  constructor() { }

  get mensajeError() {
    for (let propertyName in this.control.errors) {
      if (this.control.errors.hasOwnProperty(propertyName) && this.control.touched) {
        return ValidacionService.getValidadorMensajeError(propertyName, this.control.errors[propertyName]);
      }
    }

    return null;
  }
}
