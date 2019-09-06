import {Injectable} from "@angular/core";
import { HttpClient} from "@angular/common/http";
import {appService} from "./../../credentials";
import {CarrerasResponse } from "../models/carrera.model";


@Injectable()
export class CarreraService {

    constructor(private http: HttpClient) {
    }

    getCarrerasVigentes() {
        return this.http.get<CarrerasResponse>(appService.ws_curricular_carrera_lista_vigentes)
    }

}
