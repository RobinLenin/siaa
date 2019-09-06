import {Component, OnInit} from "@angular/core";
import {Router} from "@angular/router";
import {TranslateService} from "@ngx-translate/core";
import {DetalleParametrizacionService} from "../configuracion/services/detalle-parametrizacion.service";
import {FuncionalidadService} from "../seguridad/services/funcionalidad.service";
import {UsuarioService} from "../seguridad/services/usuario.service";
import {Usuario} from "../seguridad/models/usuario.model";
import {FuncionalidadGroup} from "../seguridad/models/funcionalidad-group.model";
import {DetalleParametrizacionEnum} from "../shared/comun/utils/enums";
import {MediaChange, ObservableMedia} from "@angular/flex-layout";
import {Subscription} from "rxjs";

@Component({
    moduleId: module.id,
    selector: 'home',
    templateUrl: './home.component.html'
})

export class HomeComponent implements OnInit {

    public usuario: Usuario;
    public funcionalidades: FuncionalidadGroup[];
    public cargando:boolean=false;
    private watcher: Subscription;
    isOpen = true;
    mode = 'side';
    estilo = 'width-20 sidebar-left';

    constructor(private router: Router,
                 private detalleParametrizacion: DetalleParametrizacionService,
                 private funcionalidadService: FuncionalidadService,
                 private usuarioService: UsuarioService,
                 public translate: TranslateService,
                 private media: ObservableMedia) {

        let token = window.localStorage.getItem('auth_key');
        if (token != null) {
            this.getUsuarioLogueado();
            this.cargarConfiguraciones();
            this.cargarFuncionalidadesGroup();
            this.router.navigate(['home/dashboard']);
        } else {
            this.router.navigate(['login'])
        }
        this.watcher = media.subscribe((change: MediaChange) => {
            let isMobile = (change.mqAlias == 'xs') || (change.mqAlias == 'sm');
            this.isOpen = !isMobile;
            if (isMobile) {
                this.mode = 'over';
                this.estilo = ''
            }else {
                this.mode = 'side';
                this.estilo = 'width-20 sidebar-left';
            }
        });
    }

    ngOnInit() {

    }


    /**
     * @desc Función que obtiene datos de inicio
     * relacionado a la configuración de las tablas
     */
    cargarConfiguraciones() {
        var token = window.localStorage.getItem('auth_key')
        this.detalleParametrizacion.getDetalleParametrizacionPorCodigo(token, DetalleParametrizacionEnum.ROWS_TABLE)
            .subscribe(res => {
            if (res.status == 200 && res.data) {
                localStorage.setItem(DetalleParametrizacionEnum.ROWS_TABLE, res.data.valor)
            }
        })
    }

    /* @desc Función que obtiene las funcionalidades
     * habilitadas para el usuario y que son presentadas
     * en el menu principal
     */
    cargarFuncionalidadesGroup() {
        var token = window.localStorage.getItem('auth_key')
        this.funcionalidadService.getFuncionalidadesAccesoUsuario(token).subscribe(datos => this.funcionalidades = datos);
    }

    /**
     * @desc Función que obtiene datos del usuario que
     * esta actualmente logeado
     */
    getUsuarioLogueado() {
        var token = window.localStorage.getItem('auth_key')
        this.usuarioService.getUsuarioLogueado(token).subscribe(data => this.usuario = data);

    }

    /**
     * @desc Función que finaliza el inicio de sesión
     * del usuario
     */
    logout() {
        window.localStorage.removeItem('auth_key')
        localStorage.removeItem(DetalleParametrizacionEnum.ROWS_TABLE)
        this.router.navigate(['']);
    }

    /**
     * @desc Función que cambia el estado de la variable cargando, por el
     * parametro que recibe o por la varibale actual que posee
     */
    cambioEstadoCargando(estado=null){
        if(typeof estado == 'boolean'){
            this.cargando=estado;
        }else{
            this.cargando=!this.cargando;
        }
    }

}
