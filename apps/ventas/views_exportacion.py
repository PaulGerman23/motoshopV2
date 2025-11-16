# apps/ventas/views_exportacion.py
# Agregar al proyecto: pip install reportlab openpyxl

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from datetime import datetime, timedelta

from .models import Venta, DetalleVenta, CierreCaja


@login_required
def exportar_venta_pdf(request, venta_id):
    """Exporta una venta individual a PDF (ticket)"""
    venta = get_object_or_404(Venta, id=venta_id)
    
    # Crear respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="venta_{venta.codigo_venta}.pdf"'
    
    # Crear documento PDF
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilo personalizado para el título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Encabezado
    elements.append(Paragraph('MotoShop', title_style))
    elements.append(Paragraph('Sistema de Gestión de Inventario', styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Información de la venta
    info_data = [
        ['Comprobante de Venta', ''],
        ['Número de Venta:', f'#{venta.codigo_venta}'],
        ['Fecha:', venta.fecha.strftime('%d/%m/%Y %H:%M')],
        ['Cliente:', venta.cliente.nombre_completo if venta.cliente else 'Consumidor Final'],
        ['Vendedor:', f'{venta.usuario.first_name} {venta.usuario.last_name}'],
        ['Método de Pago:', venta.get_tipo_pago_display()],
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Detalles de productos
    detalles = venta.detalles.filter(status=1)
    
    productos_data = [['Cant.', 'Descripción', 'Precio Unit.', 'Subtotal']]
    
    for detalle in detalles:
        productos_data.append([
            str(detalle.cantidad),
            detalle.producto.descripcion if detalle.producto else 'Producto eliminado',
            f'${detalle.precio_unitario:.2f}',
            f'${detalle.subtotal:.2f}'
        ])
    
    productos_table = Table(productos_data, colWidths=[1*inch, 3*inch, 1.5*inch, 1.5*inch])
    productos_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
    ]))
    
    elements.append(productos_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Total
    total_data = [
        ['TOTAL:', f'${venta.total:.2f}']
    ]
    
    total_table = Table(total_data, colWidths=[5*inch, 1.5*inch])
    total_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('PADDING', (0, 0), (-1, -1), 12),
    ]))
    
    elements.append(total_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Pie de página
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph('Gracias por su compra', footer_style))
    elements.append(Paragraph('www.motoshop.com | Tel: (387) 123-4567', footer_style))
    
    # Construir PDF
    doc.build(elements)
    
    return response


@login_required
def exportar_ventas_excel(request):
    """Exporta todas las ventas a Excel"""
    # Obtener parámetros de fecha
    fecha_desde = request.GET.get('desde')
    fecha_hasta = request.GET.get('hasta')
    
    # Filtrar ventas
    ventas = Venta.objects.filter(estado=1, estado_venta__in=[1, 2]).select_related('cliente', 'usuario')
    
    if fecha_desde:
        ventas = ventas.filter(fecha__gte=fecha_desde)
    if fecha_hasta:
        ventas = ventas.filter(fecha__lte=fecha_hasta)
    
    ventas = ventas.order_by('-fecha')
    
    # Crear workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Ventas"
    
    # Estilos
    header_fill = PatternFill(start_color="667EEA", end_color="667EEA", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Encabezados
    headers = ['Código', 'Fecha', 'Cliente', 'Vendedor', 'Total', 'Método Pago', 'Estado']
    
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = border
    
    # Datos
    for row_num, venta in enumerate(ventas, 2):
        ws.cell(row=row_num, column=1, value=venta.codigo_venta).border = border
        ws.cell(row=row_num, column=2, value=venta.fecha.strftime('%d/%m/%Y %H:%M')).border = border
        ws.cell(row=row_num, column=3, value=venta.cliente.nombre_completo if venta.cliente else 'Consumidor Final').border = border
        ws.cell(row=row_num, column=4, value=f'{venta.usuario.first_name} {venta.usuario.last_name}').border = border
        
        cell_total = ws.cell(row=row_num, column=5, value=float(venta.total))
        cell_total.number_format = '$#,##0.00'
        cell_total.border = border
        
        ws.cell(row=row_num, column=6, value=venta.get_tipo_pago_display()).border = border
        ws.cell(row=row_num, column=7, value=venta.get_estado_venta_display()).border = border
    
    # Ajustar anchos de columna
    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 18
    ws.column_dimensions['C'].width = 25
    ws.column_dimensions['D'].width = 20
    ws.column_dimensions['E'].width = 15
    ws.column_dimensions['F'].width = 20
    ws.column_dimensions['G'].width = 15
    
    # Agregar total general
    row_total = len(ventas) + 2
    ws.cell(row=row_total, column=4, value='TOTAL GENERAL:').font = Font(bold=True)
    total_formula = f'=SUM(E2:E{len(ventas)+1})'
    cell_total_general = ws.cell(row=row_total, column=5, value=total_formula)
    cell_total_general.font = Font(bold=True, size=12)
    cell_total_general.number_format = '$#,##0.00'
    cell_total_general.fill = PatternFill(start_color="10B981", end_color="10B981", fill_type="solid")
    
    # Crear respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="ventas_{datetime.now().strftime("%Y%m%d")}.xlsx"'
    
    wb.save(response)
    
    return response


@login_required
def exportar_cierre_pdf(request, cierre_id):
    """Exporta un cierre de caja a PDF"""
    cierre = get_object_or_404(CierreCaja, id=cierre_id)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="cierre_caja_{cierre.fecha}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph('MotoShop - Cierre de Caja', title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Información del cierre
    info_data = [
        ['Fecha:', cierre.fecha.strftime('%d/%m/%Y')],
        ['Usuario:', str(cierre.usuario)],
        ['Hora de Cierre:', cierre.fecha_cierre.strftime('%H:%M:%S')],
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Resumen de ventas
    ventas_data = [
        ['Resumen de Ventas', ''],
        ['Monto Inicial:', f'${cierre.monto_inicial:.2f}'],
        ['Cantidad de Ventas:', str(cierre.cantidad_ventas)],
        ['Total Ventas:', f'${cierre.total_ventas:.2f}'],
    ]
    
    ventas_table = Table(ventas_data, colWidths=[3*inch, 2*inch])
    ventas_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
    ]))
    
    elements.append(ventas_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Desglose por método de pago
    metodos_data = [
        ['Método de Pago', 'Monto'],
        ['Efectivo', f'${cierre.efectivo_ventas:.2f}'],
        ['Débito', f'${cierre.debito_ventas:.2f}'],
        ['Crédito', f'${cierre.credito_ventas:.2f}'],
        ['Transferencia', f'${cierre.transferencia_ventas:.2f}'],
    ]
    
    metodos_table = Table(metodos_data, colWidths=[3*inch, 2*inch])
    metodos_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    
    elements.append(metodos_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Totales finales
    totales_data = [
        ['Monto Final Esperado:', f'${cierre.monto_final_esperado:.2f}'],
        ['Monto Final Real:', f'${cierre.monto_final_real:.2f}'],
        ['Diferencia:', f'${cierre.diferencia:.2f}'],
    ]
    
    totales_table = Table(totales_data, colWidths=[3*inch, 2*inch])
    
    # Color de la diferencia según signo
    diferencia_color = colors.HexColor('#10b981') if cierre.diferencia >= 0 else colors.HexColor('#ef4444')
    
    totales_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEABOVE', (0, 0), (-1, 0), 2, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 2, colors.black),
        ('TEXTCOLOR', (0, -1), (-1, -1), diferencia_color),
        ('FONTSIZE', (0, -1), (-1, -1), 13),
    ]))
    
    elements.append(totales_table)
    
    # Construir PDF
    doc.build(elements)
    
    return response