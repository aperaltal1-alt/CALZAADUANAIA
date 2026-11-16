"""Generate clearly marked illustrative documents; never impersonate SUNAT forms."""
from io import BytesIO
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

def _doc(title, case):
    doc=Document()
    section=doc.sections[0]; section.header.paragraphs[0].text='CALZADUANA IA | MODELO COMERCIAL REFERENCIAL'
    doc.add_heading(title, 0)
    p=doc.add_paragraph('EJEMPLO DIDÁCTICO — DATOS SIMULADOS. NO ES DOCUMENTO EMITIDO NI APROBADO POR SUNAT.')
    p.runs[0].bold=True; p.runs[0].font.color.rgb=RGBColor(177,42,42)
    doc.add_paragraph('No sustituye comprobantes electrónicos, declaraciones aduaneras ni documentos que deban emitir terceros o autoridades.')
    for k,v in [('Operación',case.get('operacion','')),('Mercancía',case.get('producto','')),('País asociado',case.get('pais','')),('Material superior',case.get('material','')),('Material planta',case.get('suela','')),('Condición',case.get('estado','')),('Cantidad (referencial)',case.get('cantidad',1))]:
        doc.add_paragraph(f'{k}: {v}')
    return doc

def commercial_invoice(case):
    d=_doc('FACTURA COMERCIAL / COMMERCIAL INVOICE — MODELO',case)
    d.add_paragraph('N.º documento: SIM-INV-001  |  Fecha: [DD/MM/AAAA]')
    t=d.add_table(rows=0, cols=2); t.style='Table Grid'
    for a,b in [('Vendedor / Exportador','EMPRESA DEMO S.A.C. (FICTICIA)'),('Comprador / Importador','CLIENTE DEMO (FICTICIO)'),('Dirección del vendedor','[Completar]'),('Dirección del comprador','[Completar]'),('Moneda','[USD / otra]'),('Incoterm y lugar convenido','[Definir según contrato]'),('Cantidad y unidad',f"{case.get('cantidad',1)} pares (verificar unidad)"),('Descripción detallada',case.get('producto','[Completar]')),('Marca / modelo','[Completar]'),('Precio unitario','[Completar]'),('Valor total','[Completar]'),('País de origen declarado','[Verificar; no equivale a origen preferencial]'),('Condiciones de pago','[Completar]')]:
        row=t.add_row().cells; row[0].text=str(a); row[1].text=str(b)
    d.add_paragraph('Validar la información del documento con el proveedor y el procedimiento aduanero aplicable. Este ejemplo no tiene valor tributario por sí mismo.')
    b=BytesIO(); d.save(b); return b.getvalue()

def packing_list(case):
    d=_doc('LISTA DE EMPAQUE / PACKING LIST — MODELO',case)
    d.add_paragraph('Referencia comercial: [Factura / contrato]     Fecha: [DD/MM/AAAA]')
    t=d.add_table(rows=0, cols=6); t.style='Table Grid'
    for values in [('Bulto','Descripción','Cantidad','Peso neto kg','Peso bruto kg','Medidas cm'),('1',case.get('producto','[Mercancía]'),str(case.get('cantidad',1)),'[ ]','[ ]','[L × A × H]')]:
        row=t.add_row().cells
        for i,v in enumerate(values): row[i].text=str(v)
    d.add_paragraph('Total bultos: [ ]   |   Peso neto total: [ ] kg   |   Peso bruto total: [ ] kg')
    d.add_paragraph('Incluir marcas de embalaje, numeración, diferencias por talla/modelo y otros datos que requiera la operación concreta.')
    b=BytesIO(); d.save(b); return b.getvalue()

def checklist_pdf(case, items, done, sources):
    b=BytesIO(); c=canvas.Canvas(b,pagesize=A4); w,h=A4; y=h-55
    def block(text, fontsize=10, bold=False):
        nonlocal y
        c.setFont('Helvetica-Bold' if bold else 'Helvetica',fontsize)
        for line in simpleSplit(text,'Helvetica',fontsize,w-100):
            if y<70: c.showPage(); y=h-55
            c.drawString(48,y,line); y-=17
    block('CALZADUANA IA - CHECKLIST EDUCATIVO',15,True); y-=12
    block('CASO SIMULADO - NO REEMPLAZA CONTROL NI DECLARACION ADUANERA',9,True)
    block('Operacion: '+case.get('operacion',''));block('Mercancia: '+case.get('producto',''));block('Pais: '+case.get('pais',''));y-=18
    for item in items: block(('[X] ' if item in done else '[  ] ')+item)
    y-=15; block('FUENTES OFICIALES REFERENCIALES:',10,True)
    for source in sources:
        block(source['numero']+' - '+source['titulo']);block(source['url'],8)
    y-=10; block('Verificar vigencia normativa, regimen, subpartida y entidades competentes antes de operar.',9)
    c.save();return b.getvalue()
