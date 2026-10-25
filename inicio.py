import base64
import io
import streamlit as st
import numpy as np
from PIL import Image
from openai import OpenAI
from streamlit_drawable_canvas import st_canvas


# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

st.set_page_config(
    page_title="Atelier | Laboratorio de Arte",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# ESTADO DE SESIÓN
# =========================================================

if "artwork_bytes" not in st.session_state:
    st.session_state.artwork_bytes = None

if "last_style" not in st.session_state:
    st.session_state.last_style = ""

if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""


# =========================================================
# ESTILOS VISUALES
# =========================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=IM+Fell+English&display=swap');

    :root {
        --cream: #f4eddf;
        --paper: #fffaf0;
        --ink: #35271d;
        --gold: #ad8746;
        --gold-light: #d9bd80;
        --wine: #6f3036;
        --olive: #536344;
    }

    .stApp {
        background-color: var(--cream);
        background-image:
            radial-gradient(
                ellipse at 50% 0%,
                rgba(255,255,255,0.85),
                transparent 65%
            );
        color: var(--ink);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stToolbar"] {
        visibility: hidden;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    html, body, [class*="css"] {
        font-family: 'Cormorant Garamond', Georgia, serif;
        color: var(--ink);
    }

    h1, h2, h3 {
        font-family: 'IM Fell English', Georgia, serif !important;
        color: var(--ink) !important;
        font-weight: 400 !important;
    }

    p, label, span {
        color: var(--ink);
    }

    .atelier-header {
        text-align: center;
        padding: 30px 15px 25px 15px;
        margin-bottom: 25px;
        border-top: 2px solid var(--gold);
        border-bottom: 1px solid var(--gold);
        position: relative;
    }

    .atelier-eyebrow {
        font-family: 'Cormorant Garamond', serif;
        font-size: 13px;
        letter-spacing: 5px;
        text-transform: uppercase;
        color: var(--wine);
        margin-bottom: 12px;
    }

    .atelier-title {
        font-family: 'IM Fell English', Georgia, serif;
        font-size: clamp(36px, 6vw, 66px);
        line-height: 1.05;
        color: #4b3024;
        letter-spacing: 1px;
    }

    .atelier-subtitle {
        font-size: 19px;
        font-style: italic;
        color: #78644c;
        margin-top: 14px;
    }

    .ornament {
        color: var(--gold);
        font-size: 25px;
        letter-spacing: 8px;
        margin: 8px 0;
    }

    .section-kicker {
        font-size: 12px;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: var(--wine);
        font-weight: 700;
        margin-bottom: 5px;
    }

    .section-title {
        font-family: 'IM Fell English', Georgia, serif;
        font-size: 30px;
        color: #493225;
        margin-bottom: 8px;
    }

    .section-description {
        font-size: 17px;
        color: #796753;
        margin-bottom: 18px;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 250, 240, 0.86);
        border: 1px solid #d9c7a6 !important;
        border-radius: 4px !important;
        box-shadow: 0 5px 18px rgba(73, 50, 37, 0.055);
    }

    [data-testid="stVerticalBlockBorderWrapper"] > div {
        border-radius: 4px;
    }

    .card-heading {
        font-family: 'IM Fell English', Georgia, serif;
        font-size: 24px;
        color: #51382a;
        margin-bottom: 5px;
    }

    .card-caption {
        color: #88745a;
        font-size: 15px;
        font-style: italic;
        margin-bottom: 15px;
    }

    .stButton > button {
        background: #6f3036;
        color: #fff8e9;
        border: 1px solid #6f3036;
        border-radius: 2px;
        padding: 11px 18px;
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: 18px;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    .stButton > button p {
        color: inherit !important;
    }

    .stButton > button:hover {
        background: #8a4548;
        color: white;
        border-color: #8a4548;
        box-shadow: 0 4px 12px rgba(111, 48, 54, 0.2);
    }

    .stTextInput input,
    .stTextArea textarea {
        background: #fffdf7;
        border: 1px solid #cdbb98;
        border-radius: 2px;
        color: #35271d;
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: 17px;
    }

    [data-testid="stWidgetLabel"] p {
        color: #594332 !important;
        font-size: 16px;
    }

    .result-frame {
        background: #fffaf0;
        border: 1px solid var(--gold);
        padding: 10px;
        box-shadow: 0 6px 22px rgba(53, 39, 29, 0.12);
    }

    .result-caption {
        text-align: center;
        font-family: 'IM Fell English', Georgia, serif;
        color: #755a39;
        font-size: 21px;
        font-style: italic;
        margin-top: 12px;
    }

    .museum-label {
        border-top: 1px solid #d8c7a5;
        margin-top: 22px;
        padding-top: 13px;
        text-align: center;
        color: #897657;
        font-size: 13px;
        letter-spacing: 3px;
        text-transform: uppercase;
    }

    [data-testid="stAlert"] {
        border-radius: 3px;
    }

    /* Opciones de estilo */

    div[role="radiogroup"] {
        gap: 8px;
    }

    div[role="radiogroup"] label {
        background: #fffaf0;
        border: 1px solid #d9c7a6;
        border-radius: 3px;
        padding: 8px 12px;
    }

    div[role="radiogroup"] label:hover {
        border-color: #ad8746;
    }

    /* Ocultar elementos de navegación lateral */

    [data-testid="stSidebar"] {
        display: none;
    }

    @media (max-width: 700px) {
        .atelier-header {
            padding: 20px 5px;
        }

        .atelier-eyebrow {
            letter-spacing: 2px;
        }

        .atelier-subtitle {
            font-size: 17px;
        }

        .section-title {
            font-size: 26px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# ENCABEZADO DEL ATELIER
# =========================================================

st.markdown(
    """
    <div class="atelier-header">
        <div class="atelier-eyebrow">
            Estudio de creación artística
        </div>

        <div class="atelier-title">
            Atelier de las Musas
        </div>

        <div class="ornament">❦ ✧ ❦</div>

        <div class="atelier-subtitle">
            Todo gran cuadro comienza con un primer trazo.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# INTRODUCCIÓN
# =========================================================

st.markdown(
    """
    <div style="text-align:center; max-width:760px;
                margin:0 auto 28px auto;">
        <div class="section-kicker">Tu imaginación, nuestra paleta</div>
        <div class="section-title">Crea una obra a tu manera</div>
        <div class="section-description">
            Dibuja una idea, escoge una corriente artística y deja
            que la inteligencia artificial la transforme en una
            obra inspirada en la historia del arte.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# TARJETA 1: DIBUJO
# =========================================================

col_canvas, col_options = st.columns([1.08, 0.92], gap="large")

with col_canvas:
    with st.container(border=True):
        st.markdown(
            """
            <div class="section-kicker">01 — El boceto</div>
            <div class="card-heading">El primer trazo</div>
            <div class="card-caption">
                No necesitas dibujar a la perfección.
                La imaginación es suficiente.
            </div>
            """,
            unsafe_allow_html=True
        )

        stroke_width = st.slider(
            "Grosor del pincel",
            min_value=1,
            max_value=20,
            value=4
        )

        stroke_color = st.color_picker(
            "Color del trazo",
            value="#35271D"
        )

        canvas_result = st_canvas(
            fill_color="rgba(173, 135, 70, 0.10)",
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            background_color="#FFFCF5",
            height=340,
            width=460,
            drawing_mode="freedraw",
            key="atelier_canvas",
            display_toolbar=True,
            update_streamlit=True
        )

        st.caption(
            "Puedes usar las herramientas del lienzo para dibujar "
            "y borrar tus trazos."
        )


# =========================================================
# MOVIMIENTOS ARTÍSTICOS
# =========================================================

ART_STYLES = {
    "Renacimiento": {
        "description": "Armonía, perspectiva y belleza clásica.",
        "prompt": (
            "Renacimiento europeo: composición equilibrada, "
            "perspectiva lineal precisa, anatomía estudiada, "
            "volúmenes modelados con delicados claroscuros, "
            "pigmentos tradicionales, ambiente clásico y "
            "acabado de pintura al óleo de museo."
        )
    },
    "Romanticismo": {
        "description": "Emoción, naturaleza y dramatismo.",
        "prompt": (
            "Romanticismo del siglo XIX: emoción intensa, "
            "naturaleza sublime, atmósfera dramática, "
            "contrastes de luz, cielos expresivos, pincelada "
            "pictórica y paleta evocadora."
        )
    },
    "Cubismo": {
        "description": "Geometría, planos y perspectivas múltiples.",
        "prompt": (
            "Cubismo: descomposición geométrica de las formas, "
            "múltiples perspectivas simultáneas, planos "
            "fragmentados, composición estructural y paleta "
            "artística coherente. El sujeto original debe "
            "seguir siendo reconocible."
        )
    },
    "Puntillismo": {
        "description": "Miles de puntos construyen la imagen.",
        "prompt": (
            "Puntillismo: construir toda la imagen mediante "
            "pequeños puntos de colores diferenciados, "
            "mezcla óptica, luz vibrante, gran precisión "
            "y una composición pictórica rica en detalles."
        )
    },
    "Impresionismo": {
        "description": "Luz cambiante y pinceladas vivas.",
        "prompt": (
            "Impresionismo: pinceladas visibles y sueltas, "
            "luz natural, colores luminosos, atmósfera "
            "fugaz, sombras coloreadas y sensación de "
            "una escena capturada en un instante."
        )
    },
    "Barroco": {
        "description": "Contrastes intensos y teatralidad.",
        "prompt": (
            "Barroco europeo: claroscuro intenso, iluminación "
            "teatral, composición dinámica, sombras profundas, "
            "riqueza de texturas, colores profundos y acabado "
            "de pintura al óleo."
        )
    },
    "Surrealismo": {
        "description": "Sueños, símbolos y mundos inesperados.",
        "prompt": (
            "Surrealismo: atmósfera onírica, asociaciones "
            "inesperadas, detalles imaginativos, espacios "
            "sugerentes y apariencia de sueño. Mantener "
            "como referencia el sujeto del boceto."
        )
    },
    "Art Nouveau": {
        "description": "Líneas orgánicas y ornamentos elegantes.",
        "prompt": (
            "Art Nouveau: líneas curvas y fluidas, motivos "
            "botánicos, composición ornamental, contornos "
            "elegantes, detalles decorativos y paleta "
            "sofisticada inspirada en el arte de finales "
            "del siglo XIX."
        )
    },
    "Acuarela": {
        "description": "Pigmentos transparentes y suaves.",
        "prompt": (
            "Pintura en acuarela: pigmentos translúcidos, "
            "lavados de color, bordes suaves, transparencias, "
            "textura de papel artístico y una composición "
            "delicada hecha a mano."
        )
    }
}


with col_options:
    with st.container(border=True):
        st.markdown(
            """
            <div class="section-kicker">02 — La inspiración</div>
            <div class="card-heading">Escoge tu movimiento</div>
            <div class="card-caption">
                Cada corriente cuenta una historia diferente.
            </div>
            """,
            unsafe_allow_html=True
        )

        selected_style = st.radio(
            "¿Qué lenguaje artístico tendrá tu obra?",
            options=list(ART_STYLES.keys()),
            index=0,
            label_visibility="collapsed"
        )

        st.markdown(
            f"""
            <div style="
                background:#f4eddf;
                border-left:3px solid #ad8746;
                padding:16px;
                margin:12px 0 18px 0;
            ">
                <div style="
                    color:#6f3036;
                    font-size:12px;
                    letter-spacing:2px;
                    text-transform:uppercase;
                ">
                    Movimiento seleccionado
                </div>
                <div style="
                    font-family:'IM Fell English',Georgia,serif;
                    font-size:27px;
                    color:#493225;
                    margin:6px 0;
                ">
                    {selected_style}
                </div>
                <div style="
                    font-size:16px;
                    color:#796753;
                    font-style:italic;
                ">
                    {ART_STYLES[selected_style]["description"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        extra_instructions = st.text_area(
            "Detalles opcionales para la obra",
            placeholder=(
                "Ej.: una paleta azul y dorada, un jardín al "
                "atardecer, una atmósfera misteriosa..."
            ),
            height=110
        )

        st.caption(
            "La IA utilizará tu dibujo como referencia y conservará "
            "su idea principal siempre que sea posible."
        )


# =========================================================
# TARJETA 3: CREAR OBRA
# =========================================================

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

with st.container(border=True):
    st.markdown(
        """
        <div style="text-align:center; padding:8px 8px 2px 8px;">
            <div class="section-kicker">03 — La transformación</div>
            <div class="section-title">Dale vida a tu boceto</div>
            <div class="section-description">
                Tu dibujo será reinterpretado como una obra artística.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    api_key = st.text_input(
        "Clave de API de OpenAI",
        type="password",
        placeholder="Introduce tu API key para generar la imagen"
    )

    generate_button = st.button(
        "✦ Transformar en obra de arte ✦",
        use_container_width=True
    )


# =========================================================
# GENERACIÓN DE IMAGEN
# =========================================================

if generate_button:

    if not api_key.strip():
        st.warning(
            "Introduce tu API key de OpenAI antes de generar la obra."
        )

    elif canvas_result.image_data is None:
        st.warning(
            "Primero dibuja algo en el lienzo."
        )

    else:
        canvas_objects = (
            canvas_result.json_data.get("objects", [])
            if canvas_result.json_data
            else []
        )

        if len(canvas_objects) == 0:
            st.warning(
                "El lienzo parece estar vacío. Haz al menos un trazo "
                "antes de continuar."
            )

        else:
            try:
                with st.spinner(
                    "El atelier está preparando tus pigmentos "
                    "y pintando la obra..."
                ):
                    # Convertir el lienzo a una imagen PNG.
                    canvas_array = np.array(
                        canvas_result.image_data
                    ).astype("uint8")

                    sketch_image = Image.fromarray(
                        canvas_array
                    ).convert("RGB")

                    image_buffer = io.BytesIO()
                    sketch_image.save(
                        image_buffer,
                        format="PNG"
                    )

                    image_bytes = image_buffer.getvalue()

                    style_prompt = ART_STYLES[selected_style]["prompt"]

                    prompt = f"""
                    Transforma la imagen de referencia dibujada por
                    el usuario en una obra de arte terminada.

                    MOVIMIENTO ARTÍSTICO ELEGIDO:
                    {selected_style}

                    CARACTERÍSTICAS VISUALES DEL MOVIMIENTO:
                    {style_prompt}

                    INSTRUCCIONES IMPORTANTES:
                    - Utiliza el boceto proporcionado como referencia
                      principal del contenido.
                    - Conserva el sujeto, la idea y la composición
                      general del dibujo tanto como sea posible.
                    - Interpreta las líneas simples y conviértelas en
                      una imagen artística completa y coherente.
                    - Aplica las técnicas, texturas, colores,
                      iluminación y composición del movimiento
                      artístico elegido.
                    - Añade detalles visuales apropiados cuando
                      ayuden a desarrollar la idea original.
                    - El resultado debe parecer una obra de arte
                      cuidadosamente creada, no un filtro aplicado
                      sobre el boceto.
                    - No incluyas textos, letras, marcas de agua,
                      interfaces ni marcos de aplicación.
                    - Presenta una sola obra terminada, con una
                      composición clara y visualmente atractiva.

                    INSTRUCCIONES ADICIONALES DEL USUARIO:
                    {extra_instructions.strip() or
                     "Sin instrucciones adicionales."}
                    """

                    client = OpenAI(
                        api_key=api_key.strip()
                    )

                    result = client.images.edit(
                        model="gpt-image-2.5-sunburst",
                        image=(
                            "boceto.png",
                            image_bytes,
                            "image/png"
                        ),
                        prompt=prompt,
                        size="1024x1024",
                        quality="high",
                        output_format="png"
                    )

                    if not result.data or not result.data[0].b64_json:
                        raise RuntimeError(
                            "La API no devolvió una imagen."
                        )

                    generated_bytes = base64.b64decode(
                        result.data[0].b64_json
                    )

                    # Guardar el resultado en la sesión.
                    st.session_state.artwork_bytes = generated_bytes
                    st.session_state.last_style = selected_style
                    st.session_state.last_prompt = prompt

            except Exception as error:
                st.error(
                    "No fue posible generar la obra. "
                    "Revisa tu clave, tu conexión y el acceso "
                    "a la API de generación de imágenes."
                )
                st.code(str(error))


# =========================================================
# MOSTRAR OBRA GENERADA
# =========================================================

if st.session_state.artwork_bytes:
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style="text-align:center; margin-bottom:20px;">
            <div class="section-kicker">La obra está terminada</div>
            <div class="section-title">Tu creación artística</div>
            <div class="section-description">
                Una idea, reinterpretada a través de la historia del arte.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.container(border=True):
        artwork = Image.open(
            io.BytesIO(st.session_state.artwork_bytes)
        ).convert("RGB")

        st.image(
            artwork,
            use_container_width=True
        )

        st.markdown(
            f"""
            <div class="result-caption">
                {st.session_state.last_style}
            </div>
            <div class="museum-label">
                Atelier de las Musas · Obra creada con inteligencia artificial
            </div>
            """,
            unsafe_allow_html=True
        )

        st.download_button(
            label="↓ Descargar mi obra en PNG",
            data=st.session_state.artwork_bytes,
            file_name=(
                "obra_"
                + st.session_state.last_style.lower().replace(" ", "_")
                + ".png"
            ),
            mime="image/png",
            use_container_width=True
        )


# =========================================================
# PIE DE PÁGINA
# =========================================================

st.markdown(
    """
    <div style="
        text-align:center;
        margin-top:38px;
        padding:20px 10px;
        border-top:1px solid #d9c7a6;
        color:#897657;
    ">
        <div style="
            font-family:'IM Fell English',Georgia,serif;
            font-size:22px;
            font-style:italic;
        ">
            Ars longa, vita brevis
        </div>
        <div style="
            font-size:12px;
            letter-spacing:3px;
            margin-top:8px;
        ">
            ATELIER DE LAS MUSAS · ESTUDIO DE ARTE
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
