import {Injectable, EventEmitter} from "@angular/core";
import {HttpClient, HttpResponse} from "@angular/common/http";
import {ComunEnum} from "./../utils/enums";
import "rxjs/add/operator/map";
import "rxjs/add/operator/catch";


@Injectable()
export class ResourceService {

    public data: Array<any> = [];
    public numberTotalPages = 0;
    public numberTotalItems = 0;
    public keys: Array<any> = [];
    public key: string;
    private static _pipedDataEmitter;

    constructor(private http: HttpClient) {
    }

    static getPipedData(): EventEmitter<any> {
        if (!this._pipedDataEmitter) {
            this._pipedDataEmitter = new EventEmitter();
        }
        return this._pipedDataEmitter;
    }

    /**
     * @desc Permite obtener una lista de objetos de acuerdo a una paginación. Se envia
     * como parametros el nombre del servicio, token, página, numero de items y el filtro
     * @returns
     */
    getObjectsPagination(servicio, token, page, numberItems, filter) {
        typeof filter === 'undefined' ? filter = '' : filter;
        let parametros = {page: page, numberItems: numberItems, filter: filter};
        let options = this.getRequestOptions(token, parametros);

        return this.http.get(servicio, options)
            .map((response: ResponseCount) => {
                this.numberTotalItems = response.count;
                this.numberTotalPages = Math.ceil(response.count / numberItems);
                return response
            });
    }

    /**
     * @desc Permite descargar un archivo por post enviando como
     * parametros el nombre del servicio, los datos y el token. El archivo
     * se descarga y se asigna el nombre del parametro nameFile, ejemplo: archivo.xlsx
     * @returns
     */
    printObjetoBlobPorPostByNameFile(servicio, data, token, nameFile, homeComponent = null) {
        let options = this.getRequestOptions(token);
        options['responseType'] = 'blob';
        if (homeComponent) {
            homeComponent.cambioEstadoCargando();
        }
        this.http.post<HttpResponse<any>>(servicio, data, options).subscribe(res => {
            let blob = new Blob([res], {type: "" + res['type']});

            if (window.navigator && window.navigator.msSaveOrOpenBlob) {
                window.navigator.msSaveOrOpenBlob(blob);
                return;
            }

            // For other browsers, create a link pointing to the ObjectURL containing the blob.
            let urlBlob = window.URL.createObjectURL(blob);
            var link = document.createElement('a');
            link.href = urlBlob;
            link.download = nameFile;
            link.click();
            if (homeComponent) {
                homeComponent.cambioEstadoCargando();
            }
        });
    }

    /**
     * @desc Permite obtener y mostrar un objeto PDF por post enviando como
     * parametros el nombre del servicio, los datos y el token.
     * @returns
     */
    printObjetoBlobPorPost(servicio, data, token, homeComponent = null) {
        let options = this.getRequestOptions(token);
        options['responseType'] = 'blob';
        if (homeComponent) {
            homeComponent.cambioEstadoCargando();
        }
        this.http.post<HttpResponse<any>>(servicio, data, options).subscribe(res => {
            let blob = new Blob([res], {type: "" + res['type']});
            let urlBlob = window.URL.createObjectURL(blob);
            window.open(urlBlob);
            if (homeComponent) {
                homeComponent.cambioEstadoCargando();
            }
        });
    }


    /**
     * Metodo que retorna el HttpHeaders para consumir el API
     * @returns {*}
     */
    getRequestOptions(authToken, parametros = {}) {
        let headers = {'Content-Type': 'application/json'};
        headers[ComunEnum.AUTHORIZATION] = 'Token '+authToken;
        return {headers: headers, params: parametros};
    }
}

export interface ResponseCount {
    status: number;
    data: any;
    message: string;
    count: number
}
