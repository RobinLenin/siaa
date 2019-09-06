# -*- coding: utf-8 -*-
import datetime

from django.http import HttpResponse
from xlwt import *

COLORES = {'black': 0, 'white': 1, 'red': 2, 'dark gray': 22, "green": 3, "blue": 4, "yellow": 5,
           "magenta": 6, "cyan": 7, "maroon": 16, "dark_green": 17, "dark_blue": 18, "dark_yellow": 19,
           "dark_magenta": 20, "teal": 21, "light_gray": 22, "dark_gray": 23}

def retornar_excel(nombre_reporte, filas, cabeceras=[], filtros=[], tamanio_columnas=[], titulo="Reporte", alto_filas=1):
    """
    Genera y retorna el reporte excel
    :param nombre_reporte:
    :param filas:
    :param cabeceras:
    :param filtros:
    :param tamanio_columnas:
    :param titulo:
    :param alto_filas:
    :return:
    """
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="%s%s.xls"' % (
        nombre_reporte, datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    )
    workbook = generar_excel(filas=filas,
                             cabeceras=cabeceras,
                             filtros = filtros,
                             tamanio_columnas= tamanio_columnas,
                             titulo=titulo,
                             alto_filas=alto_filas)
    workbook.save(response)
    return response


def generar_excel(filas, cabeceras=[], filtros=[], tamanio_columnas=[], titulo="Reporte", alto_filas=1):
    """
    Genera el reporte excel a presentar
    :param self:
    :param filas: [["dato1","dato2"...],["dato1","dato2"...]]
    :param cabeceras: ["titulo1", "titulo2",...]
    :param filtros: [("Clave:", "Valor"), ("Clave:", "Valor")]
    :param tamanio_columnas: [int, int, ]
    :param titulo: String
    :param alto_filas: {columna:alto}
    :return: Workwook
    """
    try:
        hoy = datetime.datetime.now()
        workbook = Workbook(style_compression=2, encoding='utf-8')
        worksheet = workbook.add_sheet("Reporte")

        for k, v in enumerate(tamanio_columnas):
            worksheet.col(k).width = v

        worksheet.write_merge(1, 1, 0, 4, 'Universidad Nacional de Loja',
                              font_style_titulos_encabezado_pri(position='center', bold=1, color='black', tamano=250))
        worksheet.write_merge(2, 2, 0, 4, titulo,
                              font_style_titulos_encabezado_pri(position='center', bold=1, color='black', tamano=250))
        row = 6
        filtros.append(("Fecha Impresión", hoy.strftime("%Y-%m-%d %HH:%MM:%SS")))
        filtros.append(("Total Registros", len(filas)))
        for fila in filtros:
            if isinstance(fila, (list, tuple)) and len(fila) >= 2:
                worksheet.write_merge(row, row, 0, 1, fila[0],
                                      font_style_titulos_encabezado_pri(position='left', bold=1, color='black',
                                                                        tamano=200))
                worksheet.write_merge(row, row, 2, 3, fila[1],
                                      font_style_titulos_encabezado_pri(position='left', bold=0, color='black',
                                                                        tamano=200))
            else:
                worksheet.write(row, 0, fila,
                                font_style_titulos_encabezado_pri(position='left', bold=0, color='black', tamano=200))
            row += 1

        row += 1
        for columna, dato in enumerate(cabeceras):
            worksheet.write(row, columna, dato, font_style_datos(position='left', bold=1, color='black'))

        row += 1
        for fila in filas:
            if isinstance(fila, (list, tuple)):
                for columna, dato in enumerate(fila):
                    estilo_celda = font_style_datos(position='left', bold=0, color='black')
                    if isinstance(dato, datetime.date):
                        estilo_celda.num_format_str = 'dd/mm/yyyy'
                    worksheet.write(row, columna, dato, estilo_celda)
                    worksheet.row(row).height = 256 * alto_filas
            else:
                worksheet.write(row, 0, fila, font_style_filas())
            row += 1

        return workbook

    except Exception as e:
        print("Error en ExcelUtil: genererar_excel")
        print(e)
        return None


def font_style_titulos_encabezado_pri(position='center', bold=0, color='black', fondo='', tamano=200):
    font = Font()
    font.name = 'Verdana'
    font.bold = bold
    font.height = tamano
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    center.vert = Alignment.VERT_CENTER
    left = Alignment()
    left.horz = Alignment.HORZ_LEFT
    left.vert = Alignment.VERT_CENTER
    orient = Alignment()
    orient.orie = Alignment.ORIENTATION_90_CC

    style = XFStyle()
    if COLORES.get(fondo, False):
        pattern = Pattern()
        pattern.pattern = Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour = COLORES[fondo]
        style.pattern = pattern
    font.colour_index = COLORES.get(color, 0)
    style.font = font

    if position == 'center':
        style.alignment = center
    else:
        style.alignment = left
        
    return style


def font_style_filas():
    font = Font()
    font.height = 50 * 10
    borders = Borders()
    borders.left = 1
    borders.right = 1
    borders.top = 1
    borders.bottom = 1
    style = XFStyle()
    style.font = font
    style.borders = borders
    return style


def font_style_datos(position='center', bold=0, color='black', fondo='', familia='Verdana', tamano=200):
    font = Font()
    font.name = familia
    font.bold = bold
    font.height = tamano
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    center.vert = Alignment.VERT_CENTER
    left = Alignment()
    left.horz = Alignment.HORZ_LEFT
    left.vert = Alignment.VERT_CENTER
    orient = Alignment()
    orient.orie = Alignment.ORIENTATION_90_CC
    borders = Borders()
    borders.left = 1
    borders.right = 1
    borders.top = 1
    borders.bottom = 1

    style = XFStyle()
    if COLORES.get(fondo, False):
        pattern = Pattern()
        pattern.pattern = Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour = COLORES[fondo]
        style.pattern = pattern
    font.colour_index = COLORES.get(color, 0)
    style.font = font
    style.borders = borders

    if position == 'center':
        style.alignment = center
    else:
        style.alignment = left

    return style


