import { Injectable } from '@angular/core';
declare let alertify: any;

@Injectable()
export class NotificationService {
    private _notifier: any = alertify;

    constructor() { }

    /*
    Opens a confirmation dialog using the alertify.js lib
    */
    openConfirmationDialog(message: string, okCallback: () => any) {
        this._notifier.confirm(message, function (e) {
            if (e) {
                okCallback();
            } else {
            }
        });
    }

    /*
    Prints a success message using the alertify.js lib
    */
    printSuccessMessage(message: string) {
        this._notifier.success(message);
    }

    /*
    Prints an error message using the alertify.js lib
    */
    printErrorMessage(message: string) {
        this._notifier.error(message);
    }

    /**
    * Metodo que muestra una alerta con un mensaje de "ADVERTENCIA"
    */
    printWarningMessage(message: string){
        this._notifier.warning(message);
    }

    /**
    * Metodo que muestra una alerta con un mensaje de "INFORMACIÓN"
    */
    printInformationMessage(message: string){
        this._notifier.message(message);
    }
}
