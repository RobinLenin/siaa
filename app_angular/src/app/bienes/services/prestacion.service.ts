/* Autor: Yazber Romero.
 * Fecha: 07/10/2016
 * ----------------------------Historial---------------------------
 * Autor                     	Fecha:                           	Descripcion  
 * Yazber Romero      	        07/10/2016                   	    Implementación inicial.
 */
import {Injectable} from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {Observable} from 'rxjs/Observable';
import {appService} from './../../credentials';
import {BaseService} from './base.service';
import {IPrestacion, IPrestacionResponse} from './../dto/IPrestacion';
import {IDetallePrestacion} from '../dto/IDetallePrestacion';

@Injectable()
export class PrestacionService extends BaseService {
    private guardarPrestacionUrl = appService.ws_bienes_prestacion_guardar;
    private actualizarDetallePrestacionUrl = appService.ws_bienes_detalle_prestacion_guardar;


    constructor(private http: HttpClient) {
        super();
    }

    guardar(data: IPrestacion, token: string) {
        let body = JSON.stringify(data);
        let headers = new HttpHeaders({'Content-Type': 'application/json'});
        let options = {headers: headers};
        if (!data.id) {
            return this.http.post<IPrestacionResponse>(this.guardarPrestacionUrl + '/' + token, body, options)
        }
    }

    actualizarDetalle(detalle: IDetallePrestacion): Observable<any> {
        let body = JSON.stringify(detalle);
        let headers = {'Content-Type': 'application/json'};
        let options = {headers: headers};
        return this.http.put<IPrestacionResponse>(this.actualizarDetallePrestacionUrl + '/' + detalle.id, body, options)
    }


}
