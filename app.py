import os
import streamlit as st
import base64
from openai import OpenAI

def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

st.set_page_config(page_title="Analisis de imagen", layout="centered", initial_sidebar_state="collapsed")

st.title("Análisis de Poligonaje")
ke = st.text_input('Ingresa tu Clave', type="password")

if ke:
    os.environ['OPENAI_API_KEY'] = ke

api_key = os.environ.get('OPENAI_API_KEY', '')

if api_key:
    client = OpenAI(api_key=api_key)

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    with st.expander("Image", expanded = True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

show_details = st.toggle("Pregunta algo específico sobre la imagen", value=False)

if show_details:
    additional_details = st.text_area(
        "Adiciona contexto de la imagen aqui:",
        disabled=not show_details
    )

analyze_button = st.button("Analiza la imagen", type="secondary")

if uploaded_file is not None and api_key and analyze_button:
    with st.spinner("Analizando ..."):
        base64_image = encode_image(uploaded_file)
        
        # Modificación principal: Prompt de validación y clasificación
        prompt_text = (
            "Evalúa la imagen. Determina si el modelo es 'Low poly', 'Mid poly', 'High poly' o 'No aplica'. "
            "Si pertenece a una de las tres categorías de poligonaje, explica técnicamente por qué y menciona el sector "
            "o industria en el que serviría. Si la imagen no aplica a ninguna de estas tres categorías, responde exclusivamente 'No aplica'."
        )
        
        if show_details and additional_details:
            prompt_text += (
                f"\n\nContexto adicional:\n{additional_details}"
            )
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    },
                ],
            }
        ]
        
        try:
            full_response = ""
            message_placeholder = st.empty()
            for completion in client.chat.completions.create(
                model="gpt-4o", messages=messages,   
                max_tokens=1200, stream=True
            ):
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        
        except Exception as e:
            st.error(f"Error detectado: {e}")
else:
    if not uploaded_file and analyze_button:
        st.warning("Please upload an image.")
    if not api_key and analyze_button:
        st.warning("Por favor ingresa tu API key.")
