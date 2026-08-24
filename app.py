import streamlit as st
from docxtpl import DocxTemplate
import io
from datetime import datetime

st.set_page_config(layout="wide", page_title="Generador de Informe SCADA - CCM")

# 1. Base de datos de equipos / subestaciones parametrizadas
CATALOGO_ALIMENTADORES = {
    "SER01_PTVES - AL3 (154-3)": {
        "interruptor": "154-3 SER01_PTVES",
        "alimentador_ser": "AL3-154 SER01_PTVES",
        "ser": "SER01_PTVES",
        "alimentador": "AL3",
        "interruptor_num": "154-3",
	"zona":"201,203"
    },

"SER01_PTVES - AL4 (154-4)": {
        "interruptor": "154-4 SER01_PTVES",
        "alimentador_ser": "AL4-154 SER01_PTVES",
        "ser": "SER01_PTVES",
        "alimentador": "AL4",
        "interruptor_num": "154-4",
	"zona":"202,204"
    },

"SER03_PIN - AL1 (154-1)": {
        "interruptor": "154-1 SER03_PIN",
        "alimentador_ser": "AL1-154 SER03_PIN",
        "ser": "SER03_PIN",
        "alimentador": "AL1",
        "interruptor_num": "154-1",
	"zona":"201,203"
    },

"SER03_PIN - AL2 (154-2)": {
        "interruptor": "154-2 SER03_PIN",
        "alimentador_ser": "AL2-154 SER03_PIN",
        "ser": "SER03_PIN",
        "alimentador": "AL2",
        "interruptor_num": "154-2",
	"zona":"202,204"
    },

"SER03_PIN - AL3 (154-3)": {
        "interruptor": "154-3 SER03_PIN",
        "alimentador_ser": "AL3-154 SER03_PIN",
        "ser": "SER03_PIN",
        "alimentador": "AL3",
        "interruptor_num": "154-3",
	"zona":"205"
    },

"SER03_PIN - AL4 (154-4)": {
        "interruptor": "154-4 SER03_PIN",
        "alimentador_ser": "AL4-154 SER03_PIN",
        "ser": "SER03_PIN",
        "alimentador": "AL4",
        "interruptor_num": "154-4",
	"zona":"206"
    },

"SER05_VMA - AL1 (154-1)": {
        "interruptor": "154-1 SER05_VMA",
        "alimentador_ser": "AL1-154 SER05_VMA",
        "ser": "SER05_VMA",
        "alimentador": "AL1",
        "interruptor_num": "154-1",
	"zona":"205"
    },

"SER05_VMA - AL2 (154-2)": {
        "interruptor": "154-2 SER05_VMA",
        "alimentador_ser": "AL2-154 SER05_VMA",
        "ser": "SER05_VMA",
        "alimentador": "AL2",
        "interruptor_num": "154-2",
	"zona":"206"
    },

"SER05_VMA - AL3 (154-3)": {
        "interruptor": "154-3 SER05_VMA",
        "alimentador_ser": "AL3-154 SER05_VMA",
        "ser": "SER05_VMA",
        "alimentador": "AL3",
        "interruptor_num": "154-3",
	"zona":"207"
    },

"SER05_VMA - AL4 (154-4)": {
        "interruptor": "154-4 SER05_VMA",
        "alimentador_ser": "AL4-154 SER05_VMA",
        "ser": "SER05_VMA",
        "alimentador": "AL4",
        "interruptor_num": "154-4",
	"zona":"208"
    },

"SER08_ATO - AL1 (154-1)": {
        "interruptor": "154-1 SER08_ATO",
        "alimentador_ser": "AL1-154 SER08_ATO",
        "ser": "SER08_ATO",
        "alimentador": "AL1",
        "interruptor_num": "154-1",
	"zona":"207"
    },

"SER08_ATO - AL2 (154-2)": {
        "interruptor": "154-2 SER08_ATO",
        "alimentador_ser": "AL2-154 SER08_ATO",
        "ser": "SER08_ATO",
        "alimentador": "AL2",
        "interruptor_num": "154-2",
	"zona":"208"
    },

"SER08_ATO - AL3 (154-3)": {
        "interruptor": "154-3 SER08_ATO",
        "alimentador_ser": "AL3-154 SER08_ATO",
        "ser": "SER08_ATO",
        "alimentador": "AL3",
        "interruptor_num": "154-3",
	"zona":"209"
    },

"SER08_ATO - AL4 (154-4)": {
        "interruptor": "154-4 SER08_ATO",
        "alimentador_ser": "AL4-154 SER08_ATO",
        "ser": "SER08_ATO",
        "alimentador": "AL4",
        "interruptor_num": "154-4",
	"zona":"210"
    },

"SER11_CAB - AL1 (154-1)": {
        "interruptor": "154-1 SER11_CAB",
        "alimentador_ser": "AL1-154 SER11_CAB",
        "ser": "SER11_CAB",
        "alimentador": "AL1",
        "interruptor_num": "154-1",
	"zona":"209"
    },

"SER11_CAB - AL2 (154-2)": {
        "interruptor": "154-2 SER11_CAB",
        "alimentador_ser": "AL2-154 SER11_CAB",
        "ser": "SER11_CAB",
        "alimentador": "AL2",
        "interruptor_num": "154-2",
	"zona":"210"
    },

"SER11_CAB - AL3 (154-3)": {
        "interruptor": "154-3 SER11_CAB",
        "alimentador_ser": "AL3-154 SER11_CAB",
        "ser": "SER11_CAB",
        "alimentador": "AL3",
        "interruptor_num": "154-3",
	"zona":"211"
    },

"SER11_CAB - AL4 (154-4)": {
        "interruptor": "154-4 SER11_CAB",
        "alimentador_ser": "AL4-154 SER11_CAB",
        "ser": "SER11_CAB",
        "alimentador": "AL4",
        "interruptor_num": "154-4",
	"zona":"212"
    },

"SER14_CUL - AL1 (154-1)": {
        "interruptor": "154-1 SER14_CUL",
        "alimentador_ser": "AL1-154 SER14_CUL",
        "ser": "SER14_CUL",
        "alimentador": "AL1",
        "interruptor_num": "154-1",
	"zona":"211"
    },

"SER14_CUL - AL2 (154-2)": {
        "interruptor": "154-2 SER14_CUL",
        "alimentador_ser": "AL2-154 SER14_CUL",
        "ser": "SER14_CUL",
        "alimentador": "AL2",
        "interruptor_num": "154-2",
	"zona":"212"
    },

"SER14_CUL - AL3 (154-3)": {
        "interruptor": "154-3 SER14_CUL",
        "alimentador_ser": "AL3-154 SER14_CUL",
        "ser": "SER14_CUL",
        "alimentador": "AL3",
        "interruptor_num": "154-3",
	"zona":"213"
    },

"SER14_CUL - AL4 (154-4)": {
        "interruptor": "154-4 SER14_CUL",
        "alimentador_ser": "AL4-154 SER14_CUL",
        "ser": "SER14_CUL",
        "alimentador": "AL4",
        "interruptor_num": "154-4",
	"zona":"214"
    },

"SER16_GAM - AL1 (154-1)": {
        "interruptor": "154-1 SER16_GAM",
        "alimentador_ser": "AL1-154 SER16_GAM",
        "ser": "SER16_GAM",
        "alimentador": "AL1",
        "interruptor_num": "154-1",
	"zona":"213"
    },

"SER16_GAM - AL2 (154-2)": {
        "interruptor": "154-2 SER16_GAM",
        "alimentador_ser": "AL2-154 SER16_GAM",
        "ser": "SER16_GAM",
        "alimentador": "AL2",
        "interruptor_num": "154-2",
	"zona":"214"
    },

"SER16_GAM - AL3 (154-3)": {
        "interruptor": "154-3 SER16_GAM",
        "alimentador_ser": "AL3-154 SER16_GAM",
        "ser": "SER16_GAM",
        "alimentador": "AL3",
        "interruptor_num": "154-3",
	"zona":"215"
    },

"SER16_GAM - AL4 (154-4)": {
        "interruptor": "154-4 SER16_GAM",
        "alimentador_ser": "AL4-154 SER16_GAM",
        "ser": "SER16_GAM",
        "alimentador": "AL4",
        "interruptor_num": "154-4",
	"zona":"216"
    },

"SER20_CAA - AL1 (154-1)": {
        "interruptor": "154-1 SER20_CAA",
        "alimentador_ser": "AL1-154 SER20_CAA",
        "ser": "SER20_CAA",
        "alimentador": "AL1",
        "interruptor_num": "154-1",
	"zona":"215"
    },

"SER20_CAA - AL2 (154-2)": {
        "interruptor": "154-2 SER20_CAA",
        "alimentador_ser": "AL2-154 SER20_CAA",
        "ser": "SER20_CAA",
        "alimentador": "AL2",
        "interruptor_num": "154-2",
	"zona":"216"
    },

"SER20_CAA - AL3 (154-3)": {
        "interruptor": "154-3 SER20_CAA",
        "alimentador_ser": "AL3-154 SER20_CAA",
        "ser": "SER20_CAA",
        "alimentador": "AL3",
        "interruptor_num": "154-3",
	"zona":"217"
    },

"SER20_CAA - AL4 (154-4)": {
        "interruptor": "154-4 SER20_CAA",
        "alimentador_ser": "AL4-154 SER20_CAA",
        "ser": "SER20_CAA",
        "alimentador": "AL4",
        "interruptor_num": "154-4",
	"zona":"218"
    },

"SER22_JAR - AL1 (154-1)": {
        "interruptor": "154-1 SER22_JAR",
        "alimentador_ser": "AL1-154 SER22_JAR",
        "ser": "SER22_JAR",
        "alimentador": "AL1",
        "interruptor_num": "154-1",
	"zona":"217"
    },

"SER22_JAR - AL2 (154-2)": {
        "interruptor": "154-2 SER22_JAR",
        "alimentador_ser": "AL2-154 SER22_JAR",
        "ser": "SER22_JAR",
        "alimentador": "AL2",
        "interruptor_num": "154-2",
	"zona":"218"
    },

"SER22_JAR - AL3 (154-3)": {
        "interruptor": "154-3 SER22_JAR",
        "alimentador_ser": "AL3-154 SER22_JAR",
        "ser": "SER22_JAR",
        "alimentador": "AL3",
        "interruptor_num": "154-3",
	"zona":"219"
    },

"SER22_JAR - AL4 (154-4)": {
        "interruptor": "154-4 SER22_JAR",
        "alimentador_ser": "AL4-154 SER22_JAR",
        "ser": "SER22_JAR",
        "alimentador": "AL4",
        "interruptor_num": "154-4",
	"zona":"220"
    },

"SER25_SMA - AL1 (154-1)": {
        "interruptor": "154-1 SER25_SMA",
        "alimentador_ser": "AL1-154 SER25_SMA",
        "ser": "SER25_SMA",
        "alimentador": "AL1",
        "interruptor_num": "154-1",
	"zona":"219"
    },

"SER25_SMA - AL2 (154-2)": {
        "interruptor": "154-2 SER25_SMA",
        "alimentador_ser": "AL2-154 SER25_SMA",
        "ser": "SER25_SMA",
        "alimentador": "AL2",
        "interruptor_num": "154-2",
	"zona":"220"
    },

"SER25_SMA - AL3 (154-1)": {
        "interruptor": "154-3 SER25_SMA",
        "alimentador_ser": "AL3-154 SER25_SMA",
        "ser": "SER25_SMA",
        "alimentador": "AL3",
        "interruptor_num": "154-3",
	"zona":"221-223"
    },

"SER25_SMA - AL4 (154-4)": {
        "interruptor": "154-4 SER25_SMA",
        "alimentador_ser": "AL4-154 SER25_SMA",
        "ser": "SER25_SMA",
        "alimentador": "AL4",
        "interruptor_num": "154-4",
	"zona":"222-224"
    },

"SER27_BAY - AL1 (154-1)": {
        "interruptor": "154-1 SER27_BAY",
        "alimentador_ser": "AL1-154 SER27_BAY",
        "ser": "SER27_BAY",
        "alimentador": "AL1",
        "interruptor_num": "154-1",
	"zona":"221-223"
    },

"SER27_BAY - AL2 (154-2)": {
        "interruptor": "154-2 SER27_BAY",
        "alimentador_ser": "AL2-154 SER27_BAY",
        "ser": "SER27_BAY",
        "alimentador": "AL2",
        "interruptor_num": "154-2",
	"zona":"222-224"
    }


}

st.title("⚡ Generador de Informe de Disparo y Recierre DC")

col_form, col_preview = st.columns([1, 1], gap="medium")


with col_form:
    st.header("📝 Parámetros del Evento")
    
    plantilla_word = st.file_uploader("Cargar plantilla base (.docx)", type=["docx"])
    
    with st.expander("1. Selección de Equipos (Autocompletado)", expanded=True):
        sel_aperturado = st.selectbox("Subestación / Celda Aperturada:", list(CATALOGO_ALIMENTADORES.keys()), index=0)
        sel_vecino = st.selectbox("Subestación / Celda Vecina:", list(CATALOGO_ALIMENTADORES.keys()), index=1)
        
        datos_ap = CATALOGO_ALIMENTADORES[sel_aperturado]
        datos_vec = CATALOGO_ALIMENTADORES[sel_vecino]

    with st.expander("2. Funciones de Protección y ST"):
        f_disp_ini = st.text_input("Función VICOS de apertura:", value="Disparo instantáneo Disparador di/dt")
        f_disp_fin = st.text_input("Función rele Sitras PRO:", value="Disparo Imax")
        
      
        c_st1, c_st2, c_st3 = st.columns(3)
        st_ap = c_st1.text_input("ST Aperturado:", value="1404241")
        st_vec = c_st2.text_input("ST Vecino:", value="1404242")
        st_zn = c_st3.text_input("ST Zona:", value="1404245")
        
        corriente_val = st.text_input("Corriente registrada (A):", value="2450")

    with st.expander("3. Datos de Operación y Sistema"):
        c_op1, c_op2 = st.columns(2)
        fecha_val = c_op1.date_input("Fecha:", value=datetime.today()).strftime("%d/%m/%Y")
        dia_val = c_op2.selectbox("Día:", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])
        
        c_op3, c_op4 = st.columns(2)
        headway = c_op3.text_input("Headway (min):", value="3")
        condicion = c_op4.text_input("Condición Señales:", value="Normal")
        
        c_op5, c_op6 = st.columns(2)
        operacion_val = c_op5.text_input("Horario Operación:", value="Hora Valle")
        # zona_val = c_op6.text_input("Zona Eléctrica:", value="Zona 3")

    with st.expander("4. Cronología y Horas (HH:MM:SS)"):
        h_disp = st.text_input("Hora disparo SCADA:", value="21:15:02")
        h_vec = st.text_input("Hora disparo Vecino:", value="21:15:03")
        h_dcierre = st.text_input("Hora recierre Aperturado:", value="21:15:10")
        h_vcierre = st.text_input("Hora recierre Vecino:", value="21:15:12")
        h_rep = st.text_input("Hora reporte CCM:", value="21:20:00")
        h_env_st = st.text_input("Hora envío ST:", value="21:25:00")
        h_foto_disp = st.text_input("Hora reporte Técnico Sub:", value="21:32:00")
        h_foto_vec = st.text_input("Hora reporte Técnico Vecino:", value="22:23:00")
        h_cat = st.text_input("Hora reporte Catenaria:", value="07:28:00")

    with st.expander("5. Personal Involucrado"):
        sup_pco_val = st.text_input("Supervisor PCO:", value="Jesús Salguedo")
        per_sub_val = st.text_input("Personal Subestaciones:", value="Carlos Morales")
        per_cat_val = st.text_input("Personal Catenarias:", value="Luis Vargas")


context = {
    # 1, 3, 7, 16, 20 (Autocompletados Aperturado)
    "interruptor_aperturado": datos_ap["interruptor"],
    "alimentador_ser_aperturado": datos_ap["alimentador_ser"],
    "ser_aperturado": datos_ap["ser"],
    "alimentador_aperturado": datos_ap["alimentador"],
    "alimentador_aperturado_num": datos_ap["interruptor_num"],

    # 2, 6, 8, 18, 21 (Autocompletados Vecino)
    "interruptor_vecino": datos_vec["interruptor"],
    "alimentador_ser_vecino": datos_vec["alimentador_ser"],
    "ser_vecino": datos_vec["ser"],
    "alimentador_vecino": datos_vec["alimentador"],
    "alimentador_vecino_num": datos_vec["interruptor_num"],

    # Funciones y protecciones
    "funcion_disparo_inicial": f_disp_ini,
    "funcion_disparo_final": f_disp_fin,
    "st_aperturado": st_ap,
    "st_vecino": st_vec,
    "st_zona": st_zn,
    "corriente": corriente_val,

    # Datos operativos
    "fecha": fecha_val,
    "dia": dia_val,
    "tiempo_entre_trenes": headway,
    "condicion_señales": condicion,
    "operacion": operacion_val,
    "zona": zona,

    # Cronología
    "hora_vicos_disparo": h_disp,
    "hora_vicos_vecino": h_vec,
    "hora_vicos_dcierre": h_dcierre,
    "hora_vicos_vcierre": h_vcierre,
    "hora_reporte": h_rep,
    "hora_envio_st": h_env_st,
    "hora_foto_disparo": h_foto_disp,
    "hora_foto_vecino": h_foto_vec,
    "hora_cat": h_cat,

    # Personal
    "sup_pco": sup_pco_val,
    "per_sub": per_sub_val,
    "per_cat": per_cat_val
}

import streamlit.components.v1 as components
import base64

with col_preview:
    st.header("📄 Vista Previa Real del Documento")

    # Si hay plantilla cargada o local, generamos el docx en memoria
    if plantilla_word is not None:
        doc = DocxTemplate(plantilla_word)
        doc.render(context)
        
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        docx_bytes = buffer.getvalue()
        
        # Codificamos a Base64 para pasarlo al visor JS
        docx_b64 = base64.b64encode(docx_bytes).decode("utf-8")

        # Componente visualizador docx-preview
        viewer_html = f"""
        <div id="document-container" style="background-color: #525659; padding: 20px; height: 750px; overflow-y: auto; border-radius: 6px;"></div>
        
        <!-- Librería JSZip y docx-preview desde CDN -->
        <script src="https://unpkg.com/jszip/dist/jszip.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/docx-preview@0.1.15/dist/docx-preview.min.js"></script>
        
        <script>
            var base64Data = "{docx_b64}";
            var byteCharacters = atob(base64Data);
            var byteNumbers = new Array(byteCharacters.length);
            for (var i = 0; i < byteCharacters.length; i++) {{
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }}
            var byteArray = new Uint8Array(byteNumbers);
            var blob = new Blob([byteArray], {{type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}});

            var container = document.getElementById("document-container");
            docx.renderAsync(blob, container)
                .then(function() {{
                    console.log("Word renderizado con éxito");
                }})
                .catch(function(err) {{
                    console.error("Error al renderizar docx:", err);
                }});
        </script>
        """
        
        components.html(viewer_html, height=780, scrolling=False)

        st.download_button(
            label="📥 Descargar Informe Completo (.docx)",
            data=buffer,
            file_name=f"Informe_Disparo_{context['ser_aperturado']}_{context['fecha'].replace('/', '-')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
    else:
        st.info("💡 Carga o selecciona tu plantilla `.docx` para ver la previsualización interactiva.")