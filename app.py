import streamlit as st
from docxtpl import DocxTemplate
import io
from datetime import datetime

st.set_page_config(layout="wide", page_title="Generador de Informe SCADA - CCM")

# 1. Base de datos de equipos / subestaciones parametrizadas
CATALOGO_ALIMENTADORES = {
    "SER16_GAM - AL4 (154-4)": {
        "interruptor": "154-4 SER16_GAM",
        "alimentador_ser": "AL4-154 SER16_GAM",
        "ser": "SER16_GAM",
        "alimentador": "AL4",
        "interruptor_num": "154-4"
    },
    "SER20_CAA - AL2 (154-2)": {
        "interruptor": "154-2 SER20_CAA",
        "alimentador_ser": "AL2-154 SER20_CAA",
        "ser": "SER20_CAA",
        "alimentador": "AL2",
        "interruptor_num": "154-2"
    },
    "SER11_CAB - AL1 (154-1)": {
        "interruptor": "154-1 SER11_CAB",
        "alimentador_ser": "AL1-154 SER11_CAB",
        "ser": "SER11_CAB",
        "alimentador": "AL1",
        "interruptor_num": "154-1"
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
        f_disp_ini = st.text_input("Función SCADA Aperturado:", value="Disparo instantáneo Disparador di/dt")
        f_disp_fin = st.text_input("Función Relé Aperturado:", value="Disparo Imax")
        f_disp_vec_ini = st.text_input("Función SCADA Vecino:", value="Disparo por S/E vecina")
        f_disp_vec_fin = st.text_input("Función Relé Vecino:", value="Arrastre desde SSEE colateral activo")
        
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
        operacion_val = c_op5.text_input("Horario Operación:", value="Comercial")
        zona_val = c_op6.text_input("Zona Eléctrica:", value="Zona 3")

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
    "funcion_disparo_vecina_inicial": f_disp_vec_ini,
    "funcion_disparo_vecina_final": f_disp_vec_fin,
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
    "zona": zona_val,

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

with col_preview:
    st.header("📄 Vista Previa (Formato Word A4)")

    # 1. Estilos CSS para simular hoja Word formal
    hoja_estilos = """
    <style>
        .hoja-word {
            background-color: #ffffff;
            color: #1a1a1a;
            padding: 35px 45px;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
            line-height: 1.5;
            border: 1px solid #d3d3d3;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
            border-radius: 4px;
            max-height: 85vh;
            overflow-y: auto;
        }
        .hoja-word h3 {
            color: #0b3c5d;
            font-size: 14px;
            margin-top: 18px;
            margin-bottom: 8px;
            text-transform: uppercase;
            border-bottom: 1px solid #0b3c5d;
            padding-bottom: 3px;
        }
        .variable-destacada {
            background-color: #fff2a8;
            padding: 1px 4px;
            border-radius: 3px;
            font-weight: 600;
            color: #000;
        }
        .tabla-word {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            font-size: 12px;
        }
        .tabla-word th, .tabla-word td {
            border: 1px solid #7f8c8d;
            padding: 6px 8px;
            text-align: left;
        }
        .tabla-word th {
            background-color: #e9ecef;
            color: #2c3e50;
            font-weight: bold;
            text-align: center;
        }
        .item-lista {
            margin-bottom: 6px;
        }
    </style>
    """

    # 2. Estructura HTML con tus variables dinámicas
    contenido_html = f"""
    {hoja_estilos}
    <div class="hoja-word">
        <h2 style="text-align: center; font-size: 16px; margin-bottom: 20px; color: #111;">
            INFORME TÉCNICO DE DISPARO Y RECIERRE DE CELDAS DC
        </h2>

        <h3>1. EVENTO: DISPARO CON RECIERRE DE INTERRUPTORES {context['interruptor_aperturado']} Y {context['interruptor_vecino']}</h3>
        <p>El presente informe tiene como objetivo dar a conocer los detalles del evento de apertura de los interruptores con recierre en las celdas DC:</p>
        
        <div class="item-lista">
            Ø <span class="variable-destacada">{context['alimentador_ser_aperturado']}</span> en el sistema SCADA VICOS RSC por función 
            “<span class="variable-destacada">{context['funcion_disparo_inicial']}</span>” y por actuación del relé Sitras PRO por función 
            “<span class="variable-destacada">{context['funcion_disparo_final']}</span>”.
        </div>
        <div class="item-lista">
            Ø <span class="variable-destacada">{context['alimentador_ser_vecino']}</span> en el sistema SCADA_VICOS RSC por función 
            “<span class="variable-destacada">{context['funcion_disparo_vecina_inicial']}</span>” y por actuación del relé Sitras PRO por función 
            “<span class="variable-destacada">{context['funcion_disparo_vecina_final']}</span>”.
        </div>

        <h3>2. UBICACIÓN, FECHA Y HORA</h3>
        <p>
            <strong>Subestaciones:</strong> <span class="variable-destacada">{context['ser_aperturado']}</span> y <span class="variable-destacada">{context['ser_vecino']}</span><br>
            <strong>Fecha:</strong> {context['dia']} {context['fecha']}<br>
            <strong>Hora:</strong> <span class="variable-destacada">{context['hora_vicos_disparo']}</span> horas; según sistema SCADA_VICOS RSC.
        </p>

        <h3>3. DATOS OPERATIVOS AL MOMENTO DEL EVENTO</h3>
        <p>
            • <strong>Headway de trenes:</strong> {context['tiempo_entre_trenes']} min<br>
            • <strong>Condición:</strong> {context['condicion_señales']}<br>
            • <strong>Horario de Operación:</strong> {context['operacion']}<br>
            • <strong>Zona eléctrica afectada:</strong> {context['zona']}
        </p>

        <h3>4. CRONOLOGÍA DE EVENTOS</h3>
        <table class="tabla-word">
            <thead>
                <tr>
                    <th style="width: 15%;">HORA</th>
                    <th style="width: 25%;">UBICACIÓN</th>
                    <th style="width: 60%;">DESCRIPCIÓN DEL EVENTO</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>{context['hora_vicos_disparo']}</td>
                    <td><strong>{context['ser_aperturado']}</strong></td>
                    <td>Se registró en SCADA_VICOS función “{context['funcion_disparo_inicial']}” del {context['alimentador_aperturado']}. En relé Sitras PRO: “{context['funcion_disparo_final']}” (ST {context['st_aperturado']}).</td>
                </tr>
                <tr>
                    <td>{context['hora_vicos_vecino']}</td>
                    <td><strong>{context['ser_vecino']}</strong></td>
                    <td>Se registró en SCADA_VICOS función “{context['funcion_disparo_vecina_inicial']}” del {context['alimentador_vecino']}. En relé Sitras PRO: “{context['funcion_disparo_vecina_final']}” (ST {context['st_vecino']}).</td>
                </tr>
                <tr>
                    <td>{context['hora_vicos_dcierre']}</td>
                    <td><strong>{context['ser_aperturado']}</strong></td>
                    <td>Recierre automático del interruptor {context['alimentador_aperturado_num']} en {context['alimentador_aperturado']} con resultado exitoso.</td>
                </tr>
                <tr>
                    <td>{context['hora_vicos_vcierre']}</td>
                    <td><strong>{context['ser_vecino']}</strong></td>
                    <td>Recierre automático del interruptor {context['alimentador_vecino_num']} en {context['alimentador_vecino']} con resultado exitoso.</td>
                </tr>
                <tr>
                    <td>{context['hora_reporte']}</td>
                    <td>CCM</td>
                    <td>Se comunica al supervisor de PCO {context['sup_pco']}. Reporte en grupo CCM_SUB_CAT de SYC.</td>
                </tr>
                <tr>
                    <td>{context['hora_foto_disparo']}</td>
                    <td>{context['ser_aperturado']}</td>
                    <td>Técnico {context['per_sub']} informa relé {context['alimentador_aperturado']} registró “{context['funcion_disparo_final']}” con {context['corriente']} A. Operativo sin alarmas.</td>
                </tr>
                <tr>
                    <td>{context['hora_cat']}</td>
                    <td>Zona {context['zona']} (Vía principal)</td>
                    <td>Técnico Catenarias {context['per_cat']} realizó inspección visual LAC en zona {context['zona']}. Sin observaciones.</td>
                </tr>
            </tbody>
        </table>
    </div>
    """

    # 3. Renderizar el HTML en Streamlit
    st.markdown(contenido_html, unsafe_allow_html=True)
    
    st.write("") # Espaciador

    # 4. Generación y descarga del .docx
    if plantilla_word is not None:
        doc = DocxTemplate(plantilla_word)
        doc.render(context)
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        st.download_button(
            label="📥 Descargar Informe Oficial (.docx)",
            data=buffer,
            file_name=f"Informe_Disparo_{context['ser_aperturado']}_{context['fecha'].replace('/', '-')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
    else:
        st.warning("⚠️ Carga el archivo base `.docx` en el panel izquierdo para habilitar la exportación.")