import {HttpClient} from "@angular/common/http";
import {Injectable} from "@angular/core";
import {Observable} from "rxjs/Observable";
import "rxjs/add/operator/map";
import "rxjs/add/operator/catch";
import {appService} from "../../credentials";
import {ResourceService} from "../../shared/comun/services/resource.service";
import {Producto, IProductoResponse, IProductosResponse} from "../models/producto.model";

@Injectable()
export class ProductoService {

    constructor(private http: HttpClient,
                private resourceService: ResourceService) {
    }

    /**
     * @desc Consume el API, para obtener la lista de productos
     * @param {String} token -Cadena de caracteres para la autenticacion en el API
     * @returns {Observable<TResult>}
     */
    getProductos(token: string) {
        let options = this.resourceService.getRequestOptions(token)
        return this.http.get<IProductosResponse>(appService.ws_recaudacion_productos, options)
    }

    /**
     * @desc Consume el API para obtener un producto
     * @param {String} token - Cadena de caracteres para la autenticacion en el API
     * @param {Number} id - Identificador del item
     * @returns {Observable<TResult>}
     */
    getProducto(token: string, id: number) {
        let options = this.resourceService.getRequestOptions(token);
        return this.http.get<IProductoResponse>(appService.ws_recaudacion_productos + '/' + id, options)
    }

    /**
     * @desc Consume el API para elimina un producto
     * @param {String} token - Cadena de caracteres para la autenticacion en el API
     * @param {Number} id - Identificador del item
     * @returns {Observable<TResult>}
     */
    deleteProducto(token: string, id: number) {
        let options = this.resourceService.getRequestOptions(token)
        return this.http.delete<IProductoResponse>(appService.ws_recaudacion_productos + '/' + id, options)
    }

    /**
     * @desc Consume el API para guardar o actualizar un producto
     * @param {String} token - Cadena de caracteres para la autenticacion en el API
     * @param {Producto} data - Datos a guardar
     * @returns {Observable<TResult>}
     */
    guardarProducto(token: string, data: Producto) {
        let body = JSON.stringify(data);
        let options = this.resourceService.getRequestOptions(token)
        if (!data.id) {
            return this.http.post<IProductoResponse>(appService.ws_recaudacion_productos, body, options)
        } else {
            return this.http.put<IProductoResponse>(appService.ws_recaudacion_productos + '/' + data.id, body, options)
        }
    }

    /**
     * @desc Consume el API para asignar una Unidad
     * Academica Administratica (UAA)  a un producto
     * @param {String} token - Cadena de caracteres para la autenticacion en el API
     * @param {Object} data - UAA a asignar al Producto
     * @returns {Observable<TResult>}
     */
    asignarUaasInProducto(token: string, data) {
        let body = JSON.stringify(data)
        let options = this.resourceService.getRequestOptions(token)
        return this.http.post<IProductoResponse>(appService.ws_recaudacion_productos + '/0/asignar_uaas_in_producto', body, options)
    }

    /**
     * @desc Consume el API para eliminar una Unidad
     * Academica Administratica (UAA)  a un producto
     * @param {String} token - Cadena de caracteres para la autenticacion en el API
     * @param {Object} data - UAA a eliminar del Producto
     * @returns {Observable<TResult>}
     */
    deleteUaaInProducto(token: string, data) {
        let body = JSON.stringify(data);
        let options = this.resourceService.getRequestOptions(token)
        return this.http.post<IProductoResponse>(appService.ws_recaudacion_productos + "/0/delete_uaa_in_producto", body, options)
    }

    /**
     * @desc Consume el API, para obtener la lista de
     * productos que pertenecen a las Unidades Academicas Administrativas
     * del funcionario en sesión
     * @param {String} token -Cadena de caracteres para la autenticacion en el API
     * @returns {Observable<TResult>}
     */
    getProductosInFuncionarioInUaa(token: string) {
        let options = this.resourceService.getRequestOptions(token)
        return this.http.get<IProductosResponse>(appService.ws_recaudacion_productos + '/get_productos_in_funcionario_in_uaa', options)
    }

}
