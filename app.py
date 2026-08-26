import streamlit as st
from docxtpl import DocxTemplate
import streamlit.components.v1 as components
import io
import base64
import os
from datetime import datetime
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
from streamlit_image_coordinates import streamlit_image_coordinates
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm

st.set_page_config(layout="wide", page_title="Generador de Informes SCADA - CCM")

# =========================================================
# MODAL CON ENVÍO DIRECTO A WORD (SIN DESCARGAS)
# =========================================================
# =========================================================
# MODAL CON RENDERIZADO VISUAL Y ASIGNACIÓN DIRECTA
# =========================================================
@st.dialog("✏️ Editor Visual Sitras PRO", width="large")
def modal_editor_sitras(pdf_bytes):
    doc_pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc_pdf.load_page(0)
    pix = page.get_pixmap(dpi=130)
    img_b64 = base64.b64encode(pix.tobytes("jpeg")).decode("utf-8")
    w, h = pix.width, pix.height

    editor_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body {{ margin: 0; font-family: sans-serif; background-color: #262730; color: #fff; text-align: center; }}
        #toolbar {{ padding: 8px; background: #1e1e24; display: flex; justify-content: center; gap: 10px; align-items: center; border-radius: 6px; margin-bottom: 8px; font-size: 13px; }}
        #instrucciones {{ font-weight: bold; color: #ff4b4b; }}
        #canvas-wrapper {{ position: relative; display: inline-block; max-height: 480px; overflow-y: auto; border: 2px solid #555; border-radius: 4px; }}
        canvas {{ display: block; cursor: crosshair; }}
        button {{ padding: 6px 12px; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; }}
        .btn-undo {{ background-color: #f39c12; color: white; }}
        .btn-reset {{ background-color: #555; color: white; }}
        .btn-word {{ background-color: #0078d4; color: white; display: none; font-size: 14px; padding: 8px 16px; }}
      </style>
    </head>
    <body>
      <div id="toolbar">
        <span id="instrucciones">Paso 1: Arrastra el mouse para encuadrar "Función de disparo".</span>
        <button class="btn-undo" onclick="deshacer()">↩ Deshacer (Clic Derecho)</button>
        <button class="btn-reset" onclick="resetCanvas()">🔄 Reiniciar</button>
      </div>

      <div id="canvas-wrapper">
        <canvas id="canvasSitras" width="{w}" height="{h}"></canvas>
      </div>

      <div style="margin-top: 10px;">
        <button id="btnWord" class="btn-word" onclick="guardarImagen()">📄 Guardar Imagen Anexo</button>
      </div>

      <script>
        const canvas = document.getElementById("canvasSitras");
        const ctx = canvas.getContext("2d");
        const instruc = document.getElementById("instrucciones");
        const btnWord = document.getElementById("btnWord");

        const bgImg = new Image();
        bgImg.src = "data:image/jpeg;base64,{img_b64}";

        const eventos = [
          "Función de disparo",
          "Apertura automática del interruptor",
          "Re-cierre exitoso del interruptor"
        ];

        let paso = 0; 
        let modo = "RECT"; 
        let isDrawing = false;
        let startX = 0, startY = 0;
        let currentRect = null;
        let anotaciones = []; 

        bgImg.onload = () => redraw();

        function redraw() {{
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.drawImage(bgImg, 0, 0);

          anotaciones.forEach(a => {{
            ctx.strokeStyle = "red";
            ctx.lineWidth = 3;
            ctx.strokeRect(a.rect.x, a.rect.y, a.rect.w, a.rect.h);

            ctx.fillStyle = "white";
            ctx.fillRect(a.textBox.x, a.textBox.y, a.textBox.w, a.textBox.h);
            ctx.strokeStyle = "red";
            ctx.lineWidth = 2;
            ctx.strokeRect(a.textBox.x, a.textBox.y, a.textBox.w, a.textBox.h);

            ctx.fillStyle = "red";
            ctx.font = "bold 14px Arial";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillText(a.texto, a.textBox.x + (a.textBox.w / 2), a.textBox.y + (a.textBox.h / 2));

            ctx.beginPath();
            ctx.moveTo(a.arrow.fromX, a.arrow.fromY);
            ctx.lineTo(a.arrow.toX, a.arrow.toY);
            ctx.stroke();

            const headlen = 9;
            const angle = Math.atan2(a.arrow.toY - a.arrow.fromY, a.arrow.toX - a.arrow.fromX);
            ctx.beginPath();
            ctx.moveTo(a.arrow.toX, a.arrow.toY);
            ctx.lineTo(a.arrow.toX - headlen * Math.cos(angle - Math.PI / 6), a.arrow.toY - headlen * Math.sin(angle - Math.PI / 6));
            ctx.lineTo(a.arrow.toX - headlen * Math.cos(angle + Math.PI / 6), a.arrow.toY - headlen * Math.sin(angle + Math.PI / 6));
            ctx.fillStyle = "red";
            ctx.fill();
          }});

          if (currentRect) {{
            ctx.strokeStyle = "red";
            ctx.lineWidth = 3;
            ctx.strokeRect(currentRect.x, currentRect.y, currentRect.w, currentRect.h);
          }}
        }}

        function getMousePos(evt) {{
          const rect = canvas.getBoundingClientRect();
          const scaleX = canvas.width / rect.width;
          const scaleY = canvas.height / rect.height;
          return {{
            x: (evt.clientX - rect.left) * scaleX,
            y: (evt.clientY - rect.top) * scaleY
          }};
        }}

        window.oncontextmenu = (e) => {{
          e.preventDefault();
          deshacer();
        }};

        function deshacer() {{
          if (modo === "CLICK_POS") {{
            currentRect = null;
            modo = "RECT";
            instruc.innerText = `Paso ${{paso + 1}}: Arrastra el mouse para encuadrar "${{eventos[paso]}}"`;
          }} else if (anotaciones.length > 0) {{
            anotaciones.pop();
            paso--;
            modo = "RECT";
            btnWord.style.display = "none";
            instruc.innerText = `Paso ${{paso + 1}}: Arrastra el mouse para encuadrar "${{eventos[paso]}}"`;
          }}
          redraw();
        }}

        canvas.onmousedown = (e) => {{
          if (e.button === 2) return;
          if (paso >= 3) return;
          const pos = getMousePos(e);

          if (modo === "RECT") {{
            isDrawing = true;
            startX = pos.x;
            startY = pos.y;
            currentRect = {{ x: startX, y: startY, w: 0, h: 0 }};
          }} else if (modo === "CLICK_POS") {{
            const clickArriba = pos.y < (currentRect.y + currentRect.h / 2);
            const centroX = currentRect.x + currentRect.w / 2;
            
            ctx.font = "bold 14px Arial";
            const textWidth = ctx.measureText(eventos[paso]).width + 30;
            const textHeight = 28;
            
            let tbX = centroX - textWidth / 2;
            let tbY = clickArriba ? currentRect.y - 45 : currentRect.y + currentRect.h + 20;
            let fromY = clickArriba ? tbY + textHeight : tbY;
            let toY = clickArriba ? currentRect.y : currentRect.y + currentRect.h;

            anotaciones.push({{
              texto: eventos[paso],
              rect: currentRect,
              textBox: {{ x: tbX, y: tbY, w: textWidth, h: textHeight }},
              arrow: {{ fromX: centroX, fromY: fromY, toX: centroX, toY: toY }}
            }});

            currentRect = null;
            paso++;

            if (paso < 3) {{
              modo = "RECT";
              instruc.innerText = `Paso ${{paso + 1}}: Arrastra el mouse para encuadrar "${{eventos[paso]}}"`;
            }} else {{
              instruc.innerText = "✅ ¡Listo! Presiona el botón azul para generar el anexo.";
              btnWord.style.display = "inline-block";
            }}
            redraw();
          }}
        }};

        canvas.onmousemove = (e) => {{
          if (!isDrawing) return;
          const pos = getMousePos(e);
          currentRect = {{
            x: Math.min(startX, pos.x),
            y: Math.min(startY, pos.y),
            w: Math.abs(pos.x - startX),
            h: Math.abs(pos.y - startY)
          }};
          redraw();
        }};

        canvas.onmouseup = () => {{
          if (!isDrawing) return;
          isDrawing = false;
          if (currentRect && currentRect.w > 15 && currentRect.h > 8) {{
            modo = "CLICK_POS";
            instruc.innerText = `Haz un clic ARRIBA o ABAJO del recuadro para posicionar "${{eventos[paso]}}".`;
          }} else {{
            currentRect = null;
            redraw();
          }}
        }};

        function resetCanvas() {{
          paso = 0;
          modo = "RECT";
          currentRect = null;
          anotaciones = [];
          btnWord.style.display = "none";
          instruc.innerText = `Paso 1: Arrastra el mouse para encuadrar "${{eventos[0]}}"`;
          redraw();
        }}

        function guardarImagen() {{
          const link = document.createElement("a");
          link.download = "Anexo_Sitras_Editado.jpg";
          link.href = canvas.toDataURL("image/jpeg", 0.95);
          link.click();
        }}
      </script>
    </body>
    </html>
    """
    components.html(editor_html, height=580, scrolling=False)

# =========================================================
# 1. CATÁLOGO COMPLETO DE ALIMENTADORES Y ZONAS
# =========================================================
CATALOGO_ALIMENTADORES = {
    "SER01_PTVES - AL3 (154-3)": {"interruptor": "154-3 SER01_PTVES", "alimentador_ser": "AL3-154 SER01_PTVES", "ser": "SER01_PTVES", "alimentador": "AL3", "interruptor_num": "154-3", "zona":"201,203"},
    "SER01_PTVES - AL4 (154-4)": {"interruptor": "154-4 SER01_PTVES", "alimentador_ser": "AL4-154 SER01_PTVES", "ser": "SER01_PTVES", "alimentador": "AL4", "interruptor_num": "154-4", "zona":"202,204"},
    "SER03_PIN - AL1 (154-1)": {"interruptor": "154-1 SER03_PIN", "alimentador_ser": "AL1-154 SER03_PIN", "ser": "SER03_PIN", "alimentador": "AL1", "interruptor_num": "154-1", "zona":"201,203"},
    "SER03_PIN - AL2 (154-2)": {"interruptor": "154-2 SER03_PIN", "alimentador_ser": "AL2-154 SER03_PIN", "ser": "SER03_PIN", "alimentador": "AL2", "interruptor_num": "154-2", "zona":"202,204"},
    "SER03_PIN - AL3 (154-3)": {"interruptor": "154-3 SER03_PIN", "alimentador_ser": "AL3-154 SER03_PIN", "ser": "SER03_PIN", "alimentador": "AL3", "interruptor_num": "154-3", "zona":"205"},
    "SER03_PIN - AL4 (154-4)": {"interruptor": "154-4 SER03_PIN", "alimentador_ser": "AL4-154 SER03_PIN", "ser": "SER03_PIN", "alimentador": "AL4", "interruptor_num": "154-4", "zona":"206"},
    "SER05_VMA - AL1 (154-1)": {"interruptor": "154-1 SER05_VMA", "alimentador_ser": "AL1-154 SER05_VMA", "ser": "SER05_VMA", "alimentador": "AL1", "interruptor_num": "154-1", "zona":"205"},
    "SER05_VMA - AL2 (154-2)": {"interruptor": "154-2 SER05_VMA", "alimentador_ser": "AL2-154 SER05_VMA", "ser": "SER05_VMA", "alimentador": "AL2", "interruptor_num": "154-2", "zona":"206"},
    "SER05_VMA - AL3 (154-3)": {"interruptor": "154-3 SER05_VMA", "alimentador_ser": "AL3-154 SER05_VMA", "ser": "SER05_VMA", "alimentador": "AL3", "interruptor_num": "154-3", "zona":"207"},
    "SER05_VMA - AL4 (154-4)": {"interruptor": "154-4 SER05_VMA", "alimentador_ser": "AL4-154 SER05_VMA", "ser": "SER05_VMA", "alimentador": "AL4", "interruptor_num": "154-4", "zona":"208"},
    "SER08_ATO - AL1 (154-1)": {"interruptor": "154-1 SER08_ATO", "alimentador_ser": "AL1-154 SER08_ATO", "ser": "SER08_ATO", "alimentador": "AL1", "interruptor_num": "154-1", "zona":"207"},
    "SER08_ATO - AL2 (154-2)": {"interruptor": "154-2 SER08_ATO", "alimentador_ser": "AL2-154 SER08_ATO", "ser": "SER08_ATO", "alimentador": "AL2", "interruptor_num": "154-2", "zona":"208"},
    "SER08_ATO - AL3 (154-3)": {"interruptor": "154-3 SER08_ATO", "alimentador_ser": "AL3-154 SER08_ATO", "ser": "SER08_ATO", "alimentador": "AL3", "interruptor_num": "154-3", "zona":"209"},
    "SER08_ATO - AL4 (154-4)": {"interruptor": "154-4 SER08_ATO", "alimentador_ser": "AL4-154 SER08_ATO", "ser": "SER08_ATO", "alimentador": "AL4", "interruptor_num": "154-4", "zona":"210"},
    "SER11_CAB - AL1 (154-1)": {"interruptor": "154-1 SER11_CAB", "alimentador_ser": "AL1-154 SER11_CAB", "ser": "SER11_CAB", "alimentador": "AL1", "interruptor_num": "154-1", "zona":"209"},
    "SER11_CAB - AL2 (154-2)": {"interruptor": "154-2 SER11_CAB", "alimentador_ser": "AL2-154 SER11_CAB", "ser": "SER11_CAB", "alimentador": "AL2", "interruptor_num": "154-2", "zona":"210"},
    "SER11_CAB - AL3 (154-3)": {"interruptor": "154-3 SER11_CAB", "alimentador_ser": "AL3-154 SER11_CAB", "ser": "SER11_CAB", "alimentador": "AL3", "interruptor_num": "154-3", "zona":"211"},
    "SER11_CAB - AL4 (154-4)": {"interruptor": "154-4 SER11_CAB", "alimentador_ser": "AL4-154 SER11_CAB", "ser": "SER11_CAB", "alimentador": "AL4", "interruptor_num": "154-4", "zona":"212"},
    "SER14_CUL - AL1 (154-1)": {"interruptor": "154-1 SER14_CUL", "alimentador_ser": "AL1-154 SER14_CUL", "ser": "SER14_CUL", "alimentador": "AL1", "interruptor_num": "154-1", "zona":"211"},
    "SER14_CUL - AL2 (154-2)": {"interruptor": "154-2 SER14_CUL", "alimentador_ser": "AL2-154 SER14_CUL", "ser": "SER14_CUL", "alimentador": "AL2", "interruptor_num": "154-2", "zona":"212"},
    "SER14_CUL - AL3 (154-3)": {"interruptor": "154-3 SER14_CUL", "alimentador_ser": "AL3-154 SER14_CUL", "ser": "SER14_CUL", "alimentador": "AL3", "interruptor_num": "154-3", "zona":"213"},
    "SER14_CUL - AL4 (154-4)": {"interruptor": "154-4 SER14_CUL", "alimentador_ser": "AL4-154 SER14_CUL", "ser": "SER14_CUL", "alimentador": "AL4", "interruptor_num": "154-4", "zona":"214"},
    "SER16_GAM - AL1 (154-1)": {"interruptor": "154-1 SER16_GAM", "alimentador_ser": "AL1-154 SER16_GAM", "ser": "SER16_GAM", "alimentador": "AL1", "interruptor_num": "154-1", "zona":"213"},
    "SER16_GAM - AL2 (154-2)": {"interruptor": "154-2 SER16_GAM", "alimentador_ser": "AL2-154 SER16_GAM", "ser": "SER16_GAM", "alimentador": "AL2", "interruptor_num": "154-2", "zona":"214"},
    "SER16_GAM - AL3 (154-3)": {"interruptor": "154-3 SER16_GAM", "alimentador_ser": "AL3-154 SER16_GAM", "ser": "SER16_GAM", "alimentador": "AL3", "interruptor_num": "154-3", "zona":"215"},
    "SER16_GAM - AL4 (154-4)": {"interruptor": "154-4 SER16_GAM", "alimentador_ser": "AL4-154 SER16_GAM", "ser": "SER16_GAM", "alimentador": "AL4", "interruptor_num": "154-4", "zona":"216"},
    "SER20_CAA - AL1 (154-1)": {"interruptor": "154-1 SER20_CAA", "alimentador_ser": "AL1-154 SER20_CAA", "ser": "SER20_CAA", "alimentador": "AL1", "interruptor_num": "154-1", "zona":"215"},
    "SER20_CAA - AL2 (154-2)": {"interruptor": "154-2 SER20_CAA", "alimentador_ser": "AL2-154 SER20_CAA", "ser": "SER20_CAA", "alimentador": "AL2", "interruptor_num": "154-2", "zona":"216"},
    "SER20_CAA - AL3 (154-3)": {"interruptor": "154-3 SER20_CAA", "alimentador_ser": "AL3-154 SER20_CAA", "ser": "SER20_CAA", "alimentador": "AL3", "interruptor_num": "154-3", "zona":"217"},
    "SER20_CAA - AL4 (154-4)": {"interruptor": "154-4 SER20_CAA", "alimentador_ser": "AL4-154 SER20_CAA", "ser": "SER20_CAA", "alimentador": "AL4", "interruptor_num": "154-4", "zona":"218"},
    "SER22_JAR - AL1 (154-1)": {"interruptor": "154-1 SER22_JAR", "alimentador_ser": "AL1-154 SER22_JAR", "ser": "SER22_JAR", "alimentador": "AL1", "interruptor_num": "154-1", "zona":"217"},
    "SER22_JAR - AL2 (154-2)": {"interruptor": "154-2 SER22_JAR", "alimentador_ser": "AL2-154 SER22_JAR", "ser": "SER22_JAR", "alimentador": "AL2", "interruptor_num": "154-2", "zona":"218"},
    "SER22_JAR - AL3 (154-3)": {"interruptor": "154-3 SER22_JAR", "alimentador_ser": "AL3-154 SER22_JAR", "ser": "SER22_JAR", "alimentador": "AL3", "interruptor_num": "154-3", "zona":"219"},
    "SER22_JAR - AL4 (154-4)": {"interruptor": "154-4 SER22_JAR", "alimentador_ser": "AL4-154 SER22_JAR", "ser": "SER22_JAR", "alimentador": "AL4", "interruptor_num": "154-4", "zona":"220"},
    "SER25_SMA - AL1 (154-1)": {"interruptor": "154-1 SER25_SMA", "alimentador_ser": "AL1-154 SER25_SMA", "ser": "SER25_SMA", "alimentador": "AL1", "interruptor_num": "154-1", "zona":"219"},
    "SER25_SMA - AL2 (154-2)": {"interruptor": "154-2 SER25_SMA", "alimentador_ser": "AL2-154 SER25_SMA", "ser": "SER25_SMA", "alimentador": "AL2", "interruptor_num": "154-2", "zona":"220"},
    "SER25_SMA - AL3 (154-1)": {"interruptor": "154-3 SER25_SMA", "alimentador_ser": "AL3-154 SER25_SMA", "ser": "SER25_SMA", "alimentador": "AL3", "interruptor_num": "154-3", "zona":"221-223"},
    "SER25_SMA - AL4 (154-4)": {"interruptor": "154-4 SER25_SMA", "alimentador_ser": "AL4-154 SER25_SMA", "ser": "SER25_SMA", "alimentador": "AL4", "interruptor_num": "154-4", "zona":"222-224"},
    "SER27_BAY - AL1 (154-1)": {"interruptor": "154-1 SER27_BAY", "alimentador_ser": "AL1-154 SER27_BAY", "ser": "SER27_BAY", "alimentador": "AL1", "interruptor_num": "154-1", "zona":"221-223"},
    "SER27_BAY - AL2 (154-2)": {"interruptor": "154-2 SER27_BAY", "alimentador_ser": "AL2-154 SER27_BAY", "ser": "SER27_BAY", "alimentador": "AL2", "interruptor_num": "154-2", "zona":"222-224"}
}

st.title("⚡ Generador de Informes de Disparo y Recierre DC")

col_form, col_preview = st.columns([1, 1], gap="medium")

with col_form:
    st.header("📝 Parámetros del Evento")

    plantilla_path = "plantilla_base.docx"
    plantilla_doc = None
    
    if os.path.exists(plantilla_path):
        plantilla_doc = plantilla_path
    else:
        plantilla_subida = st.file_uploader("Cargar plantilla base (.docx)", type=["docx"])
        if plantilla_subida is not None:
            plantilla_doc = plantilla_subida

    with st.expander("1. Selección de Equipos (Filtro por Zona)", expanded=True):
        opciones_aperturado = list(CATALOGO_ALIMENTADORES.keys())
        sel_aperturado = st.selectbox("Subestación / Celda Aperturada:", opciones_aperturado, index=0)
        datos_ap = CATALOGO_ALIMENTADORES[sel_aperturado]
        zona_detectada = datos_ap["zona"]

        opciones_vecino_filtradas = [
            k for k, v in CATALOGO_ALIMENTADORES.items() 
            if v["zona"] == zona_detectada and k != sel_aperturado
        ]
        if not opciones_vecino_filtradas:
            opciones_vecino_filtradas = [k for k in CATALOGO_ALIMENTADORES.keys() if k != sel_aperturado]

        sel_vecino = st.selectbox("Subestación / Celda Vecina:", opciones_vecino_filtradas, index=0)
        datos_vec = CATALOGO_ALIMENTADORES[sel_vecino]

    with st.expander("2. Funciones de Protección y ST"):
        f_disp_ini = st.text_input("Función SCADA Aperturado:", value="Disparo instantáneo Disparador di/dt")
        f_disp_fin = st.text_input("Función Relé Aperturado:", value="Disparo Imax")
        f_disp_vec_ini = "Disparo por S/E vecina"
        f_disp_vec_fin = "Arrastre desde SSEE colateral activo"
        c_st1, c_st2, c_st3 = st.columns(3)
        st_ap = c_st1.text_input("ST Aperturado:", value="1404241")
        st_vec = c_st2.text_input("ST Vecino:", value="1404242")
        st_zn = c_st3.text_input("ST Zona:", value="1404245")
        corriente_val = st.text_input("Corriente registrada (A):", value="2450")

    with st.expander("3. Datos de Operación"):
        c_op1, c_op2 = st.columns(2)
        fecha_raw = c_op1.date_input("Fecha:", value=datetime.today())
        fecha_val = fecha_raw.strftime("%d/%m/%Y")
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        dia_val = dias_semana[fecha_raw.weekday()]
        c_op2.text_input("Día (Automático):", value=dia_val, disabled=True)
        c_op3, c_op4 = st.columns(2)
        headway = c_op3.text_input("Headway (min):", value="3")
        condicion = c_op4.selectbox("Condición Señales:", ["Señales encendidas", "Señales apagadas"])
        c_op5, c_op6 = st.columns(2)
        operacion_val = c_op5.selectbox("Horario Operación:", ["Hora pico", "Hora valle"])
        zona_manual = c_op6.text_input("Zona afectada (en documento):", value=f"Zona {zona_detectada}")
    
    with st.expander("4. Cronología y Horas (HH:MM:SS)"):
        st.info("💡 Las filas se reordenarán e insertarán automáticamente en la tabla de Word.")
        h_disp = st.text_input("Hora disparo Aperturado (SCADA):", value="21:15:02")
        h_vec = st.text_input("Hora disparo Vecino (SCADA):", value="21:15:03")
        h_dcierre = st.text_input("Hora recierre Aperturado:", value="21:15:10")
        h_vcierre = st.text_input("Hora recierre Vecino:", value="21:15:12")
        h_rep = st.text_input("Hora reporte CCM a PCO:", value="21:20:00")
        h_env_st = st.text_input("Hora envío solicitud ST:", value="21:25:00")
        h_foto_disp = st.text_input("Hora foto Técnico Subestaciones de SER Disparo:", value="21:32:00")
        h_foto_vec = st.text_input("Hora foto Técnico Subestaciones SER Vecino:", value="22:23:00")
        h_cat = st.text_input("Hora informe Técnico Catenaria:", value="07:28:00")

    with st.expander("5. Personal Involucrado"):
        sup_pco_val = st.text_input("Supervisor PCO:", value="Jesús Salguedo")
        per_sub_val = st.text_input("Personal Subestaciones:", value="Carlos Morales")
        per_cat_val = st.text_input("Personal Catenarias:", value="Luis Vargas")

 

# =========================================================
    # SECCIÓN 6: DENTRO DE COL_FORM
    # =========================================================
    with st.expander("6. Anexos y Gráficos", expanded=True):
        st.write("Sube el PDF para abrir el editor visual en tiempo real.")
        pdf_file = st.file_uploader("Log Sitras PRO (.pdf)", type=["pdf"])
        
        if pdf_file is not None:
            if st.button("🚀 Abrir Editor de Sitras PRO", use_container_width=True):
                modal_editor_sitras(pdf_file.getvalue())

        anexo_cargado = st.file_uploader("Cargar Imagen Anexo Procesada (.jpg / .png):", type=["jpg", "png", "jpeg"])
        if anexo_cargado is not None:
            st.session_state["anexo_sitras_file"] = anexo_cargado
            st.success("✅ Imagen lista para insertarse en el Word.")

# =========================================================
# CONSTRUCCIÓN Y AUTO-ORDENAMIENTO DE EVENTOS
# =========================================================
eventos_para_ordenar = []

if h_disp.strip(): eventos_para_ordenar.append({"hora": h_disp.strip(), "ubicacion": datos_ap["ser"], "descripcion": f"Se registró en el sistema SCADA_VICOS RSC, función “{f_disp_ini}” del alimentador {datos_ap['alimentador']}. Asimismo, se registró en el relé Sitras PRO por función “{f_disp_fin}” (ST {st_ap})."})
if h_vec.strip(): eventos_para_ordenar.append({"hora": h_vec.strip(), "ubicacion": datos_vec["ser"], "descripcion": f"Se registró en el sistema SCADA_VICOS RSC, función “{f_disp_vec_ini}” del alimentador {datos_vec['alimentador']}. Asimismo, se registró en el relé Sitras PRO por función “{f_disp_vec_fin}” (ST {st_vec})."})
if h_dcierre.strip(): eventos_para_ordenar.append({"hora": h_dcierre.strip(), "ubicacion": datos_ap["ser"], "descripcion": f"Recierre automático del interruptor {datos_ap['interruptor_num']} en el alimentador {datos_ap['alimentador']} con resultado exitoso."})
if h_vcierre.strip(): eventos_para_ordenar.append({"hora": h_vcierre.strip(), "ubicacion": datos_vec["ser"], "descripcion": f"Recierre automático del interruptor {datos_vec['interruptor_num']} en el alimentador {datos_vec['alimentador']} con resultado exitoso."})
if h_rep.strip(): eventos_para_ordenar.append({"hora": h_rep.strip(), "ubicacion": "CCM", "descripcion": f"Se comunica al supervisor de PCO {sup_pco_val}.\n\nSe reporta en el grupo de WhatsApp de CCM_SUB_CAT de SYC."})
if h_env_st.strip(): eventos_para_ordenar.append({"hora": h_env_st.strip(), "ubicacion": "CCM", "descripcion": f"Personal de Subestaciones, {per_sub_val}; realizar inspección de las celdas DC: {datos_ap['alimentador_ser']} (ST {st_ap}) y {datos_vec['alimentador_ser']} (ST {st_vec}).\n\nPersonal de Catenarias, {per_cat_val}; realizar inspección de la {zona_manual} de vía principal (ST {st_zn})."})
if h_foto_disp.strip(): eventos_para_ordenar.append({"hora": h_foto_disp.strip(), "ubicacion": datos_ap["ser"], "descripcion": f"El técnico de Subestaciones, {per_sub_val}; informa que el relé Sitras PRO del alimentador {datos_ap['alimentador']}, registró:\n\n· “{f_disp_fin}” con el valor de {corriente_val} A\n\nReporta que se encuentra operativo sin alarmas presentes y en servicio."})
if h_foto_vec.strip(): eventos_para_ordenar.append({"hora": h_foto_vec.strip(), "ubicacion": datos_vec["ser"], "descripcion": f"El técnico de Subestaciones, {per_sub_val}; informa que el relé Sitras PRO del alimentador {datos_vec['alimentador']} registró:\n\n· “Arrastre desde SSEE colateral activo”\n\nReporta que se encuentra operativo sin alarmas presentes y en servicio."})
if h_cat.strip(): eventos_para_ordenar.append({"hora": h_cat.strip(), "ubicacion": f"{zona_manual}\nVía principal", "descripcion": f"El técnico de Catenarias, {per_cat_val}; informa que realizo inspección visual de la línea aérea de contacto en la {zona_manual} y reporta que no se encontró observaciones."})

cronologia_ordenada = sorted(eventos_para_ordenar, key=lambda x: str(x["hora"]))

context = {
    "interruptor_aperturado": datos_ap["interruptor"], "alimentador_ser_aperturado": datos_ap["alimentador_ser"], "ser_aperturado": datos_ap["ser"], "alimentador_aperturado": datos_ap["alimentador"], "alimentador_aperturado_num": datos_ap["interruptor_num"],
    "interruptor_vecino": datos_vec["interruptor"], "alimentador_ser_vecino": datos_vec["alimentador_ser"], "ser_vecino": datos_vec["ser"], "alimentador_vecino": datos_vec["alimentador"], "alimentador_vecino_num": datos_vec["interruptor_num"],
    "funcion_disparo_inicial": f_disp_ini, "funcion_disparo_final": f_disp_fin, "funcion_disparo_vecina_inicial": f_disp_vec_ini, "funcion_disparo_vecina_final": f_disp_vec_fin,
    "st_aperturado": st_ap, "st_vecino": st_vec, "st_zona": st_zn, "corriente": corriente_val,
    "fecha": fecha_val, "dia": dia_val, "tiempo_entre_trenes": headway, "condicion_senales": condicion, "operacion": operacion_val, "zona": zona_manual,
    "sup_pco": sup_pco_val, "per_sub": per_sub_val, "per_cat": per_cat_val
}

# =========================================================
# PANEL DERECHO: RENDERIZADO HÍBRIDO (DOCXTPL + PYTHON-DOCX)
# =========================================================
with col_preview:
    st.header("📄 Vista Previa Real del Documento")

    if plantilla_doc is not None:
        try:
            doc = DocxTemplate(plantilla_doc)
            
            # 1. Inyección de la imagen del anexo
            if "anexo_sitras_file" in st.session_state and st.session_state["anexo_sitras_file"] is not None:
                context["anexo_sitras"] = InlineImage(doc, st.session_state["anexo_sitras_file"], width=Mm(165))
            else:
                context["anexo_sitras"] = ""

            doc.render(context)
            
            # 2. Inyección de la tabla de cronología (HORA)
            tabla_cronologia = None
            for table in doc.docx.tables:
                if len(table.rows) > 0 and "HORA" in table.rows[0].cells[0].text.upper():
                    tabla_cronologia = table
                    break
            
            if tabla_cronologia is not None:
                for evento in cronologia_ordenada:
                    fila = tabla_cronologia.add_row()
                    fila.cells[0].text = str(evento["hora"])
                    fila.cells[1].text = str(evento["ubicacion"])
                    fila.cells[2].text = str(evento["descripcion"])
            
            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            docx_bytes = buffer.getvalue()
            docx_b64 = base64.b64encode(docx_bytes).decode("utf-8")

            viewer_html = f"""
            <div id="document-container" style="background-color: #525659; padding: 15px; height: 740px; overflow-y: auto; border-radius: 6px;"></div>
            <script src="https://unpkg.com/jszip/dist/jszip.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/docx-preview@0.1.15/dist/docx-preview.min.js"></script>
            <script>
                var base64Data = "{docx_b64}";
                var byteCharacters = atob(base64Data);
                var byteNumbers = new Array(byteCharacters.length);
                for (var i = 0; i < byteCharacters.length; i++) {{ byteNumbers[i] = byteCharacters.charCodeAt(i); }}
                var blob = new Blob([new Uint8Array(byteNumbers)], {{type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}});
                docx.renderAsync(blob, document.getElementById("document-container")).catch(e => console.error(e));
            </script>
            """
            components.html(viewer_html, height=760, scrolling=False)

            st.download_button(
                label="📥 Descargar Informe Completo (.docx)",
                data=buffer,
                file_name=f"Informe_Disparo_{datos_ap['ser']}_{context['fecha'].replace('/', '-')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error al compilar la plantilla Word: {e}")
    else:
        st.warning("Coloca un archivo `plantilla_base.docx` en el repositorio o súbelo en el formulario para visualizarlo.")