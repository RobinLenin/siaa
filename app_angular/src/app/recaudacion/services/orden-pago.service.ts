import {Injectable} from "@angular/core";
import {HttpClient} from "@angular/common/http";
import {Observable} from "rxjs/Observable";
import {appService} from "../../credentials";
import {ResourceService} from "../../shared/comun/services/resource.service";
import {OrdenPago, OrdenesPagoResponse, OrdenPagoResponse} from "../models/orden-pago.model";
import {IFactura} from "../models/factura-response.model";
import "rxjs/add/operator/map";

@Injectable()
export class OrdenPagoService {

    constructor(private http: HttpClient,
                private resourceService: ResourceService) {
    }

    /**
     * @desc Obtiene en formato json la lista de Ordenes de Pago del funcionario
     * en sesión y el punto de emisón UAA
     * @param {String} token - Cadena de caracteres para la autenticacion en el API
     * @param {Number} punto_emision_uaa_id - Identificador del Punto Emision UAA
     * @returns {Observable<TResult>}
     */
    getOrdenesPago(token: String, punto_emision_uaa_id) {
        let parametros = {
            punto_emision_uaa_id: punto_emision_uaa_id
        };
        let options = this.resourceService.getRequestOptions(token, parametros);
        return this.http.get<OrdenesPagoResponse>(appService.ws_recaudacion_ordenes_pago, options)
    }

    /**
     * @desc Consume el API para obtener una orden de pago
     * @param {String} token - Cadena de caracteres para la autenticacion en el API
     * @param {Number} id - Identificador de la Orden de Pago
     * @param {Number} punto_emision_uaa_id - Identificador del Punto Emision UAA
     * @returns {Observable<TResult>}
     */
    getOrdenPago(token: string, id: number, punto_emision_uaa_id=null) {
        let parametros = punto_emision_uaa_id ? {punto_emision_uaa_id: punto_emision_uaa_id} : {};
        let options = this.resourceService.getRequestOptions(token, parametros);
        return this.http.get<OrdenPagoResponse>(appService.ws_recaudacion_ordenes_pago + '/' + id, options)
    }

    /**
     * @desc Consume el API para guardar una Orden de Pago junto a las
     * Ordenes de Pago Detalle
     * @param {String} token - Cadena de caracteres para la autenticacion en el API
     * @param {OrdenPago} data - datos a guardar
     * @returns {Observable<TResult>}
     */
    guardarOrdenPago(token: string, data) {
        let body = JSON.stringify(data);
        let options = this.resourceService.getRequestOptions(token)
        return this.http.post<OrdenPagoResponse>(appService.ws_recaudacion_ordenes_pago, body, options)
    }

    /**
     * @desc Consume el API para anular una Orden de Pago
     * @param {String} token - Cadena de caracteres para la autenticacion en el API
     * @param {Nummber} id - Orden de Pago Detalle a guardar
     * @returns {Observable<TResult>}
     **/
    anularOrdenPago(token: string, id) {
        let options = this.resourceService.getRequestOptions(token)
        return this.http.put<OrdenPagoResponse>(appService.ws_recaudacion_ordenes_pago + "/" + id + "/anular", null, options)
    }

    /**
     * @desc Obtiene en formato json la lista de facturas a emitir de acuerdo a las
     * ordenes de pago registradas
     * @param {String} token - Cadena de caracteres para la autenticacion en el API
     * @returns {Observable<TResult>}
     */
    getFacturasEmitir(token: string, desde, hasta, punto_emision_id) {
        let parametros = {
            desde: desde,
            hasta: hasta,
            punto_emision_id: punto_emision_id,
        };
        let options = this.resourceService.getRequestOptions(token, parametros);
        return this.http.get<IFactura>(appService.ws_recaudacion_ordenes_pago + '/get_facturas_emitir_por_ordenes_pago', options);
    }

    /**
     * @desc Guarda las facturas que fueron generadas a partir de
     * las ordenes de pago emitidas en un rango de fechas.
     * @param {String} token - Cadena de caracteres para la autenticacion en el API
     * @param {Array} data - Lista de facturas a guardar
     * @returns {Observable<TResult>}
     */
    guardarFacturasEmitir(token: string, data) {
        let options = this.resourceService.getRequestOptions(token)
        return this.http.post<IFactura>(appService.ws_recaudacion_ordenes_pago + '/0/guardar_facturas_por_ordenes_pago', data, options)
    }

    /**
     * @desc Obtiene en formato json la lista de facturas emitidas de acuerdo a las
     * a un rango de fechas
     * @param {String} token - Cadena de caracteres para la autenticacion en el API
     * @returns {Observable<TResult>}
     */
    getFacturasEmitidas(token: string, desde, hasta) {
        let parametros = {
            desde: desde,
            hasta: hasta
        };
        let options = this.resourceService.getRequestOptions(token, parametros);
        return this.http.get<IFactura>(appService.ws_recaudacion_ordenes_pago + '/get_facturas_emitidas_por_ordenes_pago', options);
    }

    /**
     * @desc Anula las facturas emitidas enviadas como parámetro
     * @param {String} token - Cadena de caracteres para la autenticacion en el API
     * @param {Array} data - Lista de facturas anular
     * @returns {Observable<TResult>}
     */
    anularFacturas(token: string, data) {
        let options = this.resourceService.getRequestOptions(token)
        return this.http.post<IFactura>(appService.ws_recaudacion_ordenes_pago + '/0/anular_facturas_emitidas_por_ordenes_pago', data, options)
    }

    /**
     * @desc Validar la Orden de Pago de PENDIENTE a EMITIDA creando un registro de PAGO
     * @param {String} token - Cadena de caracteres para la autenticacion en el API
     * @param {OrdenPago} data - datos a guardar del pago
     * @returns {Observable<TResult>}
     */
    validarOrdenPago(token: string, id: number, data) {
        let body = JSON.stringify(data);
        let options = this.resourceService.getRequestOptions(token);
        return this.http.put<OrdenPagoResponse>(appService.ws_recaudacion_ordenes_pago+"/" + id + "/validar", body, options)
    }
}
