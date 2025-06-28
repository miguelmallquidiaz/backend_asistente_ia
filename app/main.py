from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
import os
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

atencion_alumno_utp = {
    "red_WiFi": {"contraseña": "Aprende+"},
    "accesos": {
        "portal": "https://portal.utp.edu.pe",
        "class": "https://class.utp.edu.pe",
        "correo": "https://office.com (usuario: codigodealumno@utp.edu.pe)"
    },
    "emision_carnet": {
        "costo": "S/ 30.00",
        "fecha_limite": "27 junio 2025",
        "info_url": "https://info.utp.edu.pe/articulo/KA-01805"
    },
    "contacto": {
        "telefono_lima": "(01) 315 9600",
        "telefono_provincia": "0801 19 600",
        "whatsapp": "https://bit.ly/contacto_SAE"
    },
    "problemas_comunes": {
        "correo_error_toomany": "Si ves el mensaje 'Too Many Requests' al entrar al correo, solo actualiza la página (Ctrl+R) o cierra la pestaña y vuelve a ingresar.",
        "class_no_carga": "Si Class UTP no carga, intenta cambiar de navegador o borrar caché. También revisa si otros sitios cargan normalmente.",
        "wifi_no_funciona": "Verifica que estás conectado a la red correcta y que la contraseña es 'Aprende+'. Si no funciona, reinicia el dispositivo o consulta en soporte.",
        "no_ingresa_portal": "Verifica que ingresas a https://portal.utp.edu.pe desde Chrome o Edge actualizado. Si persiste, limpia cookies o intenta en modo incógnito.",
        "app_utp_caida": "Si la aplicación de la UTP está caída, esto suele deberse a una alta cantidad de solicitudes de ingreso no previstas por el sistema. Este tipo de fallas es común durante las primeras semanas del ciclo, pero suele estabilizarse progresivamente."
    }
}

temas_indexados = {
    "carnet": ["emision_carnet"],
    "portal": ["accesos"],
    "wifi": ["red_WiFi"],
    "contacto": ["contacto"],
    "comunicación": ["contacto"],
    "telefonos": ["contacto"],
    "soporte": ["contacto"],
    "ayuda": ["contacto"],
    "comunicarme": ["contacto"],
    "comunicar": ["contacto"],
    "atención": ["contacto"],
    "caida": ["problemas_comunes"],
    "aplicación": ["problemas_comunes"],
    "app": ["problemas_comunes"],
    "demanda": ["problemas_comunes"],
    "solicitudes": ["problemas_comunes"],
    "inicio": ["problemas_comunes"],
    "primeras": ["problemas_comunes"],
    "semanas": ["problemas_comunes"]
}

def recuperar_contexto(pregunta: str) -> Dict:
    tokens = set(pregunta.lower().split())
    for clave, temas in temas_indexados.items():
        if clave in tokens:
            return {tema: atencion_alumno_utp.get(tema) for tema in temas if tema in atencion_alumno_utp}
    return {"mensaje": "No se encontró información relevante."}

def generar_respuesta(pregunta: str) -> str:
    contexto = recuperar_contexto(pregunta)
    prompt = f"""
    Tu nombre es AIRA eres una asistente de soporte de la universidad UTP del Perú, brindar una atención poner emotes y reducir el texto.
    Usa solo la siguiente información contextual: 
    Contexto: {contexto}

    Pregunta: {pregunta}

    Respuesta:
    """
    respuesta = model.generate_content(prompt)
    return respuesta.text.strip() if hasattr(respuesta, "text") else "Sin respuesta generada."

app = FastAPI()

class PreguntaInput(BaseModel):
    pregunta: str

@app.get("/")
async def root():
    return {"message": "Proyecto API con FastAPI, ingresar a la uri /docs"}

@app.post("/respuesta")
def responder(data: PreguntaInput):
    return {"respuesta": generar_respuesta(data.pregunta)}

origins = [
    "https://9000-firebase-app-1750283637671.cluster-uf6urqn4lned4spwk4xorq6bpo.cloudworkstations.dev"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Solo tu dominio Angular
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)