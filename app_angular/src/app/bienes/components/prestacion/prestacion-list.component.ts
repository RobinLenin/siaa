/* Autor: Yazber Romero.
 * Fecha: 27/07/2016
 * ----------------------------Historial---------------------------
 * Autor                     	Fecha:                           	Descripcion  
 * Yazber Romero      	        27/07/2016                   	    Implementación inicial.
 */
import {Component, Input, OnInit} from "@angular/core";
import {Router} from "@angular/router";
import {DetallePrestacionService} from "../../services/detalle-prestacion.service";
import {IDetallePrestacion} from "../../dto/IDetallePrestacion";
import {ConfigService} from "../../services/configure.service";
import {ResourceService} from "../../../shared/comun/services/resource.service";
import {UtilService} from "../../../shared/comun/services/util.service";
import {ComunEnum, DetalleParametrizacionEnum, StatusRestEnum} from "../../../shared/comun/utils/enums";
import {appService} from "../../../credentials";
import {IAccionToolbar} from "../toolbar/IAccionToolbar";
import {NotificationService} from '../../services/notificacion.service';
import {PrestacionService} from './../../services/prestacion.service';

@Component({
	moduleId: module.id,
	selector: 'list-prestacion',
	templateUrl: './prestacion-list.component.html',
	styleUrls: ['./prestacion-list.component.css']
})
export class PrestacionListComponent implements OnInit {

	/*Seccion de Atributos*/
	displayedColumns: string[] = ['action', 'codigo_prestacion', 'fecha_registro', 'hora_entrada', 'fecha_finalizacion', 'hora_salida', 'numero', 'numero_documento', 'nombres', 'apellidos', 'carrera', 'estado', 'finalizar'];
	detallesPrestaciones: IDetallePrestacion[];
	detallesPrestacionSelect: IDetallePrestacion[];
	operaciones: IAccionToolbar[];
	@Input() configuration: ConfigService;
	numberOfItemsPerPage: number = 0;
	query: string;
	servicio: string;
	token: string;
	columns = [
		{title: 'Código', dataKey: 'codigo'},
		{title: 'Fecha de Regístro', dataKey: 'fecha_r'},
		{title: 'Hora de Entrada', dataKey: 'hora_e'},
		{title: 'Fecha de Finalización', dataKey: 'fecha_f'},
		{title: 'Hora de Salida', dataKey: 'hora_s'},
		{title: 'Número', dataKey: 'numero'},
		{title: 'DNI', dataKey: 'dni'},
		{title: 'Nombres', dataKey: 'nombres'},
		{title: 'Apellidos', dataKey: 'apellidos'},
		{title: 'Carrera', dataKey: 'carrera'},
		{title: 'Estado', dataKey: 'estado'},
	];
	dataPDF: any;

	constructor(private router: Router,
				 private service: DetallePrestacionService,
				 private serviceUtil: UtilService,
				 public config: ConfigService,
				 public resource: ResourceService,
				 private notificationService: NotificationService,
				 private prestacion_service: PrestacionService
				) {
	}

	cargardp(event){
		this.detallesPrestaciones=event;
		this.getDataPDF(this.detallesPrestaciones);
	}

	ngOnInit() {
		this.detallesPrestacionSelect = [];
		this.operaciones = [];
		this.loadDetallePrestaciones();
		this.loadOperaciones();
		this.service.setDetallesPrestaciones(this.detallesPrestacionSelect);
		this.service.setEditar(false);
	}


	/**
    * @desc Funcion que genera un areglo para ser enviado a Imprimir
    */
	getDataPDF(list) {
		var data = [];
		if(list){
			for (let item of list){
				data.push({
					codigo: item.codigo_prestacion,
					fecha_r: item.fecha_registro,
					hora_e: item.hora_entrada,
					fecha_f: item.fecha_finalizacion,
					hora_s: item.hora_salida,
					numero: item.numero,
					dni: item.persona.numero_documento,
					nombres: item.persona.primer_nombre+" "+item.persona.segundo_nombre,
					apellidos: item.persona.primer_apellido+" "+item.persona.segundo_apellido,
					carrera: item.carrera.nombre,
					estado: item.estado.nombre
				});
			}
			this.dataPDF = data;
		}
	}

	loadOperaciones() {
		var op_uno = { codigo: 'finalizar', nombre: 'Finalizar', icono: '', path: 'home/prestacion',desabilitar:false }
		var op_dos = { codigo: 'detalles', nombre: 'Detalles', icono: '', path: 'home/prestacion',desabilitar:true }
		this.operaciones.push(op_uno);
		this.operaciones.push(op_dos);
	}

	/**
     * Permite cargar los detalles de  prestaciones 
     */
	loadDetallePrestaciones() {
		this.token = localStorage.getItem(ComunEnum.AUTH_KEY);
		this.numberOfItemsPerPage = Number(localStorage.getItem(DetalleParametrizacionEnum.ROWS_TABLE))
		this.servicio = appService.ws_bienes_detalle_prestacion_lista;

	}

	/**
     * Permite agregar los detalles seleccionados
     * @param  {} item
     * @param  {} list
     */
	selectedItem(item, list) {
		this.serviceUtil.seleccionarItem(item, list);
		this.service.setDetallesPrestaciones(this.detallesPrestacionSelect);
		this.service.setEditar(true);
		if(this.detallesPrestacionSelect.length > 0){
			this.getDataPDF(this.detallesPrestacionSelect);
		}else{
			this.getDataPDF(this.detallesPrestaciones);
		}
	};



	/** Permite indicar si se encuentra o no agregado un detalle
     * @param  {} item
     * @param  {} list
     */
	exists(item, list) {
		return this.serviceUtil.existeItem(item, list);
	}

	/**
    * Permite crear las prestaciones
    */
	onFinalizaPrestaciones(element) {
		element.estado_id = 613;
		element.hora_salida = new Date().toLocaleTimeString();
		var date = new Date();
		element.fecha_finalizacion = date.getFullYear()+'-'+(date.getMonth()+1)+'-'+date.getDate();
		this.onActualizarDetalle(element);
		this.notificationService.printSuccessMessage('Se finalizó 1 Prestación Exitosamente');
	}

	onActualizarDetalle(element) {
		this.prestacion_service.actualizarDetalle(element)
			.subscribe(res => {
			if (res.status == StatusRestEnum.HTTP_200_OK) {
				element.estado = res.data.estado;
			} else {
				if (res.status == StatusRestEnum.HTTP_401_UNAUTHORIZED) {
					let link = ['home/unauthorized'];
					this.router.navigate(link);
				}
			}
		});
	}

	onChangePersona(item) {
		item.persona_id = item.persona.id;
		item.carrera_id= item.carrera.id;
		item.razon_id= item.razon.id;
		item.estado_id= item.estado.id;
		item.funcion_id= item.funcion.id;
		item.tipo_ente_id= item.tipo_ente.id;
		item.activo= true;
		this.onFinalizaPrestaciones(item);
	}

}
