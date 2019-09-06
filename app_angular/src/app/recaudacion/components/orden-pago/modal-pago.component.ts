import {Component, Inject, ViewContainerRef} from '@angular/core';
import {FormBuilder, Validators} from "@angular/forms";
import {MAT_DIALOG_DATA, MatDialogRef} from "@angular/material";

import {Pago} from "../../models/pago.model";
import {OrdenPago} from "../../models/orden-pago.model";
import {OrdenPagoService} from "../../services/orden-pago.service";
import {DialogService} from "../../../shared/comun/services/dialog.service";

@Component({
    selector: 'recaudacion-pago',
    templateUrl: './modal-pago.component.html',
})
export class ModalPagoComponent {

    ordenPago: OrdenPago;
    opcion: string = 'NUEVO'; // NUEVO, crear una orden de pago. VALIDAR, actualiza la orden de pago de PENDIENTE a EMITIDA con su pago
    pagoForm;
    choiceFormaPago = [
        {value: 'DEPOSITO', nombre: 'Depósito'},
        {value: 'EFECTIVO', nombre: 'Efectivo'},
        {value: 'TRANSFERENCIA', nombre: 'Tranferencia'},
        {value: 'TARJETA_CREDITO', nombre: 'Tarjeta de crédito'}];


    constructor(
        public dialogRef: MatDialogRef<ModalPagoComponent>,
        private dialogService: DialogService,
        private formBuilder: FormBuilder,
        private ordenPagoService: OrdenPagoService,
        private viewContainerRef: ViewContainerRef,
        @Inject(MAT_DIALOG_DATA) public data) {

        this.opcion = data.opcion;
        this.ordenPago = Object.assign({}, data.ordenPago);
        this.ordenPago.pago = new Pago();
        this.ordenPago.pago.forma_pago = 'EFECTIVO';
        this.ordenPago.pago.total = this.ordenPago.total;

        this.pagoForm = this.formBuilder.group({
            'forma_pago': [this.ordenPago.pago.forma_pago, [Validators.required]],
            'referencia': [this.ordenPago.pago.referencia],
            'depositante': [this.ordenPago.pago.depositante],
        });
        const referencia = this.pagoForm.get('referencia');
        this.pagoForm.get('forma_pago').valueChanges
            .subscribe(value => {
                if (value == 'EFECTIVO') {
                    referencia.clearValidators();
                } else {
                    referencia.setValidators([Validators.required]);
                }
                referencia.updateValueAndValidity();
            });
    }

    cerrar(): void {

        this.dialogRef.close();
    }

    /**
     * @desc Guarda una orden de pago nueva (invocado desde orden-pago-detail), o valida la orden de pago de
     * PENDIENTE a EMITIDA con su forma de pago (invocado desde orden-pago-validar-detail)
     */
    guardar() {
        if (this.opcion == 'NUEVO') {
            this.ordenPagoService.guardarOrdenPago(window.localStorage.getItem('auth_key'), this.ordenPago)
                .subscribe(resp => {
                    if (resp.status == 200) {
                        this.dialogRef.close(resp.data.id);
                    } else {
                        this.dialogService.notificacion('ERROR!', resp.message, this.viewContainerRef)
                    }
                });
        } else {
            this.ordenPagoService.validarOrdenPago(window.localStorage.getItem('auth_key'), this.ordenPago.id, this.ordenPago.pago)
                .subscribe(resp => {
                    if (resp.status == 200) {
                        this.dialogRef.close(resp.data);
                    } else {
                        this.dialogService.notificacion('ERROR!', resp.message, this.viewContainerRef)
                    }
                });
        }
    }
}
