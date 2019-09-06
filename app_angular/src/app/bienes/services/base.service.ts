/* Autor: Yazber Romero.
 * Fecha: 27/09/2016
 * ----------------------------Historial---------------------------
 * Autor                     	Fecha:                           	Descripcion  
 * Yazber Romero      	        27/09/2016                  	    Implementación inicial.
 */
import {Response} from "@angular/http";
import {Observable} from "rxjs/Observable";

export class BaseService  {

    /**
     * Permite extrar data de json
     * @param  {Response} res
     */
    extractData(res: Response) {
        let body = res.json();
        return body;
    }

    /** 
     * Permite centralizar excepciones: Manejador de excepciones
     * @param  {any} error
     */
    handleError(error: any) {
        var applicationError = error.headers.get('Application-Error');
        var serverError = error.json();
        var modelStateErrors: string = '';

        if (!serverError.type) {
            for (var key in serverError) {
                if (serverError[key])
                    modelStateErrors += serverError[key] + '\n';
            }
        }

        modelStateErrors = modelStateErrors = '' ? null : modelStateErrors;
        return Observable.throw(applicationError || modelStateErrors || 'Server error');
    }
}