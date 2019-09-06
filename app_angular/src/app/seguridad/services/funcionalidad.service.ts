import {EventEmitter, Injectable, Output} from "@angular/core";
import {HttpClient} from "@angular/common/http";
import {ResourceService} from "../../shared/comun/services/resource.service";
import {appService} from "../../credentials";
import "rxjs/add/operator/map";
import "rxjs/add/operator/catch";

import {FuncionalidadGroup} from "../models/funcionalidad-group.model"

@Injectable()
export class FuncionalidadService {

    private codigoFuncionalidad: string;
    @Output() notificador = new EventEmitter();

    constructor(private http: HttpClient,
                private resourceService: ResourceService) {
    }

    /**
     * @desc Obtiene en formato json la lista de funcionalidades
     * a la que tiene acceso el usuario logueado
     * @param {String} token
     * @returns {Observable<TResult>}
     */
    getFuncionalidadesAccesoUsuario(token) {
        let options = this.resourceService.getRequestOptions(token);
        return this.http.get<FuncionalidadGroup[]>(appService.ws_seguridad_usuario_logueado_funcionalidades, options)
    }

    setCodigoFuncionalidad(i_codigo: string) {
        this.codigoFuncionalidad = i_codigo;
        this.notificador.emit(i_codigo)
    }

    getCodigoFuncionalidad(): string {
        return this.codigoFuncionalidad;
    }
}
