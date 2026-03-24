#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime, timedelta

try:
    from supabase import create_client
    TIENE_SUPABASE = True
except Exception:
    create_client = None
    TIENE_SUPABASE = False


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ARCHIVO_DATOS = os.path.join(DATA_DIR, "vacas.json")
ARCHIVO_VACUNACION = os.path.join(DATA_DIR, "vacunacion.json")
ARCHIVO_CONFIG = os.path.join(DATA_DIR, "config.json")
ARCHIVO_SESION = os.path.join(DATA_DIR, "sesion.json")

TU_SUPABASE_URL = "https://zxdjjiuovpsnfdbkdaaq.supabase.co"
TU_SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp4ZGpqaXVvdnBzbmZkYmtkYWFxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM1MzkzNzgsImV4cCI6MjA4OTExNTM3OH0.tN04Yl7qFpw1Cmi94cKMGd77f8KrJiLfl8C7dZal1Qw"


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def asegurar_directorios():
    os.makedirs(DATA_DIR, exist_ok=True)


def cargar_json(ruta, default=None):
    if not os.path.exists(ruta):
        return default
    try:
        with open(ruta, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return default


def guardar_json(ruta, data):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False, cls=DateTimeEncoder)


def cargar_configuracion():
    config = cargar_json(ARCHIVO_CONFIG, default={}) or {}
    return {
        "supabase_url": config.get("supabase_url", TU_SUPABASE_URL),
        "supabase_key": config.get("supabase_key", TU_SUPABASE_KEY),
    }


def guardar_configuracion(config):
    actual = cargar_json(ARCHIVO_CONFIG, default={}) or {}
    actual.update(config)
    guardar_json(ARCHIVO_CONFIG, actual)
    return actual


def normalizar_fecha(valor):
    if not valor:
        return None
    texto = str(valor).strip()
    formatos = (
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
    )
    for formato in formatos:
        try:
            return datetime.strptime(texto, formato)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(texto.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return None


def peso_invalido(valor):
    if valor is None:
        return True
    texto = str(valor).strip().lower()
    if texto in ("", "-", "—", "sin peso", "none", "null", "no registrado"):
        return True
    try:
        float(texto.replace(",", "."))
        return False
    except ValueError:
        return True


def texto_relevante(valor):
    if valor is None:
        return ""
    texto = str(valor).strip()
    if texto.lower() in ("", "-", "—", "ninguna", "sin enfermedades", "ninguno", "no"):
        return ""
    return texto


class GestorDatos:
    def __init__(self):
        asegurar_directorios()
        self.vacas = cargar_json(ARCHIVO_DATOS, default={}) or {}
        self.vacunacion = cargar_json(ARCHIVO_VACUNACION, default={}) or {}
        for uid in self.vacas:
            self.vacas[uid].setdefault("historial", [])
            self.vacas[uid].setdefault("pesajes", [])

    def guardar(self):
        guardar_json(ARCHIVO_DATOS, self.vacas)
        guardar_json(ARCHIVO_VACUNACION, self.vacunacion)

    def reemplazar_vacas(self, vacas_remotas):
        self.vacas = vacas_remotas or {}
        for uid in self.vacas:
            self.vacas[uid].setdefault("historial", [])
            self.vacas[uid].setdefault("pesajes", [])
        self.guardar()

    def listar_vacas(self):
        return sorted(self.vacas.items(), key=lambda item: item[0])

    def obtener_vaca(self, uid):
        return self.vacas.get(uid.lower())

    def crear_vaca(self, uid, nombre, edad="", raza="", peso="", enfermedades="", vacunas=""):
        uid = uid.strip().lower()
        if not uid:
            raise ValueError("El UID es obligatorio.")
        if uid in self.vacas:
            raise ValueError("Ese UID ya existe.")
        self.vacas[uid] = {
            "nombre": nombre.strip() or f"Sin nombre {uid}",
            "edad": edad.strip() or "-",
            "raza": raza.strip() or "-",
            "peso": peso.strip() or "-",
            "enfermedades": enfermedades.strip() or "-",
            "vacunas": vacunas.strip() or "-",
            "historial": [f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Registro inicial"],
            "pesajes": [],
        }
        self.guardar()

    def actualizar_vaca(self, uid, **campos):
        vaca = self.obtener_vaca(uid)
        if not vaca:
            raise ValueError("La vaca no existe.")
        for clave in ("nombre", "edad", "raza", "peso", "enfermedades", "vacunas"):
            if clave in campos:
                vaca[clave] = str(campos[clave]).strip() or "-"
        self.guardar()

    def eliminar_vaca(self, uid):
        uid = uid.lower()
        if uid in self.vacas:
            del self.vacas[uid]
        if uid in self.vacunacion:
            del self.vacunacion[uid]
        self.guardar()

    def registrar_evento(self, uid, evento):
        vaca = self.obtener_vaca(uid)
        if not vaca:
            raise ValueError("La vaca no existe.")
        vaca.setdefault("historial", []).append(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {evento}"
        )
        self.guardar()

    def registrar_pesaje(self, uid, peso, fecha=None):
        vaca = self.obtener_vaca(uid)
        if not vaca:
            raise ValueError("La vaca no existe.")
        fecha_registro = (fecha or datetime.now()).strftime("%Y-%m-%d")
        peso_texto = str(peso).strip()
        vaca.setdefault("pesajes", []).append(
            {
                "fecha": fecha_registro,
                "peso": peso_texto,
                "creado_en": datetime.now().isoformat(),
            }
        )
        vaca["peso"] = peso_texto
        self.registrar_evento(uid, f"Pesaje registrado: {peso_texto} kg el {fecha_registro}")

    def agendar_vacuna(self, uid, vacuna, fecha_texto):
        vaca = self.obtener_vaca(uid)
        if not vaca:
            raise ValueError("La vaca no existe.")
        fecha = normalizar_fecha(fecha_texto)
        if not fecha:
            raise ValueError("Fecha inválida. Usa YYYY-MM-DD.")
        self.vacunacion.setdefault(uid.lower(), []).append(
            {
                "vacuna": vacuna.strip(),
                "fecha": fecha.strftime("%Y-%m-%d"),
                "aplicada": False,
                "creado_en": datetime.now().isoformat(),
            }
        )
        self.registrar_evento(uid, f"Vacuna agendada: {vacuna.strip()} para {fecha.strftime('%Y-%m-%d')}")

    def marcar_vacuna_aplicada(self, uid, indice):
        vacunas = self.vacunacion.get(uid.lower(), [])
        if indice < 0 or indice >= len(vacunas):
            raise ValueError("No se encontró la vacuna.")
        vacunas[indice]["aplicada"] = True
        vacunas[indice]["aplicada_en"] = datetime.now().strftime("%Y-%m-%d")
        self.registrar_evento(uid, f"Vacuna aplicada: {vacunas[indice].get('vacuna', 'Vacuna')}")

    def obtener_ultimo_evento(self, vaca):
        for item in reversed(vaca.get("historial", [])):
            posible_fecha = item.split(": ", 1)[0].strip() if ": " in item else item.strip()
            fecha = normalizar_fecha(posible_fecha)
            if fecha:
                return fecha
        return None

    def construir_alertas(self):
        hoy = datetime.now().date()
        limite_proximas = hoy + timedelta(days=15)
        alertas = []
        resumen = {
            "total_vacas": len(self.vacas),
            "urgentes": 0,
            "proximas": 0,
            "sin_peso": 0,
            "sin_movimiento": 0,
        }

        for uid, vaca in self.vacas.items():
            nombre = vaca.get("nombre", uid).strip() or uid
            if peso_invalido(vaca.get("peso")):
                resumen["sin_peso"] += 1
                alertas.append(
                    {
                        "nivel": "media",
                        "tipo": "peso",
                        "uid": uid,
                        "nombre": nombre,
                        "titulo": "Peso sin registrar",
                        "detalle": "Conviene cargar un peso para mejorar el seguimiento.",
                    }
                )

            ultimo_evento = self.obtener_ultimo_evento(vaca)
            if not ultimo_evento or (hoy - ultimo_evento.date()).days > 30:
                resumen["sin_movimiento"] += 1
                dias = (
                    "sin movimientos registrados"
                    if not ultimo_evento
                    else f"último movimiento hace {(hoy - ultimo_evento.date()).days} días"
                )
                alertas.append(
                    {
                        "nivel": "media",
                        "tipo": "movimiento",
                        "uid": uid,
                        "nombre": nombre,
                        "titulo": "Seguimiento atrasado",
                        "detalle": f"{dias}. Revisa control, pesaje o sanidad.",
                    }
                )

            enfermedad = texto_relevante(vaca.get("enfermedades"))
            if enfermedad:
                alertas.append(
                    {
                        "nivel": "baja",
                        "tipo": "sanidad",
                        "uid": uid,
                        "nombre": nombre,
                        "titulo": "Seguimiento sanitario activo",
                        "detalle": enfermedad,
                    }
                )

        for uid, vacunas in self.vacunacion.items():
            nombre = self.vacas.get(uid, {}).get("nombre", uid)
            for indice, vacuna in enumerate(vacunas):
                if vacuna.get("aplicada"):
                    continue
                fecha_programada = normalizar_fecha(vacuna.get("fecha"))
                nombre_vacuna = vacuna.get("vacuna", "Vacuna").strip() or "Vacuna"
                alerta = {
                    "nivel": "media",
                    "tipo": "vacuna",
                    "uid": uid,
                    "nombre": nombre,
                    "titulo": f"Vacuna pendiente: {nombre_vacuna}",
                    "detalle": "",
                    "fecha": vacuna.get("fecha", ""),
                    "vacuna_indice": indice,
                }
                if not fecha_programada or fecha_programada.date() < hoy:
                    alerta["nivel"] = "alta"
                    resumen["urgentes"] += 1
                    alerta["detalle"] = "Vacuna vencida o con fecha inválida."
                elif fecha_programada.date() <= limite_proximas:
                    resumen["proximas"] += 1
                    dias = (fecha_programada.date() - hoy).days
                    alerta["detalle"] = f"Se vence en {dias} días."
                else:
                    continue
                alertas.append(alerta)

        prioridad = {"alta": 0, "media": 1, "baja": 2}
        alertas.sort(
            key=lambda item: (
                prioridad.get(item["nivel"], 3),
                item.get("fecha") or "9999-99-99",
                item["nombre"].lower(),
            )
        )
        return resumen, alertas


class GestorSesion:
    def __init__(self):
        asegurar_directorios()
        self.sesion = cargar_json(ARCHIVO_SESION, default=None)

    def cargar(self):
        self.sesion = cargar_json(ARCHIVO_SESION, default=None)
        return self.sesion

    def guardar(self, sesion):
        data = dict(sesion)
        data["fecha_guardado"] = datetime.now().isoformat()
        guardar_json(ARCHIVO_SESION, data)
        self.sesion = data
        return data

    def limpiar(self):
        if os.path.exists(ARCHIVO_SESION):
            os.remove(ARCHIVO_SESION)
        self.sesion = None

    def crear_sesion_local(self, nombre="Usuario local"):
        sesion = {
            "modo": "local",
            "id": f"local_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "email": "usuario@local",
            "nombre": nombre.strip() or "Usuario local",
        }
        return self.guardar(sesion)


class GestorSupabase:
    def __init__(self, url=None, key=None):
        config = cargar_configuracion()
        self.url = url or config.get("supabase_url") or TU_SUPABASE_URL
        self.key = key or config.get("supabase_key") or TU_SUPABASE_KEY
        self.client = None
        self.usuario = None
        self.session = None
        self.conectado = False
        self.soporta_pesajes = True

    def disponible(self):
        return TIENE_SUPABASE and bool(self.key)

    def conectar(self):
        if not TIENE_SUPABASE:
            raise RuntimeError("Falta instalar supabase.")
        self.client = create_client(self.url, self.key)
        self.conectado = True
        return self.client

    def _error_columna_pesajes(self, error):
        texto = str(error).lower()
        return "pesajes" in texto and ("schema cache" in texto or "could not find" in texto or "column" in texto)

    def _payload_vaca(self, uid, datos, incluir_pesajes=True):
        if not self.usuario:
            raise RuntimeError("No hay usuario autenticado.")
        payload = {
            "uid": uid.lower(),
            "nombre": datos.get("nombre", ""),
            "edad": datos.get("edad", ""),
            "raza": datos.get("raza", ""),
            "peso": datos.get("peso", ""),
            "enfermedades": datos.get("enfermedades", ""),
            "vacunas": datos.get("vacunas", ""),
            "historial": json.dumps(datos.get("historial", []), ensure_ascii=False),
            "usuario_id": self.usuario["id"],
            "ultima_actualizacion": datetime.now().isoformat(),
        }
        if incluir_pesajes:
            payload["pesajes"] = json.dumps(datos.get("pesajes", []), ensure_ascii=False)
        return payload

    def registrar_usuario(self, email, password):
        client = self.client or self.conectar()
        response = client.auth.sign_up(
            {
                "email": email,
                "password": password,
                "options": {"email_redirect_to": "http://localhost:8080/auth/callback"},
            }
        )
        if not getattr(response, "user", None):
            raise RuntimeError("No se pudo completar el registro.")
        self.usuario = {
            "id": response.user.id,
            "email": response.user.email,
            "modo": "online",
            "email_confirmado": bool(getattr(response.user, "email_confirmed_at", None)),
        }
        return self.usuario

    def enviar_magic_link(self, email):
        client = self.client or self.conectar()
        client.auth.sign_in_with_otp(
            {
                "email": email,
                "options": {"email_redirect_to": "http://localhost:8080/auth/callback"},
            }
        )
        return True

    def verificar_magic_link(self, email, token):
        client = self.client or self.conectar()
        response = client.auth.verify_otp({"email": email, "token": token, "type": "magiclink"})
        if not getattr(response, "user", None):
            raise RuntimeError("Token inválido o expirado.")
        self.usuario = {
            "id": response.user.id,
            "email": response.user.email,
            "modo": "online",
            "email_confirmado": bool(getattr(response.user, "email_confirmed_at", None)),
        }
        if getattr(response, "session", None):
            self.session = {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
            }
        self.conectado = True
        return self.usuario

    def login_password(self, email, password):
        client = self.client or self.conectar()
        response = client.auth.sign_in_with_password({"email": email, "password": password})
        if not getattr(response, "user", None):
            raise RuntimeError("Credenciales inválidas.")
        self.usuario = {
            "id": response.user.id,
            "email": response.user.email,
            "nombre": response.user.email.split("@")[0],
            "modo": "online",
            "email_confirmado": bool(getattr(response.user, "email_confirmed_at", None)),
        }
        if getattr(response, "session", None):
            self.session = {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
            }
        self.conectado = True
        return self.usuario

    def restaurar_sesion(self, sesion):
        tokens = (sesion or {}).get("tokens") or (sesion or {}).get("supabase_tokens")
        if not tokens:
            return False
        client = self.client or self.conectar()
        try:
            client.auth.set_session(tokens["access_token"], tokens["refresh_token"])
            user_response = client.auth.get_user()
            if not getattr(user_response, "user", None):
                return False
            self.usuario = {
                "id": user_response.user.id,
                "email": user_response.user.email,
                "nombre": user_response.user.email.split("@")[0],
                "modo": "online",
                "email_confirmado": bool(getattr(user_response.user, "email_confirmed_at", None)),
            }
            self.session = dict(tokens)
            self.conectado = True
            return True
        except Exception:
            return False

    def exportar_sesion(self):
        if not self.usuario:
            return None
        data = dict(self.usuario)
        if self.session:
            data["tokens"] = dict(self.session)
        return data

    def descargar_vacas(self):
        if not self.usuario:
            raise RuntimeError("No autenticado en Supabase.")
        columnas = (
            "*"
            if self.soporta_pesajes
            else "uid,nombre,edad,raza,peso,enfermedades,vacunas,historial,usuario_id,ultima_actualizacion,creado_en"
        )
        try:
            response = (
                self.client.table("vacas")
                .select(columnas)
                .eq("usuario_id", self.usuario["id"])
                .execute()
            )
        except Exception as exc:
            if self.soporta_pesajes and self._error_columna_pesajes(exc):
                self.soporta_pesajes = False
                return self.descargar_vacas()
            raise

        vacas = {}
        for item in response.data or []:
            historial = []
            pesajes = []
            if item.get("historial"):
                try:
                    historial = json.loads(item["historial"])
                except Exception:
                    historial = []
            if item.get("pesajes"):
                try:
                    pesajes = json.loads(item["pesajes"])
                except Exception:
                    pesajes = []
            vacas[item["uid"]] = {
                "nombre": item.get("nombre", ""),
                "edad": item.get("edad", ""),
                "raza": item.get("raza", ""),
                "peso": item.get("peso", ""),
                "enfermedades": item.get("enfermedades", ""),
                "vacunas": item.get("vacunas", ""),
                "historial": historial,
                "pesajes": pesajes,
            }
        return vacas

    def insertar_o_actualizar_vaca(self, uid, datos):
        if not self.usuario:
            raise RuntimeError("No autenticado en Supabase.")
        payload = self._payload_vaca(uid, datos, incluir_pesajes=self.soporta_pesajes)
        try:
            response = (
                self.client.table("vacas")
                .select("*")
                .eq("uid", uid.lower())
                .eq("usuario_id", self.usuario["id"])
                .execute()
            )
            if response.data:
                (
                    self.client.table("vacas")
                    .update(payload)
                    .eq("uid", uid.lower())
                    .eq("usuario_id", self.usuario["id"])
                    .execute()
                )
            else:
                self.client.table("vacas").insert(payload).execute()
            return True
        except Exception as exc:
            if self.soporta_pesajes and self._error_columna_pesajes(exc):
                self.soporta_pesajes = False
                payload = self._payload_vaca(uid, datos, incluir_pesajes=False)
                response = (
                    self.client.table("vacas")
                    .select("*")
                    .eq("uid", uid.lower())
                    .eq("usuario_id", self.usuario["id"])
                    .execute()
                )
                if response.data:
                    (
                        self.client.table("vacas")
                        .update(payload)
                        .eq("uid", uid.lower())
                        .eq("usuario_id", self.usuario["id"])
                        .execute()
                    )
                else:
                    self.client.table("vacas").insert(payload).execute()
                return True
            raise

    def sincronizar_vacas(self, gestor_datos):
        if not self.usuario:
            raise RuntimeError("No autenticado en Supabase.")
        total = 0
        for uid, datos in gestor_datos.vacas.items():
            if self.insertar_o_actualizar_vaca(uid, datos):
                total += 1
        return total

    def cerrar_sesion(self):
        try:
            if self.client:
                self.client.auth.sign_out()
        except Exception:
            pass
        self.usuario = None
        self.session = None
        self.conectado = False
