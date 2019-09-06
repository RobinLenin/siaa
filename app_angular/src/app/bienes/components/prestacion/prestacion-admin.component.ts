/* Autor: Yazber Romero.
 * Fecha: 27/07/2016
 * ----------------------------Historial---------------------------
 * Autor                     	Fecha:                           	Descripcion  
 * Yazber Romero      	        27/07/2016                   	    Implementación inicial.
 */
import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {Router} from '@angular/router';
import {FormBuilder} from '@angular/forms';
import {IPrestacion} from './../../dto/IPrestacion';
import {PrestacionService} from './../../services/prestacion.service';
import {CatalogoItemService} from '../../../core/services/catalogo-item.service';
import {DetallePrestacionService} from './../../services/detalle-prestacion.service';
import {ConfigService} from '../../services/configure.service';

import {ICatalogoItem} from '../../dto/ICatalogoItem';
import {NotificationService} from '../../services/notificacion.service';
import {StatusRestEnum} from '../../../shared/comun/utils/enums';
import {UtilService} from './../../../shared/comun/services/util.service';
import {AccionEnum} from './../../../shared/comun/utils/enums';
import * as moment from 'moment';
import {FuncionalidadService} from "../../../seguridad/services/funcionalidad.service";

@Component({
    moduleId: module.id,
    selector: 'admin-prestacion',
    templateUrl: './prestacion-admin.component.html',

})
export class PrestacionAdminComponent implements OnInit {

    @Input() prestacion: IPrestacion;
    @Input() configuration: ConfigService;
    @Input() numberOfItems: number;
    errorMessage: string;
    tipoPrestacion: ICatalogoItem;
    tipoEnte: ICatalogoItem;
    estadoFinaliza: ICatalogoItem;
    estadoActiva: ICatalogoItem;
    razonGrupal_id: number;
    tipoPrestacion_id: number;
    funcionPrestacion: ICatalogoItem;
    isGrupal = false;
    numRegistro: number = 0;
    esVisible: boolean = false;
    esEditable: boolean = false;
    @Output() notificador = new EventEmitter();

    constructor(
        private router: Router,
        private service: DetallePrestacionService,
        private prestacion_service: PrestacionService,
        private catalogo_service: CatalogoItemService,
        private config: ConfigService,
        private serviceUtil: UtilService,
        private notificationService: NotificationService,
        private funcionalidadService: FuncionalidadService,
        fb: FormBuilder) {

    }

    ngOnInit() {
        var p = {
            id: null,
            fecha_registro: moment(new Date()).format('YYYY-MM-DD'),
            codigo: 'xxxxx',
            tipo_id: 0,
            usuario_id: 2707,
            detalles: null
        }
        p.detalles = {id: 0}
        this.prestacion = p;
        this.prestacion.detalles = [];
        this.setData();
        this.onFijaItems();
        this.loadForm();

    }

    /**
     * Permite cargar las personas a los detalles de prestaciones Seccion de change
     * @param  {} value
     */
    onChangePersona(value) {
        this.prestacion.detalles = [];
        for (let item of value) {
            var detallePrestacion = {
                id: null,
                fecha_registro: moment(new Date()).format('YYYY-MM-DD'),
                fecha_finalizacion: null,
                hora_entrada: new Date().toLocaleTimeString(),
                hora_salida: null,
                numero: 0,
                persona: item,
                persona_id: item.id,
                carrera_id: null,
                razon_id: 0,
                estado_id: this.estadoActiva.id,
                funcion_id: this.funcionPrestacion.id,
                tipo_ente_id: this.tipoEnte.id,
                activo: true
            }
            this.prestacion.detalles.push(detallePrestacion);
        }
    }

    /**
     * Permite guardar-editar Prestacion especifica
     * @param  {} item
     */
    onGuardar(item) {
        var token = window.localStorage.getItem('auth_key');
        this.prestacion.tipo_id = this.tipoPrestacion_id;
        this.prestacion_service.guardar(this.prestacion, token)
            .subscribe(res => {
                if (res.status == StatusRestEnum.HTTP_200_OK) {
                    let link = ['home/prestaciones'];
                    this.router.navigate(link);
                    this.notificationService.printSuccessMessage('Se Registraron ' + this.prestacion.detalles.length + ' Prestaciones Exitosamente');

                } else {
                    this.notificationService.printErrorMessage('Existen problemas de creacion' + res.status);
                    if (res.status == StatusRestEnum.HTTP_401_UNAUTHORIZED) {
                        let link = ['home/unauthorized'];
                        this.router.navigate(link);
                    }

                }
            })
    }

    /**
     * Permite editar detalle de prestaciones especifica
     * @param  {} item
     */
    onActualizarDetalle(item) {
        this.prestacion.tipo_id = this.tipoPrestacion_id;
        this.prestacion_service.actualizarDetalle(item)
            .subscribe(res => {
                if (res.status == StatusRestEnum.HTTP_200_OK) {
                    //Todo revisar este redireccionamiento se lo puso aqui x no visualizarse el cambio de estado
                    let link = ['home/prestaciones'];
                    this.router.navigate(link);
                } else {
                    if (res.status == StatusRestEnum.HTTP_401_UNAUTHORIZED) {
                        let link = ['home/unauthorized'];
                        this.router.navigate(link);
                    }
                }
            })
    }

    /**
     * Permite remover prestacion especifica para el indice indicado
     * @param  {} indice
     */
    onRemove(indice) {
        this.prestacion.detalles.splice(indice, 1);
    }

    /**
     * Permite manejar evento de tipo de prestaciones
     */
    onTipoPrestacion(item) {
        this.tipoPrestacion_id = item;
        this.tipoPrestacion.id == item ?
            this.isGrupal = false : this.isGrupal = true

    }

    /*
     * Permite realizar la actualizacion prestaciones
     */
    onActualizarPrestaciones() {
        this.prestacion.detalles.forEach(detalle => {
            this.onActualizarDetalle(detalle);
            this.numRegistro++;
        });
        this.notificationService.printSuccessMessage('Se actualiza ' + this.numRegistro + ' Prestaciones Exitosamente');
    }

    /*
    * Permite realizar la finalizacion grupal de prestaciones
    */
    onFinalizaPrestaciones() {
        //1. Obtener el listado de prestaciones
        this.prestacion.detalles.forEach(detalle => {
            console.log(detalle);
            //2. Registrar las prestaciones diferente de finalizada
            if (detalle.estado_id != this.estadoFinaliza.id) {
                detalle.estado_id = this.estadoFinaliza.id;
                if (this.isGrupal) {
                    detalle.razon_id = this.razonGrupal_id;
                }
                detalle.hora_salida = new Date().toLocaleTimeString();
                detalle.fecha_finalizacion = moment(new Date()).format('YYYY-MM-DD');
                this.numRegistro++;
            }
            this.onActualizarDetalle(detalle);
        });
        this.notificationService.printSuccessMessage('Se finalizaron ' + this.numRegistro + ' Prestaciones Exitosamente');
    }

    /**
     * Permite crear las prestaciones
     */
    onCrearPrestaciones() {
        //1. Obtener el listado de prestaciones
        this.prestacion.detalles.forEach(detalle => {
            //2. Registrar las prestaciones diferente de finalizada
            if (detalle.estado_id != this.estadoFinaliza.id) {
                if (this.isGrupal) {
                    detalle.razon_id = this.razonGrupal_id;
                }
            }
        });
        this.onGuardar(this.prestacion);

    }

    /**
     * Fija la prestacion Individual
     */
    onFijaItems() {
        //fija el tipo de item tipo de prestacion Individual
        var token = window.localStorage.getItem('auth_key');
        this.catalogo_service.getCatalogoItemPorCodigo('TIPO_PRES_IND', token)
            .subscribe(res => {
                this.tipoPrestacion = res.data;
                this.tipoPrestacion_id = this.tipoPrestacion.id;
            });
        //fija el tipo de item estado de prestacion finalizado
        this.catalogo_service.getCatalogoItemPorCodigo('EST_PRES_FINALIZA', token)
            .subscribe(res => {
                this.estadoFinaliza = res.data;
            });
        //fija el tipo de item prestacion es nueva EST_PRES_ACTIVO
        this.catalogo_service.getCatalogoItemPorCodigo('EST_PRES_ACTIVO', token)
            .subscribe(res => {
                this.estadoActiva = res.data;
            });

        //fija el tipo de item funcion solicitante
        this.catalogo_service.getCatalogoItemPorCodigo('FUN_PRES_SOL', token)
            .subscribe(res => {
                this.funcionPrestacion = res.data;
            });
        //fija el tipo de item tipo estudiantes
        this.catalogo_service.getCatalogoItemPorCodigo('TP_ENTE_EST', token)
            .subscribe(res => {
                this.tipoEnte = res.data;
            });
    }

    /**
     * Permite mapear los items a editar
     */
    setData() {
        if (this.existData()) {
            this.service.getDetallesPrestaciones().forEach(item => {
                var detallePrestacion = {
                    id: item.id,
                    fecha_registro: item.fecha_registro,
                    fecha_finalizacion: item.fecha_finalizacion,
                    hora_entrada: item.hora_entrada,
                    hora_salida: item.hora_salida,
                    numero: item.numero,
                    persona: item['persona'],
                    persona_id: item['persona']['id'],
                    carrera_id: item['carrera'] ? item['carrera']['id'] : null,
                    razon_id: item['razon']['id'],
                    estado_id: item['estado']['id'],
                    funcion_id: item['funcion']['id'],
                    tipo_ente_id: item['tipo_ente']['id'],
                    activo: item.activo
                }
                this.prestacion.detalles.push(detallePrestacion);
            })
        }
    }

    existData() {
        if (this.service.getDetallesPrestaciones().length > 0) {
            return true;
        }
    }

    /**
     * Permite realizar la accion de acuerdo a la seleccion previa
     */
    getFlujoAccionar(codigo) {
        switch (codigo) {
            case AccionEnum.CREAR:
                this.onCrearPrestaciones();
                break;
            case AccionEnum.EDITAR:
                this.onActualizarPrestaciones();
                break;
            case AccionEnum.FINALIZAR:
                this.onFinalizaPrestaciones();
                break;
            default:
                break;
        }

    }

    /**
     * Dispara la accion en base a contexto actual previamente seleccionado
     */
    onAccion() {
        var codigo = this.funcionalidadService.getCodigoFuncionalidad();
        this.getFlujoAccionar(codigo);
    }

    /**
     * Permite controlar presentacion de Formulario
     */
    loadForm() {
        var codigo = this.funcionalidadService.getCodigoFuncionalidad();
        switch (codigo) {
            case AccionEnum.CREAR:
                this.esVisible = true;
                this.esEditable = false;
                break;
            case AccionEnum.EDITAR:
                this.esVisible = false;
                this.esEditable = false;
                break;
            case AccionEnum.FINALIZAR:
                this.esVisible = false;
                this.esEditable = true;
                break;
            default:
                break;
        }

    }

}

