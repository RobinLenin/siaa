import {Component, OnInit} from '@angular/core';
import {ActivatedRoute, Params, Router} from '@angular/router';

import {OrdenPagoService} from "../../services/orden-pago.service";
import {MatDialog, MatSnackBar} from "@angular/material";
import {OrdenPago} from "../../models/orden-pago.model";
import {ModalPagoComponent} from "./modal-pago.component";


@Component({
    moduleId: module.id,
    selector: 'recaudacion-orden-pago-validar-detail',
    templateUrl: './orden-pago-validar-detail.component.html'
})

export class OrdenPagoValidarDetailComponent implements OnInit {

    ordenPago: OrdenPago;

    constructor(public dialog: MatDialog,
                private ordenPagoService: OrdenPagoService,
                private route: ActivatedRoute,
                private router: Router,
                private snackBar: MatSnackBar) {
    }

    /**
     * @desc Función inicializadora del componente
     */
    ngOnInit() {
        this.route.params.forEach((params: Params) => {
            let id = +params['id'];
            this.ordenPagoService.getOrdenPago(window.localStorage.getItem('auth_key'), id)
                .subscribe(resp => {
                    if (resp.status == 200) {
                        this.ordenPago = <OrdenPago>resp.data
                    } else {
                        this.snackBar.open(resp.message, 'Aceptar', {duration: 5000});
                    }
                });
        });
    }

    /**
     * @desc Muestra el modal para validar e pago
     */
    validar() {
        if (this.ordenPago.pago) {
            this.snackBar.open("La orden de pago ya tiene un registro de Pago", 'Aceptar', {duration: 5000});
        } else {
            const dialogRef = this.dialog.open(ModalPagoComponent, {
                width: '500px',
                data: {'ordenPago': this.ordenPago, 'opcion': 'VALIDAR'}
            });
            dialogRef.afterClosed().subscribe(result => {
                if (result) {
                    this.ordenPago = result;
                }
            });
        }
    };

    /**
     * @desc Función que navega al componente que lista los pagos
     */
    regresar() {
        this.router.navigate(['home/recaudacion-orden-pago-validar-list'])
    }
}

