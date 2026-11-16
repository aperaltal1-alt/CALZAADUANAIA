"""CALZADUANA IA: prototipo educativo para MYPES del calzado de Peru.
No emite actos de SUNAT ni clasificaciones vinculantes.
"""
import io
import json
import os
import re
from datetime import date
from pathlib import Path

import streamlit as st
from docx import Document

st.set_page_config(page_title="CALZADUANA IA", page_icon="👟", layout="wide")

BASE = Path(__file__).resolve().parent
FUENTES_BASE = [
    {"id": "LGA", "numero": "D. Leg. 1053", "titulo": "Ley General de Aduanas", "url": "https://www.gob.pe/institucion/mef/normas-legales/226850-1053", "tags": ["general", "importar", "exportar"]},
    {"id": "IMP", "numero": "DESPA-PG.01", "titulo": "Importación para el consumo", "url": "https://www.sunat.gob.pe/legislacion/procedim/despacho/importacion/importac/procGeneral/despa-pg.01.htm", "tags": ["importar", "documentos", "factura"]},
    {"id": "EXP", "numero": "DESPA-PG.02", "titulo": "Exportación definitiva", "url": "https://www.sunat.gob.pe/legislacion/procedim/despacho/exportacion/exportac/procGeneral/despa-pg.02.htm", "tags": ["exportar", "documentos", "factura"]},
    {"id": "CAL", "numero": "DESPA-IT.01.23", "titulo": "Descripciones mínimas de calzado", "url": "https://www.sunat.gob.pe/legislacion/procedim/despacho/importacion/importac/instructivos/despa-it.01.23.htm", "tags": ["calzado", "material", "descripcion", "importar"]},
]


def cargar_fuentes():
    ruta = BASE / "normas.json"
    if ruta.exists():
        try:
            datos = json.loads(ruta.read_text(encoding="utf-8"))
            if isinstance(datos, list) and datos:
                return [f for f in datos if isinstance(f, dict) and f.get("url") and f.get("titulo")]
        except (ValueError, OSError):
            pass
    return FUENTES_BASE

FUENTES = cargar_fuentes()


def obtener_fuente(codigo):
    return next((f for f in FUENTES if f.get("id") == codigo), None)


def enlaces(codigos):
    vistos = set()
    for codigo in codigos:
        f = obtener_fuente(codigo)
        if not f or codigo in vistos:
            continue
        vistos.add(codigo)
        st.markdown(f"- **{f.get('numero', 'Norma')} — {f['titulo']}**: [Consultar fuente oficial]({f['url']})")
        st.caption(f"Referencia: {f.get('procedimiento', 'Norma o procedimiento')} · {f.get('parrafo', 'Consultar apartados aplicables')} · Revisión humana pendiente antes de operar")


def documento_word(nombre, datos):
    doc = Document()
    doc.add_heading("CALZADUANA IA | EJEMPLO DIDÁCTICO", 0)
    doc.add_paragraph("MODELO REFERENCIAL. No constituye documento oficial, declaración aduanera ni documento emitido por SUNAT.")
    doc.add_heading(nombre, level=1)
    for etiqueta, valor in datos.items():
        doc.add_paragraph(f"{etiqueta}: {valor or '[COMPLETAR]'}")
    doc.add_paragraph("Verifique los datos reales, condiciones pactadas, requisitos del comprador y normativa aplicable antes de utilizar este modelo.")
    archivo = io.BytesIO()
    doc.save(archivo)
    return archivo.getvalue()


def orientar(operacion, producto, pais, consulta):
    texto = (consulta or "").lower()
    puntos = []
    ids = ["LGA"]
    if operacion == "IMPORTAR":
        ids.append("IMP")
        puntos.append("**Régimen:** si la operación corresponde a importación para el consumo, revise DESPA-PG.01; otras modalidades pueden tener requisitos distintos.")
    else:
        ids.append("EXP")
        puntos.append("**Régimen:** si se trata de exportación definitiva, revise DESPA-PG.02; la aplicación no sustituye el despacho formal.")
    puntos.append("**Documentos:** identifique factura o documento comercial pertinente, documento de transporte y demás documentos que correspondan al régimen y mercancía. La exigencia exacta depende del caso.")
    if "calzad" in producto.lower() or any(p in producto.lower() for p in ["zapato", "zapatilla", "bota", "sandalia"]):
        if operacion == "IMPORTAR":
            ids.append("CAL")
            puntos.append("**Calzado:** revise si aplica el instructivo DESPA-IT.01.23 y complete las descripciones mínimas exigidas según el tipo de mercancía.")
        else:
            puntos.append("**Calzado:** describa claramente material, modelo, uso y composición; verifique las exigencias del país de destino.")
    if any(w in texto for w in ["arancel", "tribut", "igv", "impuesto", "subpartida", "clasific"]):
        puntos.append("**Tributos y clasificación:** no es posible asignar una subpartida nacional o calcular tributos definitivos sin características técnicas, valor y condiciones de operación verificadas.")
    if any(w in texto for w in ["restric", "permiso", "autoriza", "prohib"]):
        puntos.append("**Restricciones:** no presuma que todo producto de calzado es restringido. Debe determinarse si existe una autorización sectorial exigible para esa mercancía concreta.")
    if any(w in texto for w in ["origen", "tlc", "preferencia"]):
        puntos.append("**Origen preferencial:** una preferencia arancelaria requiere verificar acuerdo aplicable, reglas de origen y prueba válida; no se presume solo por el país indicado.")
    puntos.append("**Antes de presentar documentos:** confirme el procedimiento vigente, la clasificación y las condiciones concretas con SUNAT o el especialista competente.")
    return puntos, ids


st.markdown("""<style>
.block-container{max-width:1100px;padding-top:1.3rem}
[data-testid="stAppViewContainer"]{background:#f6f8fb}
.hero{background:linear-gradient(115deg,#132e51,#0b716d);border-radius:18px;padding:24px;color:white}
.hero h1{color:white;margin:0}.hero p{color:#def4f2;margin:6px 0 0}
</style>""", unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>👟 CALZADUANA IA</h1><p>Orientación aduanera y documentación para las MYPES del calzado del Perú</p></div>', unsafe_allow_html=True)
st.caption(f"Prototipo educativo • Consulta de fuentes oficiales con revisión humana • Fecha de uso: {date.today().strftime('%d/%m/%Y')} • No reemplaza a SUNAT")

consulta_tab, docs_tab, fuentes_tab, quiz_tab = st.tabs(["🧭 Orientación", "📄 Modelos documentarios", "⚖️ Fuentes oficiales", "✅ Comprobación"])

with consulta_tab:
    st.subheader("Cuéntanos qué deseas hacer")
    izquierda, derecha = st.columns(2)
    with izquierda:
        operacion = st.radio("Tipo de operación", ["IMPORTAR", "EXPORTAR"], horizontal=True)
        producto = st.text_input("Mercancía", value="Zapatillas de cuero")
        pais = st.text_input("País de origen o destino", value="China" if operacion == "IMPORTAR" else "Chile")
    with derecha:
        material = st.text_input("Material principal (si lo conoce)", placeholder="Ejemplo: cuero, textil, sintético")
        cantidad = st.number_input("Cantidad de pares", min_value=1, value=100)
        valor = st.number_input("Valor comercial aproximado (USD)", min_value=0.0, value=1500.0, step=50.0)
    pregunta = st.text_area("¿Qué necesitas saber?", placeholder="Ej.: ¿Qué documentos debo preparar y qué normas debo consultar?")
    consultar = st.button("Consultar orientación", type="primary", use_container_width=True)
    if consultar:
        datos = {"operacion": operacion, "producto": producto, "pais": pais, "material": material, "cantidad": cantidad, "valor": valor, "pregunta": pregunta}
        st.session_state["caso"] = datos
        st.session_state["resultado"] = orientar(operacion, producto, pais, pregunta)
    if "resultado" in st.session_state:
        puntos, ids = st.session_state["resultado"]
        st.success("Orientación generada a partir de reglas educativas y referencias documentales. No es una resolución de SUNAT.")
        for punto in puntos:
            st.markdown("- " + punto)
        st.markdown("#### Fuentes asociadas a la orientación")
        enlaces(ids)
        st.warning("La existencia del enlace no acredita por sí sola la vigencia ni aplicabilidad exacta de cada numeral. Verifique texto actualizado y modificaciones antes de operar.")
    else:
        st.info("Completa los datos y pulsa «Consultar orientación». No es necesario ingresar RUC ni datos personales.")

with docs_tab:
    st.subheader("Modelos comerciales descargables")
    st.write("Estos documentos son ejemplos **referenciales**. No generan DAM, certificado oficial ni factura electrónica válida.")
    caso = st.session_state.get("caso", {"operacion": "EXPORTAR", "producto": "Zapatos de cuero", "pais": "Chile", "material": "Cuero", "cantidad": 100, "valor": 2500})
    datos_base = {
        "Operación": caso.get("operacion"), "Producto": caso.get("producto"),
        "País asociado": caso.get("pais"), "Material": caso.get("material"),
        "Cantidad de pares": str(caso.get("cantidad")), "Valor comercial USD": str(caso.get("valor")),
    }
    col1, col2 = st.columns(2)
    with col1:
        factura = documento_word("FACTURA COMERCIAL INTERNACIONAL - MODELO", {**datos_base, "Número": "SIM-001", "Exportador": "[RAZÓN SOCIAL FICTICIA]", "Comprador": "[COMPRADOR FICTICIO]", "Incoterm y lugar": "[COMPLETAR]", "Fecha": "[COMPLETAR]"})
        st.download_button("⬇️ Descargar factura comercial (Word)", factura, "factura_comercial_modelo.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
    with col2:
        packing = documento_word("LISTA DE EMPAQUE / PACKING LIST - MODELO", {**datos_base, "Cantidad de bultos": "[COMPLETAR]", "Peso neto/bruto": "[COMPLETAR]", "Dimensiones": "[COMPLETAR]", "Marcas de bultos": "[COMPLETAR]"})
        st.download_button("⬇️ Descargar packing list (Word)", packing, "packing_list_modelo.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
    st.markdown("#### Checklist inicial")
    items = ["Identificar el régimen aduanero", "Describir técnicamente el calzado", "Verificar documentos comerciales y transporte", "Consultar posibles restricciones", "Verificar clasificación y tributos aplicables", "Revisar fuentes oficiales actualizadas", "Solicitar validación humana antes de presentar"]
    for i, item in enumerate(items):
        st.checkbox(item, key=f"check_{i}")
    lista = "CALZADUANA IA - CHECKLIST REFERENCIAL\n\n" + "\n".join(("[X] " if st.session_state.get(f"check_{i}") else "[ ] ") + item for i, item in enumerate(items))
    st.download_button("⬇️ Descargar checklist (TXT)", lista.encode("utf-8"), "checklist_aduanero.txt", "text/plain")

with fuentes_tab:
    st.subheader("Catálogo de referencias normativas")
    st.write("Consulta los enlaces originales y verifica la versión vigente antes de preparar una operación real.")
    for f in FUENTES:
        with st.expander(f"{f.get('numero', 'Referencia')} — {f['titulo']}"):
            st.write(f.get("extracto", "Referencia para consulta y contraste con el texto oficial."))
            st.markdown(f"[🔗 Abrir documento oficial]({f['url']})")
            st.caption(f"Emisor: {f.get('emisor', 'Entidad oficial')} | Apartado: {f.get('parrafo', 'Por verificar')} | Estado: {f.get('estado_revision', 'Revisión humana pendiente')}")

with quiz_tab:
    st.subheader("Comprueba lo aprendido")
    a = st.radio("1. ¿Puede un prototipo emitir una clasificación arancelaria vinculante?", ["Sí", "No"], index=None)
    b = st.radio("2. ¿Los modelos descargables reemplazan documentos oficiales emitidos por SUNAT?", ["Sí", "No"], index=None)
    c = st.radio("3. ¿Se debe comprobar la fuente y su vigencia antes de efectuar el trámite?", ["Sí", "No"], index=None)
    if st.button("Evaluar respuestas"):
        if None in (a, b, c):
            st.warning("Responde las tres preguntas.")
        else:
            puntaje = (a == "No") + (b == "No") + (c == "Sí")
            st.metric("Respuestas correctas", f"{puntaje}/3")
            st.write("El uso de fuentes oficiales y la validación humana son esenciales para la orientación responsable.")

st.divider()
st.caption("CALZADUANA IA • Hackathon SUNAT 2026 • Eje 4 • Datos simulados • No recopila identificación personal en este prototipo")
