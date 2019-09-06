import {HttpClient} from "@angular/common/http";

import {BaseService} from "./../../bienes/services/base.service";
import {Injectable} from "@angular/core";
import {ResourceService} from "../../shared/comun/services/resource.service";
import {appService} from "./../../credentials";
import {IUaasResponse} from "../models/uaa.model";

@Injectable()
export class UAAService extends BaseService {

    constructor(private http: HttpClient,
                private resourceService: ResourceService) {
        super();
    }

    /**
     * Permite devolver la lista de Unidades Academicas Administrativas de orden Superior (No son hijas)
     * @param {string} token
     * @returns
     */
    getUaasFathers(token: string) {
        let options = this.resourceService.getRequestOptions(token);
        return this.http.get<IUaasResponse>(appService.ws_organico_uaa_lista_padres, options)
    }

    /**
     * Permite devolver todas las Unidades Académicas Administrativas hijas relacionada a la uaa pasada como parametro
     * @param {string} token
     * @returns
     */
    getUaasChildren(token: string, id_uaa_padre: number) {
        let parametros = {id_uaa_padre: id_uaa_padre};
        let options = this.resourceService.getRequestOptions(token, parametros);
        return this.http.get<IUaasResponse>(appService.ws_organico_uaa_lista_hijas, options)
    }
}
