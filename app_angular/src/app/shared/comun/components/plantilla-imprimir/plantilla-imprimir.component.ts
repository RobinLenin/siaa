import { Component, OnInit, Input, Output, EventEmitter, ViewContainerRef} from '@angular/core';
import {DialogService} from "../../services/dialog.service";
import * as jspdf from 'jspdf';
import 'jspdf-autotable';
import html2canvas from 'html2canvas';

@Component({
    selector: 'plantilla-imprimir',
    templateUrl: './plantilla-imprimir.component.html'
})

export class PlantillaImprimirComponent implements OnInit {

    @Input() ejecutar: string;
    @Input() dataBruta: any[];
    @Input() activarImprimir: boolean;
    @Input() titulo: string;
    @Input() funcionalidad: string;
    @Input() reporte: string;
    @Input() data: any[];
    @Input() typeTable: string;
    @Input() columns: any[];
    @Input() departamento: string;
    @Output() pdf = new EventEmitter();
    base64Img: any;

    constructor(private dialogService: DialogService,
                 private viewContainerRef: ViewContainerRef) {
    }

    ngOnInit() {

    }

    generarDataReportePrestaciones(){
        var dataAux = [];
        if(this.dataBruta) {
            for(let item of this.dataBruta) {
                var carrera = "S/N";
                if(item.carrera){
                    carrera = item.carrera.nombre;
                }
                dataAux.push({
                    anio: item.anio,
                    mes: item.mes,
                    dni: item.persona.numero_documento,
                    nombres: item.persona.primer_nombre+' '+item.persona.segundo_nombre,
                    apellidos: item.persona.primer_apellido+' '+item.persona.segundo_apellido,
                    carrera: carrera,
                    cantidad: item.cantidad
                });
            }
            this.data = dataAux;
        }
    }

    imprimir() {
        var data = document.getElementById('content');
        html2canvas(data).then(canvas => {
            var imgWidth = 208;
            var pageHeight = 295;
            var imgHeight = canvas.height * imgWidth / canvas.width;
            var heightLeft = imgHeight;

            const contentDataURL = canvas.toDataURL('image/png');
            let pdf = new jspdf('p', 'mm', 'a4');
            var position = 0;
            pdf.addImage(contentDataURL, 'PNG', 0, position, imgWidth, imgHeight);
            pdf.save('reporte_prestaciones.pdf');
        });
    }

    imgToBase64(src,  callback) {
        var outputFormat = src.substr(-3) === 'png' ? 'image/png' : 'image/jpeg';
        var img = new Image();
        img.crossOrigin = 'Anonymous';
        img.onload = function() {
            var canvas = document.createElement('canvas');
            var ctx = canvas.getContext('2d');
            var dataURL;
            canvas.height = img.naturalHeight;
            canvas.width = img.naturalWidth;
            ctx.drawImage(img, 0, 0);
            dataURL = canvas.toDataURL(outputFormat);
            callback(dataURL);
        };
        img.src = src;
        if (img.complete || img.complete === undefined) {
            img.src = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==";
            img.src = src;
        }
    }

    generarPDF() {
        var msj = (this.columns.length > 4)? "La tabla contiene mas de 4 columnas, de preferencia la orientación debe ser Horizotal." : "Existen dos opciones de Impresión. Escoja la que mejor se adapte a su necesidad.";

        this.dialogService.imprimir('Imprimir ' + this.titulo, msj, this.viewContainerRef).subscribe(res => {
            if (res == true){
                this.construirPDF('l');
            }
            if (res == false){
                this.construirPDF('p');
            }
        });
    }

    construirPDF(orientacion){
        if(this.ejecutar=="GENERA_RP"){
            this.generarDataReportePrestaciones();
        }
        this.imgToBase64('assets/img/logo-UNL.png', base64 => {
            var totalPagesExp = "{total_pages_count_string}";
            var dep = this.departamento? this.departamento : "SIAAF";
            var func = this.funcionalidad;
            var doc = new jspdf(orientacion);
            var vl = 40;
            var pageContent = function(data) {
                var pageWidth = doc.internal.pageSize.width || doc.internal.pageSize.getWidth();
                var hei=0;
                //doc.setFontSize(20);
                doc.setTextColor(40);
                if (base64) {
                    doc.addImage(base64, 'PNG', data.settings.margin.left, 12, 53, 11);
                }
                doc.setFontSize(20);
                doc.setFontStyle('bold');
                var lineasWrap = doc.splitTextToSize(dep, (210-70-data.settings.margin.left));
                var len = lineasWrap.length;
                hei = (len == 1)? 25: (len*20);
                doc.text(lineasWrap, pageWidth-data.settings.margin.right, 18, 'right');
                doc.setFontSize(11);
                doc.setFontStyle('normal');
                lineasWrap = doc.splitTextToSize(func, (210-70-data.settings.margin.left));
                doc.text(lineasWrap, pageWidth-data.settings.margin.right, hei, 'right');
                len = lineasWrap.length;
                hei = (len == 1)? hei+3 : (len*10)
                doc.setLineWidth(0.5);
                doc.line(data.settings.margin.left, hei, pageWidth-data.settings.margin.right, hei);
                //				len = lineasWrap.length;
                //				hei = (len*32);
                hei += 20;
                vl = hei;
                //FOOTER
                var pageHeight = doc.internal.pageSize.height || doc.internal.pageSize.getHeight();
                doc.setLineWidth(0.5);
                doc.line(data.settings.margin.left, pageHeight - 24, pageWidth-data.settings.margin.right, pageHeight - 24);
                var str = "página " + data.pageCount;
                if (typeof doc.putTotalPages === 'function') {
                    str = str + " de " + totalPagesExp;
                }
                doc.setFontSize(8);
                doc.text('Ciudad Universitaria "Guillermo Falconí Espinosa" Casilla letra "S"', (pageWidth/2), pageHeight - 20, 'center');
                doc.text('Teléfono: 2547-252 Ext. 157', (pageWidth/2), pageHeight - 17, 'center');
                doc.setFontStyle('bold');
                doc.text('francisco.castillo@unl.edu.ec', (pageWidth/2), pageHeight - 14, 'center');
                doc.setFontStyle('normal');
                doc.text('Sistema de Información Académica, Administrativa y Financiera (SIAAF)', (pageWidth/2), pageHeight - 11, 'center');
                var fecha = new Date();
                doc.text(fecha.getDate()+"-"+(fecha.getMonth()+1)+"-"+fecha.getFullYear()+" "+fecha.getHours()+"h"+fecha.getMinutes()+"m"+fecha.getSeconds(), data.settings.margin.left, pageHeight - 8, 'left');
                doc.text(str, pageWidth-data.settings.margin.right+30, pageHeight - 8, 'right');
            };
            var pageWidth = doc.internal.pageSize.width || doc.internal.pageSize.getWidth();
            doc.text(this.titulo, (pageWidth/2), vl+8, 'center');
            doc.autoTable(this.columns, this.data, {
                addPageContent: pageContent,
                margin: {top: vl+12, bottom: 30},
                styles: {overflow: 'linebreak'}
            });

            if (typeof doc.putTotalPages === 'function') {
                doc.putTotalPages(totalPagesExp);
            }
            var fecha = new Date();
            doc.save(this.estandarNombre(this.departamento)+"_"+this.estandarNombre(this.funcionalidad)+"_"+this.estandarNombre(this.titulo)+"_"+fecha.getDate()+""+(fecha.getMonth()+1)+""+fecha.getFullYear()+"_"+fecha.getHours()+""+fecha.getMinutes()+".pdf");
            return doc;
            //this.pdf.emit(doc);
        });
    }
    /**
    * @desc metodo que elimina los pronombres el la los las de el texto
    * y devuelbe una string con el estilo "InformePago"
    */
    estandarNombre(texto){
        var res = "";
        let pronombres = ["el", "la", "los", "las", "de", "del", "y"];
        var depArr = texto.toLowerCase().split(" ");
        for(let i of depArr){
            if(!pronombres.includes(i)){
                res += i.charAt(0).toUpperCase() + i.substring(1);
            }
        }
        return res;
    }
}
