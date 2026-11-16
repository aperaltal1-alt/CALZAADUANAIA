# CALZADUANA IA — Hackathon SUNAT 2026 · Eje 4

Prototipo web educativo para MYPES del sector calzado peruano. Accesible por celular, tablet o computadora **una vez desplegado en un servidor con URL pública**.

## Qué incluye

- Selección de importación/exportación y ficha de mercancía.
- Orientación preventiva basada en corpus cerrado de referencias oficiales; cada requisito jurídico relevante muestra un enlace a la fuente.
- Consultas sobre documentos, restricciones, aranceles, clasificación y origen.
- Modelos comerciales simulados en Word: factura comercial y packing list.
- Checklist PDF y prueba de comprensión de tres preguntas.
- Biblioteca normativa transparente con fecha de corte y estado de revisión.
- IA generativa **opcional** con `OPENAI_API_KEY`: sin clave, trabaja el motor de reglas; no simula disponer de IA generativa.

## Ejecutar localmente para pruebas

1. Instala Python 3.11 o 3.12.
2. `pip install -r requirements.txt`
3. `streamlit run app.py`
4. Abre la URL local indicada. Esto es solo desarrollo: la app requiere despliegue para estar disponible en cualquier dispositivo.

## Publicar en Internet (Streamlit Community Cloud)

1. Crea un repositorio de GitHub con `app.py`, `engine.py`, `documents.py`, `normas.json`, `requirements.txt`, `.streamlit/config.toml` y este `README.md`.
2. En https://share.streamlit.io/ inicia sesión con GitHub, selecciona **Create app**, el repositorio y la rama, e indica `app.py` como archivo principal.
3. Despliega, copia la dirección HTTPS generada y pruébala en celular (datos móviles) y otra laptop (red distinta).
4. (Opcional) Configura la clave `OPENAI_API_KEY` en **Secrets** de Streamlit Cloud, nunca dentro del código ni del repositorio. El servicio de IA puede tener costo.
5. Antes de presentar, comprueba todos los enlaces normativos y revisa modificatorias. Documenta el responsable y la fecha de verificación.

## Limitaciones

- No está afiliado a SUNAT ni sustituye un despachador o asesor aduanero.
- No clasifica mercancías de forma vinculante, no liquida tributos reales, no emite DAM, certificados ni autorizaciones.
- La biblioteca contiene resúmenes revisados manualmente, no una base actualizada en tiempo real. La fecha de corte es 11/11/2026.
- El motor de IA opcional usa un conjunto acotado de fragmentos y puede equivocarse; se muestra como síntesis adicional. Confirmar siempre con fuentes oficiales.
- Los resultados de aprendizaje y checklist se gestionan como casos simulados dentro de la sesión, no se envían a SUNAT.
- Para usuarios reales, realizar evaluación de privacidad, limitación de tasa, pruebas de seguridad y revisión normativa continua.

## Checklist de pruebas sugerido para el jurado

- Importación de zapatillas nuevas desde China: aparecen referencias a DESPA-PG.01 y DESPA-IT.01.23.
- Exportación de zapatos nuevos a Chile: aparece DESPA-PG.02, sin aplicar indebidamente el instructivo de importación.
- Pregunta sobre preferencias: se exige verificar acuerdo y prueba de origen, sin prometer beneficio.
- Pregunta sobre clasificación: no asigna una subpartida de diez dígitos inventada.
- Descargar y abrir Word y PDF desde Android o iPhone.
- Abrir URL desde red ajena a la del equipo.

## Fuentes

Los enlaces están en `normas.json` y se presentan directamente dentro de la aplicación. Se priorizan SUNAT, MEF y MINCETUR. Toda modificación requiere revisión humana.
