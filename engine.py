"""Motor de orientación prudente: corpus cerrado, citas trazables y sin clasificación vinculante."""
import json, re
from pathlib import Path

BASE = Path(__file__).parent
NORMS = json.loads((BASE/'normas.json').read_text(encoding='utf-8'))
BY_ID = {n['id']: n for n in NORMS}
CUT_OFF = '11/11/2026 (revisión documental de referencia)'

def refs(ids):
    return [BY_ID[i] for i in dict.fromkeys(ids) if i in BY_ID]

def collect(context, query=''):
    op=context.get('operacion','IMPORTAR')
    q=(query+' '+context.get('producto','')).lower()
    ids=['LGA','IMP' if op=='IMPORTAR' else 'EXP']
    if op=='IMPORTAR' and any(x in q for x in ('zapato','zapatilla','calzado','bota','sandalia')): ids.append('CAL')
    if any(x in q for x in ('restric','permiso','autoriz','prohib')): ids.append('RES')
    if any(x in q for x in ('arancel','subpartida','clasific','tribut','impuesto')): ids+=['CLA','ARAN']
    if any(x in q for x in ('origen','certificado','tratado','preferen','tlc')): ids.append('ORI')
    return refs(ids)

def missing(context):
    fields=[]
    for key, label in [('producto','descripción de la mercancía'),('pais','país de origen (importación) o destino (exportación)'),('material','material de la parte superior'),('suela','material de la suela/planta'),('estado','condición nueva o usada')]:
        if not str(context.get(key,'')).strip(): fields.append(label)
    return fields

def guidance(context, question=''):
    op=context.get('operacion','IMPORTAR'); prod=context.get('producto','mercancía no especificada').strip() or 'mercancía no especificada'
    country=context.get('pais','país no definido').strip() or 'país no definido'
    used=(context.get('estado','')=='Usado')
    norm_ids=['IMP' if op=='IMPORTAR' else 'EXP','LGA']; statements=[]
    if op=='IMPORTAR':
        statements.append(('**Régimen por verificar.** Si la mercancía se destina a su consumo en Perú, evalúa el régimen de importación para el consumo. La declaración y el despacho se gestionan conforme al procedimiento vigente.', ['IMP']))
        statements.append(('**Documentación preliminar.** Revisa factura o documento equivalente/contrato, documento de transporte y los demás sustentos que correspondan al despacho. No todos los documentos aplican idénticamente a cada caso.', ['IMP']))
    else:
        statements.append(('**Régimen por verificar.** Si la mercancía nacional o nacionalizada sale para consumo definitivo en el exterior, evalúa exportación definitiva. Este régimen no está afecto a tributo alguno en Perú; ello no determina impuestos en el destino.', ['EXP']))
        statements.append(('**Documentación preliminar.** Prepara información comercial, de mercancía y transporte, y confirma con el despachador el soporte exigido para la operación concreta.', ['EXP']))
    footwear=bool(re.search(r'calzad|zapatill|zapato|sandalia|bota|botín',prod.lower()))
    if op=='IMPORTAR' and footwear:
        norm_ids.append('CAL')
        statements.append(('**Descripción técnica del calzado.** Si corresponde al ámbito del instructivo DESPA-IT.01.23 (partidas 6401 a 6405 y regímenes indicados), verifica denominación, marca, modelo, parte superior, planta, forro, usuario, sistema de tallas, talla y construcción en la DAM.', ['CAL']))
    if used and footwear and op=='IMPORTAR':
        statements.append(('**ALERTA ALTA — calzado usado.** No continúes con el despacho hasta verificar las prohibiciones aplicables al ingreso de ropa y calzado usado. Este prototipo no emite autorizaciones ni habilita la operación.', ['USADO']))
        norm_ids.append('USADO')
    norm_ids.extend(['CLA','RES','ORI']);
    statements.extend([
      ('**Subpartida y tributos.** La subpartida nacional requiere características técnicas completas y clasificación adecuada; no se asigna un código definitivo ni se calculan tributos con datos incompletos. Consulta tratamiento arancelario cuando exista clasificación sustentada.', ['CLA','ARAN']),
      ('**Restricciones.** No se presume que el producto sea restringido. Verifica la normativa de la entidad sectorial competente según el tipo exacto de mercancía.', ['RES']),
      ('**Origen y preferencias.** No se presume acceso a un beneficio por el solo país de procedencia/destino: primero debe comprobarse el acuerdo, reglas de origen y prueba admisible.', ['ORI'])
    ])
    unanswered=missing(context)
    if unanswered: statements.append(('**Faltan datos para una evaluación específica:** '+', '.join(unanswered)+'. La orientación es preliminar y requiere verificación.', []))
    if question:
        q=question.lower()
        if any(x in q for x in ('packing','empaque','factura','document')):
            statements.append(('**Modelos comerciales.** Puedes descargar una factura comercial o lista de empaque con la información simulada del caso. Son ejemplos educativos; no reemplazan una factura emitida, una DAM ni un certificado oficial.', ['IMP' if op=='IMPORTAR' else 'EXP']))
    cited={x for _, arr in statements for x in arr}
    return {'titulo':f'Orientación preliminar sobre {"importación" if op=="IMPORTAR" else "exportación"} de {prod} — {country}', 'statements':statements,'sources':refs([i for i in norm_ids if i in cited]),'missing':unanswered}

def try_llm(question, context, sources, api_key):
    """Optional: language model constrained to cited records; never replaces rule-based answer."""
    if not api_key or not question.strip(): return None
    try:
        from openai import OpenAI
        allowed=[{'id':x['id'],'titulo':x['titulo'],'parrafo':x['parrafo'],'extracto':x['extracto']} for x in sources]
        client=OpenAI(api_key=api_key, timeout=14, max_retries=0)
        response=client.chat.completions.create(model='gpt-4o-mini',messages=[
          {'role':'system','content':'Eres un orientador educativo sobre aduanas peruanas. Responde SOLO sobre hechos sustentados en EXTRACTOS de FUENTES. No inventes requisitos, artículos, datos, subpartidas, impuestos, enlaces ni pruebas de origen. Si los extractos no bastan, di «requiere verificación» y pregunta lo que falta. Responde máximo 150 palabras. Cita cada afirmación jurídica con IDs exactos entre corchetes p. ej. [IMP]. No puedes ofrecer clasificaciones vinculantes. No sustituyes a SUNAT.'},
          {'role':'user','content':json.dumps({'operacion':context,'consulta':question,'fuentes':allowed},ensure_ascii=False)}
        ],temperature=0,max_tokens=330)
        answer=response.choices[0].message.content or ''
        markers=set(re.findall(r'\[([A-Z]+)\]',answer))
        allowed_ids={x['id'] for x in sources}
        if not markers or not markers.issubset(allowed_ids): return None
        # Each paragraph with a normative claim needs a citation; output is always a supplement, never the authority.
        return answer
    except Exception:
        return None
