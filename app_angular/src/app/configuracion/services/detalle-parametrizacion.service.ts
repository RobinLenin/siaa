import {Injectable} from "@angular/core";
import "rxjs/add/operator/map";
import "rxjs/add/operator/catch";
import {HttpClient} from "@angular/common/http";
import {appService} from "../../credentials";
import {ResourceService} from "../../shared/comun/services/resource.service";
import {DetalleParametrizacionResponse} from "../models/detalle-parametrizacion.model"

@Injectable()
export class DetalleParametrizacionService {

    constructor(private http: HttpClient,
                private resourceService: ResourceService) {
    }

    /**
     * @desc Obtiene lista detalle parametrizacion de acuerdo a la Parametrización Padre
     * @param {String} token - Cadena de caracteres para la autenticacion en el API
     * param {String} codigoParametrizacion - Código de la Parametrización
     * @returns {Object|Array} Lista de detalle parametrizacion
     */
    getDetallesParametrizacionPorParametrizacion(token: string, codigoParametrizacion: string) {
        let parametros = {codigo: codigoParametrizacion};
        let requestOptions = this.resourceService.getRequestOptions(token, parametros);
        return this.http.get<DetalleParametrizacionResponse>(appService.ws_configuracion_detalle_parametrizacion_lista_por_padre, requestOptions)
    }

    /**
     * @desc Obtiene un detalle parametrización de acuerdo a su código
     * @param {String} token - Cadena de caracteres para la autenticacion en el API
     * @param {String} codigoDetalleParametrizacion - Código
     * @returns {Object|Array} Objeto Detalle Parametrización
     */
    getDetalleParametrizacionPorCodigo(token: string, codigoDetalleParametrizacion: string) {
        let parametros = {codigo: codigoDetalleParametrizacion};
        let requestOptions = this.resourceService.getRequestOptions(token, parametros);
        return this.http.get<DetalleParametrizacionResponse>(appService.ws_configuracion_detalle_parametrizacion_por_codigo, requestOptions)
    }

}
