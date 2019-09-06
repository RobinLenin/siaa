/* Autor: Yazber Romero.
 * Fecha: 24/08/2016
 * ----------------------------Historial---------------------------
 * Autor                     	Fecha:                           	Descripcion  
 * Yazber Romero      	        24/08/2016                  	    Implementación inicial.
 */
import {EventEmitter, Injectable, Output} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {appService} from './../../credentials';
import {IDetallePrestacion} from '../dto/IDetallePrestacion';
import {IPrestacionRepsResponse} from '../dto/IPrestacionRep';
import {BaseService} from './base.service';
import {UtilService} from './../../shared/comun/services/util.service';


@Injectable()
export class DetallePrestacionService extends BaseService {

    private serviciosUrlCriteria = appService.ws_bienes_detalle_prestacion_filtro;
    private detalles: IDetallePrestacion[] = [];
    private is_Editar: boolean = false;
    @Output() notificador = new EventEmitter();


    constructor(private http: HttpClient,
                private utilService: UtilService) {
        super();
    }

    obtenerPrestacionesCriterios(desde: any, hasta: any) {
        return this.http.get<IPrestacionRepsResponse>(this.serviciosUrlCriteria + "/" + desde + "/" + hasta)
    }

    setDetallesPrestaciones(i_detalles: IDetallePrestacion[]) {
        this.detalles = i_detalles;
        this.notificador.emit(i_detalles);
    }

    getDetallesPrestaciones(): IDetallePrestacion[] {
        return this.detalles;
    }

    setEditar(isEditar: boolean) {
        this.is_Editar = isEditar;
    }
}
