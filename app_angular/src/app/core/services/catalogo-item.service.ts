import "rxjs/add/operator/map";
import "rxjs/add/operator/catch";
import {HttpClient} from "@angular/common/http";
import {Injectable} from "@angular/core";
import {ResourceService} from "../../shared/comun/services/resource.service";
import {appService} from "../../credentials";
import {CatalogoItemResponse, CatalogoItemsResponse} from "../models/catalogo-item.model";

@Injectable()
export class CatalogoItemService {


    constructor(private http: HttpClient,
                private resourceService: ResourceService) {
    }

    getItemsPorCatalogo(codigoCatalogo: string, token: string) {
        let parametros = {codigoCatalogo: codigoCatalogo};
        let options = this.resourceService.getRequestOptions(token, parametros);
        return this.http.get<CatalogoItemsResponse>(appService.ws_core_catalogo_item_lista_por_catalogo, options)
    }

    getCatalogoItemPorCodigo(codigo: string, token: string) {
        let parametros = {codigo: codigo};
        let options = this.resourceService.getRequestOptions(token, parametros);
        return this.http.get<CatalogoItemResponse>(appService.ws_core_catalogo_item_por_codigo, options)
    }
}
