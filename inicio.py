
import base64
import io
import streamlit as st
import numpy as np
from PIL import Image
from openai import OpenAI
from streamlit_drawable_canvas import st_canvas


# --------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# --------------------------------------------------

st.set_page_config(
    page_title="Atelier de las Musas",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# --------------------------------------------------
# ESTILOS VISUALES
# --------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,500;0,600;1,400&display=swap');

.stApp {
    background:
        radial-gradient(ellipse at top, #383025 0%, #201c18 48%, #151310 100%);
    color: #eee3cf;
}

header[data-testid="stHeader"] {
    background: transparent;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

section[data-testid="stSidebar"] {
    display: none;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* TÍTULO PRINCIPAL */

.atelier-title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: clamp(42px, 6vw, 68px);
    font-weight: 500;
    color: #e7d0a0;
    text-align: center;
    letter-spacing: 3px;
    line-height: 1.1;
    margin-top: 8px;
    margin-bottom: 8px;
    text-shadow: 0 2px 15px rgba(0, 0, 0, 0.35);
}

.ornament {
    font-size: 27px;
    color: #bd9b60;
    text-align: center;
    margin: 8px 0 12px 0;
    letter-spacing: 8px;
}

.atelier-subtitle {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 17px;
    font-style: italic;
    color: #d5c4a7;
    text-align: center;
    margin-bottom: 35px;
}

/* ENCABEZADOS */

h1, h2, h3 {
    font-family: 'Cormorant Garamond', Georgia, serif !important;
    color: #e7d0a0 !important;
}

h2 {
    font-size: 30px !important;
}

h3 {
    font-size: 24px !important;
}

/* TEXTO GENERAL */

p, label, .stMarkdown {
    color: #eee3cf;
}

div[data-testid="stMarkdownContainer"] p {
    color: #eee3cf;
}

/* TARJETAS */

.panel {
    background: rgba(50, 43, 34, 0.82);
    border: 1px solid rgba(190, 158, 100, 0.45);
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.18);
}

.panel-title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 27px;
    color: #e7d0a0;
    margin-bottom: 6px;
}

/* BOTONES */

.stButton > button,
.stDownloadButton > button {
    background: linear-gradient(135deg, #b99a65, #947343);
    color: #211b13;
    border: 1px solid #d8bd88;
    border-radius: 9px;
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 16px;
    font-weight: 600;
    padding: 0.65rem 1.2rem;
    transition: all 0.2s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #d6bc88, #b99a65);
    color: #17120c;
    border-color: #ead6ad;
}

/* CAMPOS DE TEXTO */

.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] {
    background-color: #302920;
    color: #f4e8d2;
    border-color: #9c8051;
    border-radius: 8px;
}

/* OPCIONES DE ESTILO */

div[role="radiogroup"] label {
    color: #eee3cf !important;
}

/* LIENZO */

div[data-testid="stCanvas"] {
    border: 1px solid #b99a65;
    border-radius: 8px;
    overflow: hidden;
}

/* SEPARADORES */

hr {
    border-color: rgba(190, 158, 100, 0.35);
}

/* AVISOS */

div[data-testid="stAlert"] {
    border-radius: 10px;
}

/* PIE DE PÁGINA */

.footer-art {
    font-family: 'Playfair Display', Georgia, serif;
    color: #bca98a;
    font-size: 14px;
    text-align: center;
    margin-top: 40px;
    padding-top: 18px;
    border-top: 1px solid rgba(190, 158, 100, 0.3);
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# ENCABEZADO
# --------------------------------------------------

st.markdown("""
<div class="atelier-title">Atelier de las Musas</div>
<div class="ornament">❦ ✧ ❦</div>
<div class="atelier-subtitle">
    Todo gran cuadro comienza con un primer trazo.
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# INTRODUCCIÓN
# --------------------------------------------------

st.markdown("""
<div style="text-align:center; max-width:760px; margin:0 auto 30px auto;">
    <p style="font-size:17px; line-height:1.8; color:#d9cbb4;">
        Bienvenido a tu taller de creación artística. Dibuja una idea,
        elige una corriente pictórica y permite que la inteligencia
        artificial transforme tu boceto en una obra de arte.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")


# --------------------------------------------------
# ESTILOS ARTÍSTICOS
# --------------------------------------------------

ESTILOS = {
    "Renacimiento": (
        "Transforma el boceto en una pintura inspirada en el Renacimiento. "
        "Utiliza composición equilibrada, anatomía estudiada, perspectiva "
        "lineal, iluminación natural, detalles minuciosos y una paleta "
        "de tonos tierra, ocres y dorados. Apariencia de pintura al óleo "
        "clásica de los siglos XV y XVI."
    ),
    "Romanticismo": (
        "Transforma el boceto en una pintura romántica del siglo XIX. "
        "Emplea una atmósfera emotiva, paisajes dramáticos, contrastes "
        "de luz, colores intensos y una sensación de grandeza, misterio "
        "y emoción humana."
    ),
    "Cubismo": (
        "Reinterpreta el boceto mediante el cubismo. Descompón las formas "
        "en figuras geométricas, planos fragmentados y perspectivas "
        "simultáneas. Usa una composición estructurada y una paleta "
        "artística coherente."
    ),
    "Puntillismo": (
        "Convierte el boceto en una obra puntillista. Construye las formas "
        "mediante pequeños puntos de color cuidadosamente distribuidos, "
        "con mezclas ópticas, luminosidad y una composición equilibrada."
    ),
    "Impresionismo": (
        "Transforma el boceto en una pintura impresionista. Utiliza "
        "pinceladas visibles y sueltas, luz cambiante, colores vibrantes, "
        "sombras cromáticas y una atmósfera espontánea."
    ),
    "Barroco": (
        "Convierte el boceto en una pintura barroca. Usa claroscuro "
        "dramático, iluminación teatral, sombras profundas, riqueza "
        "de texturas, movimiento y una composición intensa."
    ),
    "Surrealismo": (
        "Reinterpreta el boceto como una obra surrealista. Combina "
        "elementos reconocibles con escenas oníricas, asociaciones "
        "inesperadas, perspectivas imposibles y una atmósfera misteriosa."
    ),
    "Art Nouveau": (
        "Transforma el boceto en una obra inspirada en el Art Nouveau. "
        "Utiliza líneas orgánicas y sinuosas, motivos vegetales, detalles "
        "ornamentales, elegancia decorativa y colores armoniosos."
    ),
    "Acuarela": (
        "Convierte el boceto en una ilustración de acuarela. Emplea "
        "transparencias, pigmentos diluidos, bordes suaves, manchas "
        "espontáneas, textura de papel y una paleta delicada."
    )
}


# --------------------------------------------------
# DISTRIBUCIÓN PRINCIPAL
# --------------------------------------------------

col_dibujo, col_opciones = st.columns([1.15, 0.85], gap="large")


# --------------------------------------------------
# COLUMNA IZQUIERDA: LIENZO
# --------------------------------------------------

with col_dibujo:

    st.markdown("""
    <div class="panel-title">I. El primer trazo</div>
    <p style="color:#cbb99a;">
        Dibuja libremente en el lienzo. No necesitas ser un experto:
        tu imaginación es el punto de partida.
    </p>
    """, unsafe_allow_html=True)

    color_pincel = st.color_picker(
        "Color del pincel",
        value="#302820"
    )

    grosor_pincel = st.slider(
        "Grosor del pincel",
        min_value=1,
        max_value=30,
        value=5
    )

    fondo_lienzo = st.selectbox(
        "Fondo del lienzo",
        ["Marfil", "Blanco", "Negro"],
        index=0
    )

    colores_fondo = {
        "Marfil": "#F5EBD8",
        "Blanco": "#FFFFFF",
        "Negro": "#24211D"
    }

    lienzo = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=grosor_pincel,
        stroke_color=color_pincel,
        background_color=colores_fondo[fondo_lienzo],
        height=380,
        width=600,
        drawing_mode="freedraw",
        key="atelier_canvas",
        display_toolbar=True
    )

    st.caption(
        "Consejo: dibuja las formas principales y deja que el estilo "
        "artístico aporte los detalles."
    )


# --------------------------------------------------
# COLUMNA DERECHA: OPCIONES
# --------------------------------------------------

with col_opciones:

    st.markdown("""
    <div class="panel-title">II. El alma de la obra</div>
    <p style="color:#cbb99a;">
        Elige la corriente artística que dará vida a tu creación.
    </p>
    """, unsafe_allow_html=True)

    estilo_elegido = st.radio(
        "Corriente artística",
        options=list(ESTILOS.keys()),
        index=0
    )

    st.markdown(f"""
    <div class="panel">
        <div style="font-family:'Cormorant Garamond',serif;
                    font-size:23px;color:#e7d0a0;margin-bottom:8px;">
            {estilo_elegido}
        </div>
        <p style="font-size:14px;line-height:1.7;color:#d9cbb4;">
            {ESTILOS[estilo_elegido]}
        </p>
    </div>
    """, unsafe_allow_html=True)

    instrucciones = st.text_area(
        "Tu visión artística (opcional)",
        placeholder=(
            "Ejemplo: quiero un cielo dorado, flores alrededor "
            "y una atmósfera mágica..."
        ),
        height=120
    )

    st.markdown("""
    <p style="font-size:13px;color:#bca98a;">
        Puedes añadir colores, ambientes, objetos o detalles que
        quieras ver en la obra final.
    </p>
    """, unsafe_allow_html=True)


# --------------------------------------------------
# GENERACIÓN DE LA OBRA
# --------------------------------------------------

st.markdown("---")
st.markdown(
    '<div class="panel-title" style="text-align:center;">'
    'III. Dar vida a la obra</div>',
    unsafe_allow_html=True
)

st.markdown("""
<p style="text-align:center;color:#d9cbb4;">
    Cuando estés listo, convierte tu boceto en una creación artística.
</p>
""", unsafe_allow_html=True)

api_key = st.text_input(
    "Clave API de OpenAI",
    type="password",
    help="La clave se utiliza para realizar la generación de la imagen."
)

generar = st.button(
    "✧ Transformar mi boceto ✧",
    use_container_width=True
)


if generar:

    if not api_key.strip():
        st.error(
            "Introduce tu clave API de OpenAI para poder generar la obra."
        )
        st.stop()

    if lienzo.image_data is None:
        st.error("No se pudo leer el lienzo. Intenta dibujar de nuevo.")
        st.stop()

    imagen_array = lienzo.image_data

    if not np.any(imagen_array[:, :, 3] > 0):
        st.error("Primero debes dibujar algo en el lienzo.")
        st.stop()

    try:
        with st.spinner(
            "Las musas están trabajando en tu obra... "
            "Esto puede tardar un momento."
        ):

            # Convertir el lienzo a imagen PNG
            imagen_original = Image.fromarray(
                imagen_array.astype("uint8"),
                mode="RGBA"
            )

            buffer_original = io.BytesIO()
            imagen_original.save(buffer_original, format="PNG")
            buffer_original.seek(0)

            # Crear la instrucción artística
            prompt = f"""
            Usa la imagen proporcionada como boceto de referencia.
            Conserva la idea principal, la composición y los elementos
            reconocibles del dibujo original.

            Transforma el boceto en una obra de arte acabada.

            Estilo artístico seleccionado: {estilo_elegido}.

            Dirección artística:
            {ESTILOS[estilo_elegido]}

            Instrucciones adicionales del usuario:
            {instrucciones.strip() if instrucciones.strip() else
            "No hay instrucciones adicionales."}

            El resultado debe parecer una obra artística terminada,
            no una fotografía del dibujo ni una captura de pantalla.
            No incluyas texto, firmas, marcas de agua ni interfaces.
            """

            cliente = OpenAI(api_key=api_key.strip())

            # Enviar la imagen y solicitar la transformación
            respuesta = cliente.images.edit(
                model="gpt-image-1",
                image=("boceto.png", buffer_original, "image/png"),
                prompt=prompt,
                size="1024x1024"
            )

            imagen_b64 = respuesta.data[0].b64_json

            if not imagen_b64:
                st.error(
                    "La API no devolvió una imagen. Intenta de nuevo."
                )
                st.stop()

            imagen_bytes = base64.b64decode(imagen_b64)
            imagen_final = Image.open(
                io.BytesIO(imagen_bytes)
            ).convert("RGB")

            st.session_state["atelier_resultado"] = imagen_final
            st.session_state["atelier_estilo"] = estilo_elegido

    except Exception as error:
        st.error(
            "No se pudo generar la imagen. Revisa la clave API, "
            "la conexión, el acceso al modelo y la configuración "
            "de facturación de tu cuenta de OpenAI."
        )

        st.code(str(error))


# --------------------------------------------------
# MOSTRAR LA OBRA GENERADA
# --------------------------------------------------

if "atelier_resultado" in st.session_state:

    st.markdown("---")

    st.markdown("""
    <div class="panel-title" style="text-align:center;">
        ✧ Tu obra ha cobrado vida ✧
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f"<p style='text-align:center;color:#d9cbb4;'>"
        f"Estilo: {st.session_state['atelier_estilo']}"
        f"</p>",
        unsafe_allow_html=True
    )

    col_espacio_izq, col_resultado, col_espacio_der = st.columns(
        [0.5, 2, 0.5]
    )

    with col_resultado:
        st.image(
            st.session_state["atelier_resultado"],
            use_container_width=True
        )

        buffer_descarga = io.BytesIO()
        st.session_state["atelier_resultado"].save(
            buffer_descarga,
            format="PNG"
        )
        buffer_descarga.seek(0)

        st.download_button(
            label="⬇ Descargar mi obra",
            data=buffer_descarga.getvalue(),
            file_name="mi_obra_atelier.png",
            mime="image/png",
            use_container_width=True
        )


# --------------------------------------------------
# PIE DE PÁGINA
# --------------------------------------------------

st.markdown("""
<div class="footer-art">
    ❦ Atelier de las Musas ❦<br>
    <span style="font-size:12px;">
        El arte comienza con la imaginación.
    </span>
</div>
""", unsafe_allow_html=True)
