import os, json, re, html
from datetime import datetime
from pathlib import Path
import streamlit as st
from engine import NORMS, BY_ID, CUT_OFF, refs, guidance, collect, missing, try_llm
from documents import commercial_invoice, packing_list, checklist_pdf

st.set_page_config(page_title='CALZADUANA IA | Orientación aduanera MYPE',page_icon='👟',layout='wide',initial_sidebar_state='collapsed')
st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"],.stApp {font-family: 'DM Sans', sans-serif;}
.stApp {background: #f5f7fb;color:#14253c;}
.block-container {max-width:1120px;padding-top:1.55rem;padding-bottom:3rem;}
.hero {background:linear-gradient(120deg,#101e39 5%,#14304b 60%,#126b6c 110%);border-radius:22px;padding:32px 36px;color:white;margin-bottom:22px;box-shadow:0 14px 25px rgba(22,50,80,.12)}
.hero h1 {font-size:clamp(28px,5vw,44px);line-height:1.1;color:#fff;margin:6px 0 9px;font-weight:800}
.hero p {color:#d9e8ed;max-width:730px;margin:0;font-size:16px}
.kicker {color:#8de3cf;font-size:12px;font-weight:800;letter-spacing:.14em}
.stat {display:inline-block;background:#ffffff1a;color:#dff5f1;padding:7px 12px;border-radius:30px;font-size:12px;margin:15px 8px 0 0}
[data-testid="stVerticalBlockBorderWrapper"] {background:white;border-radius:16px;}
h1,h2,h3 {color:#142844;}
.stButton button[kind="primary"],.stDownloadButton button[kind="primary"] {background:#12766f;border:0;border-radius:12px;font-weight:750;}
.stButton button,.stDownloadButton button{border-radius:11px;}
a {color:#08776e}
.footer {font-size:12px;color:#667b8c;text-align:center;padding:22px 0}
.note {border-left:4px solid #eaa946;background:#fffbf2;padding:12px 15px;border-radius:9px;}
@media (max-width:640px){.hero{padding:24px 19px;border-radius:16px}.block-container{padding:1rem .75rem 3rem}.hero p{font-size:14px}}
</style>''',unsafe_allow_html=True)

st.markdown('''<div class="hero"><div class="kicker">HACKATHON SUNAT 2026 · EJE 4</div><h1>👟 CALZADUANA IA</h1><p>Orientación normativa y documentación de importaciones y exportaciones para MYPES del sector calzado del Perú. Respuestas trazables con enlaces oficiales y modelos comerciales educativos.</p><span class="stat">🌐 Web adaptable a celulares</span><span class="stat">📚 Fuentes SUNAT y MINCETUR</span><span class="stat">🔒 Casos simulados</span></div>''',unsafe_allow_html=True)

if 'ctx' not in st.session_state: st.session_state.ctx={}
if 'messages' not in st.session_state: st.session_state.messages=[]
if 'done' not in st.session_state: st.session_state.done={}
if 'quiz' not in st.session_state: st.session_state.quiz=False

with st.sidebar:
    st.header('⚖️ Transparencia normativa')
    st.info('Prototipo educativo. No está afiliado a SUNAT ni emite resoluciones, DAM, autorizaciones ni clasificaciones vinculantes.')
    st.write('**Fecha de corte documental:** '+CUT_OFF)
    st.write('Los enlaces se pueden abrir desde la app. Su disponibilidad y vigencia deben revisarse antes de operaciones reales.')
    st.write('**Privacidad:** no ingresar RUC, claves SOL, DNI, datos de terceros ni información confidencial. Los casos se gestionan temporalmente durante la sesión.')
    st.caption('Si se configura un servicio externo de IA, las consultas enviadas a ese servicio estarán sujetas a sus condiciones de privacidad; emplea únicamente datos simulados.')

workflow, sources_tab, about = st.tabs(['🧭 Mi operación y consultas','📚 Biblioteca normativa','ℹ️ Proyecto y seguridad'])
with workflow:
    st.subheader('1. Describe tu operación')
    a,b=st.columns([1,1])
    with a:
        operation=st.radio('¿Qué deseas hacer?',['IMPORTAR','EXPORTAR'],horizontal=True)
        product=st.text_input('Mercancía',value=st.session_state.ctx.get('producto','Zapatillas deportivas nuevas'),placeholder='Ej.: zapatillas de material textil')
        material=st.selectbox('Material de la parte superior',['','Cuero natural','Textil','Sintético / plástico','Caucho','Mixto / por verificar'],index=0)
        status=st.selectbox('Condición de la mercancía',['','Nuevo','Usado'])
    with b:
        country=st.text_input('País de origen (importar) o destino (exportar)',value=st.session_state.ctx.get('pais','China' if operation=='IMPORTAR' else 'Chile'))
        quantity=st.number_input('Cantidad de pares (ejemplo)',min_value=1,max_value=1000000,value=200,step=1)
        sole=st.selectbox('Material de la planta / suela',['','Caucho','Plástico','Cuero','Textil','Mixto / por verificar'])
        shipment=st.selectbox('Transporte estimado',['Por definir','Marítimo','Aéreo','Terrestre','Postal / entrega rápida'])
    context={'operacion':operation,'producto':product,'pais':country,'cantidad':quantity,'material':material,'suela':sole,'estado':status,'transporte':shipment}
    st.session_state.ctx=context
    gaps=missing(context)
    if gaps: st.warning('Para orientación más específica falta precisar: '+', '.join(gaps)+'.')
    if st.button('🔎 Generar orientación normativa del caso',type='primary',use_container_width=True):
        st.session_state.result=guidance(context)
        st.session_state.messages=[]
    if 'result' in st.session_state:
        r=st.session_state.result
        st.subheader('2. Orientación sustentada')
        st.caption(r['titulo'])
        for text,ids in r['statements']:
            st.markdown('• '+text + (('  **Fuentes:** '+', '.join(f'[{x}]({BY_ID[x]["url"]})' for x in ids)) if ids else ''))
        st.info('La orientación es preventiva. No sustituye al despachador de aduana, la autoridad competente o los documentos emitidos oficialmente.')
    st.divider()
    st.subheader('3. Pregúntale al orientador')
    st.caption('Funciona sin API con un motor de reglas sustentado en la biblioteca. Si el administrador configura OPENAI_API_KEY, añade una síntesis generativa complementaria basada únicamente en los extractos seleccionados.')
    suggestions=['¿Qué documentos debo preparar?','¿Cómo sé si es mercancía restringida?','¿Qué datos necesita la descripción del calzado?','¿Puedo obtener una preferencia arancelaria?']
    selected=st.selectbox('Consulta sugerida (opcional)',['Escribir mi propia pregunta']+suggestions)
    own=st.text_area('Escribe tu pregunta',value='' if selected=='Escribir mi propia pregunta' else selected,placeholder='Ej.: Quiero importar zapatillas de tela desde China; ¿qué documentos necesito?',height=90)
    if st.button('Enviar consulta',type='primary',disabled=not own.strip(),use_container_width=True):
        selection=collect(context,own)
        g=guidance(context,own)
        key=os.getenv('OPENAI_API_KEY','')
        try: key=key or st.secrets.get('OPENAI_API_KEY','')
        except Exception: pass
        generated=try_llm(own,context,selection,key)
        st.session_state.messages.append({'question':own,'answer':g,'ai':generated,'sources':selection})
    for i,m in enumerate(reversed(st.session_state.messages)):
        with st.chat_message('user'):
            st.write(m['question'])
        with st.chat_message('assistant'):
            if m['ai']:
                st.markdown('**Síntesis generativa (revisar la fuente):**')
                st.write(m['ai'])
                st.caption('Identificadores de cita incluidos: solo hacen referencia a los enlaces visibles más abajo.')
            st.markdown('**Orientación verificada del motor de reglas:**')
            for statement, ids in m['answer']['statements']:
                st.markdown('• '+statement+('  **Referencias:** '+', '.join(f'[{k}]({BY_ID[k]["url"]})' for k in ids) if ids else ''))
            with st.expander('📖 Fuentes citadas y enlaces oficiales',expanded=True):
                for n in m['sources']:
                    st.markdown(f'**[{n["id"]}] {n["numero"]}** — {n["titulo"]}. {n["parrafo"]}. [Consultar fuente oficial]({n["url"]})')
    st.divider()
    st.subheader('4. Modelos comerciales y documentos oficiales')
    col1,col2=st.columns(2)
    with col1:
        st.download_button('⬇️ Modelo factura comercial (Word)',commercial_invoice(context),file_name='CALZADUANA_Factura_Comercial_EJEMPLO.docx',mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document',use_container_width=True)
    with col2:
        st.download_button('⬇️ Modelo Packing List (Word)',packing_list(context),file_name='CALZADUANA_Packing_List_EJEMPLO.docx',mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document',use_container_width=True)
    st.caption('Estos archivos son modelos referenciales con datos ficticios. DAM, certificados de origen y documentos de transporte oficiales deben gestionarse por los canales y emisores correspondientes.')
    with st.expander('🏛️ ¿Cómo tramitar documentos oficiales?'):
        proc = BY_ID['IMP' if operation == 'IMPORTAR' else 'EXP']
        st.markdown(
            f'- **Declaración aduanera:** consulta el procedimiento [{proc["numero"]}]({proc["url"]}). La tramitación oficial corresponde a los sujetos y canales autorizados.\n'
            f'- **Prueba de origen:** comprueba el acuerdo y sistema aplicable en [MINCETUR]({BY_ID["ORI"]["url"]}).\n'
            f'- **Autorizaciones sectoriales:** verifica si corresponden en [SUNAT]({BY_ID["RES"]["url"]}).\n'
            f'- **Clasificación:** consulta la [orientación SUNAT]({BY_ID["CLA"]["url"]}).'
        )
    st.divider()
    st.subheader('5. Lista de verificación personalizada')
    checks=[
      'Confirmar régimen aduanero y modalidad aplicable',
      'Completar características técnicas: materiales, marca, modelo y estado',
      'Revisar clasificación arancelaria con información técnica suficiente',
      'Revisar factura / contrato comercial pertinente',
      'Revisar documento de transporte y condiciones de entrega',
      'Verificar restricciones y autorizaciones sectoriales cuando corresponda',
      'Verificar acuerdo comercial y prueba de origen, solo si se pretende preferencia',
      'Confirmar documentación de despacho con operador/autoridad competente'
    ]
    if operation=='IMPORTAR' and any(x in product.lower() for x in ['calzado','zapatilla','zapato','bota','sandalia']):
        checks.insert(2,'Verificar campos de descripción mínima DESPA-IT.01.23 si aplica')
    done=[]
    for j,item in enumerate(checks):
        if st.checkbox(item,key=f'check_{operation}_{j}') : done.append(item)
    st.progress(len(done)/len(checks),text=f'{len(done)} de {len(checks)} actividades revisadas (autodeclaradas; no verificadas por SUNAT)')
    sources=refs(['LGA','IMP' if operation=='IMPORTAR' else 'EXP','CAL','CLA','RES','ORI'])
    st.download_button('⬇️ Descargar checklist con fuentes (PDF)',checklist_pdf(context,checks,done,sources),file_name='CALZADUANA_Checklist_Educativo.pdf',mime='application/pdf')
    st.divider()
    st.subheader('6. Comprobación de aprendizaje')
    questions=[('¿La IA puede asignar una subpartida nacional definitiva?', ['Sí, si la mercancía tiene marca','No; se requiere clasificación sustentada y, si corresponde, pronunciamiento oficial'],1),
      ('¿Un documento comercial simulado equivale a una DAM oficial?', ['Sí','No'],1),
      ('¿Se puede asegurar una preferencia arancelaria solo por el país?', ['Sí','No; deben verificarse acuerdo, origen y prueba admisible'],1)]
    with st.form('quizform'):
        answers=[]
        for i,(question,opts,correct) in enumerate(questions):
            answers.append(st.radio(question,opts,index=None,key=f'quiz_{i}'))
        submitted=st.form_submit_button('Evaluar comprensión',type='primary')
        if submitted:
            if any(v is None for v in answers): st.warning('Responde las tres preguntas.')
            else:
                result=sum(answer==opts[correct] for answer,(_,opts,correct) in zip(answers,questions))
                st.success(f'Resultado: {result}/3 respuestas correctas. Registro demostrativo, no certificación de competencia.')
                st.caption('Las preguntas refuerzan consulta preventiva, integridad documental y verificación del origen.')

with sources_tab:
    st.subheader('Biblioteca de normas y orientaciones oficiales')
    st.write('Catálogo curado de fuentes con identificadores, entidad emisora, referencia, estado de revisión y enlace oficial. **La existencia del enlace no garantiza por sí sola que la disposición siga vigente.**')
    for n in NORMS:
        with st.expander(f'[{n["id"]}] {n["numero"]} · {n["titulo"]}'):
            st.markdown(f'**Emisor:** {n["emisor"]}  |  **Tipo:** {n["tipo"]}  |  **Versión:** {n["version"]}  |  **Fecha registrada:** {n["fecha"]}')
            st.markdown(f'**Ubicación específica:** {n["parrafo"]}')
            st.write(n['extracto'])
            st.warning('Estado: '+n['estado_revision'])
            st.link_button('Abrir documento oficial',n['url'])
    st.download_button('⬇️ Exportar catálogo de normas (JSON)',json.dumps(NORMS,ensure_ascii=False,indent=2).encode('utf-8'),file_name='CALZADUANA_catalogo_normativo.json',mime='application/json')

with about:
    st.subheader('Sobre CALZADUANA IA')
    st.write('Propuesta académica del Hackathon SUNAT 2026 — Eje 4: Asistencia al contribuyente y usuario aduanero. Su público objetivo son las MYPES del sector calzado del Perú, con especial interés en La Libertad.')
    st.markdown('''**Alcance de esta versión**
- Operación en línea una vez desplegada; interfaz adaptable a celular, tablet y laptop.
- Orientación estructurada respaldada por una base local de fragmentos previamente seleccionados.
- Dos modelos comerciales editables y checklist PDF; no genera actos administrativos oficiales.
- IA generativa opcional con llave de API del administrador, basada en los extractos seleccionados. Sin llave, el sistema sigue funcionando como orientador de reglas, **no como chatbot generativo**.
- No realiza consultas en tiempo real a SUNAT, ni verifica automáticamente la vigencia de las normas; el equipo debe revisarlas antes del concurso y ante cambios normativos.
- No determina tributos, restricciones, beneficios ni clasificación aduanera de forma definitiva.''')
    st.markdown('**Reglas de seguridad:** R1 no clasificar vinculantemente; R2 validar régimen; R3 identificar descripción del calzado cuando aplique; R4 no asumir restricciones; R5 verificar acuerdos y reglas de origen; R6 marcar dudas como «requiere verificación».')
    st.caption('Código y documentación diseñados para uso educativo. Prohibido ingresar credenciales SOL o documentos privados de terceros.')

st.markdown('<div class="footer">CALZADUANA IA · Prototipo académico independiente · Fecha de corte: 11/11/2026 · Verifica los enlaces y la normativa antes de cualquier operación real.</div>',unsafe_allow_html=True)
