/* Autor: Yazber Romero.
 * Fecha: 27/07/2016
 * ----------------------------Historial---------------------------
 * Autor                     	Fecha:                           	Descripcion  
 * Yazber Romero      	        27/07/2016                   	    Implementación inicial.
 */
import {Pipe, PipeTransform} from '@angular/core';
import {IPrestacionRep} from '../dto/IPrestacionRep';
import * as moment from 'moment';

@Pipe({
    name: 'reporteDinamicoPipe',
})

export class reporteDinamicoPipe implements PipeTransform {

    resultado: IPrestacionRep[] = [];

    transform(items: any[], carreraId, tipoReporte, fechaDesde, fechaHasta): any {
        this.resultado = [];
        if (fechaDesde && fechaHasta && tipoReporte) {
            if (tipoReporte == 1) {
                if (carreraId > 0) {
                    var filtrados = items.filter(item => item.carrera ? item.carrera.id == carreraId : null);
                    return this.groupByPrestacionesCarrera(filtrados, this.resultado);
                } else {
                    return this.groupByPrestacionesCarrera(items, this.resultado);
                }
            } else {
                return this.groupByPrestacionesPersona(items, this.resultado);
            }
        }

    }

    /**
     * Permite agrupar los detalles de prestaciones por carreras
     * @param  {any[]} items
     * @param  {any[]} resultado
     */
    groupByPrestacionesCarrera(items: any[], resultado: any[]) {
        items.forEach(item => {
            this.selectedItem(item, resultado)
        });
        return resultado;
    }

    /**
     * Permite agrupar los detalles de prestaciones por personas
     * @param  {any[]} items
     * @param  {any[]} resultado
     */
    groupByPrestacionesPersona(items: any[], resultado: any[]) {
        items.forEach(item => {
            this.selectedItemPersona(item, resultado)
        });
        return resultado;
    }

    /**
     * Permite validar la existencia de un detalle de prestacion por carrera
     * @param  {} item
     * @param  {} list
     */
    selectedItem(item, list) {
        var check = moment(item.fecha_registro, 'YYYY-MM-DD');
        var mesItem = check.format('M');
        var anioItem = check.format('YYYY');

        var idx = list.findIndex(function (element) {
            var fechaList = moment(item.fecha_registro, 'YYYY-MM-DD');
            var mesList = fechaList.format('M');
            var anioList = fechaList.format('YYYY');
            return anioList == anioItem && mesList == mesItem && item.carrera == element.carrera;
        });
        if (idx > -1) {
            list[idx].cantidad++;
        } else {
            item.anio = anioItem;
            item.mes = this.asignaMes(parseInt(mesItem));
            item.idMes = mesItem;
            item.cantidad = 1;
            list.push(item);
        }

    };

    /**
     * Permite especificar un detalle de prestacion  por persona
     * @param  {} item
     * @param  {} list
     */
    selectedItemPersona(item, list) {

        var check = moment(item.fecha_registro, 'YYYY-MM-DD');
        var mesItem = check.format('M');
        var anioItem = check.format('YYYY');
        var idx = list.findIndex(function (element) {

            var fechaList = moment(item.fecha_registro, 'YYYY-MM-DD');
            var mesList = fechaList.format('M');
            var anioList = fechaList.format('YYYY');
            return item.persona.id == element.persona.id &&
                anioList == anioItem && mesList == mesItem;

        });

        if (idx > -1) {
            list[idx].cantidad++;
        } else {
            item.anio = anioItem;
            item.mes = this.asignaMes(parseInt(mesItem));
            item.idMes = mesItem;
            item.cantidad = 1;
            list.push(item);
        }
    };

    /**
     * Obtener el mes correspiente
     * @param  {number} idMes
     */
    asignaMes(idMes: number) {

        switch (idMes) {
            case 1:
                return 'Enero';
            case 2:
                return 'Febrero';
            case 3:
                return 'Marzo';
            case 4:
                return 'Abril';
            case 5:
                return 'Mayo';
            case 6:
                return 'Junio';
            case 7:
                return 'Julio';
            case 8:
                return 'Agosto';
            case 9:
                return 'Septiembre';
            case 10:
                return 'Octubre';
            case 11:
                return 'Noviembre';
            case 12:
                return 'Diciembre';
            default:
                break;
        }
    }
}
