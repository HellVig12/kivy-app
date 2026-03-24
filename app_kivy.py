#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from threading import Thread

try:
    import serial
    import serial.tools.list_ports
    HAS_PYSERIAL = True
except Exception:
    serial = None
    HAS_PYSERIAL = False

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import Screen, ScreenManager

from ganadero_core import GestorDatos, GestorSesion, GestorSupabase

KV = """
#:import dp kivy.metrics.dp

<PBtn@Button>:
    size_hint_y: None
    height: dp(46)
    background_normal: ""
    background_color: (0.11, 0.46, 0.83, 1)
    color: (1, 1, 1, 1)
    bold: True

<ABtn@Button>:
    size_hint_y: None
    height: dp(46)
    background_normal: ""
    background_color: (0.16, 0.62, 0.44, 1)
    color: (1, 1, 1, 1)
    bold: True

<SBtn@Button>:
    size_hint_y: None
    height: dp(42)
    background_normal: ""
    background_color: (0.93, 0.96, 0.98, 1)
    color: (0.13, 0.20, 0.28, 1)
    bold: True

<DataInput@TextInput>:
    multiline: False
    size_hint_y: None
    height: dp(42)
    padding: dp(12), dp(10)
    background_normal: ""
    background_active: ""
    background_color: (1, 1, 1, 1)

<ItemBtn@Button>:
    size_hint_y: None
    height: dp(50)
    background_normal: ""
    background_color: (0.95, 0.97, 0.99, 1)
    color: (0.14, 0.18, 0.24, 1)
    halign: "left"
    valign: "middle"
    text_size: self.width - dp(18), None

<VacasRV>:
    viewclass: "ItemBtn"
    RecycleBoxLayout:
        default_size: None, dp(50)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        spacing: dp(6)
        orientation: "vertical"

<AuthScreen>:
    name: "auth"
    BoxLayout:
        orientation: "vertical"
        padding: dp(18)
        spacing: dp(12)
        canvas.before:
            Color:
                rgba: (0.93, 0.96, 0.98, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        Widget:
            size_hint_y: 0.08
        BoxLayout:
            orientation: "vertical"
            padding: dp(16)
            spacing: dp(10)
            size_hint_y: None
            height: self.minimum_height
            canvas.before:
                Color:
                    rgba: (0.15, 0.28, 0.40, 1)
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [28]
            Label:
                text: "Sistema Ganadero"
                color: (1, 1, 1, 1)
                bold: True
                font_size: "30sp"
                size_hint_y: None
                height: self.texture_size[1] + dp(4)
            Label:
                text: "RFID  |  Supabase  |  Control sanitario"
                color: (0.83, 0.91, 0.96, 1)
                size_hint_y: None
                height: self.texture_size[1] + dp(4)
            Label:
                text: root.mensaje_estado
                color: (0.88, 0.95, 0.99, 1)
                text_size: self.width, None
                halign: "left"
                size_hint_y: None
                height: self.texture_size[1] + dp(6)
        BoxLayout:
            orientation: "vertical"
            padding: dp(16)
            spacing: dp(10)
            size_hint_y: None
            height: self.minimum_height
            canvas.before:
                Color:
                    rgba: (1, 1, 1, 0.98)
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [24]
            Label:
                text: "Acceso"
                color: (0.11, 0.17, 0.24, 1)
                bold: True
                font_size: "22sp"
                size_hint_y: None
                height: self.texture_size[1] + dp(4)
            DataInput:
                id: login_email
                hint_text: "Correo electronico"
            DataInput:
                id: login_password
                hint_text: "Contrasena"
                password: True
            PBtn:
                text: "Iniciar sesion"
                on_release: app.login_online(login_email.text, login_password.text)
            ABtn:
                text: "Crear cuenta"
                on_release: app.registrar_online(login_email.text, login_password.text)
            SBtn:
                text: "Entrar en modo local"
                on_release: app.login_local()
        Widget:
            size_hint_y: 0.18

<DashboardScreen>:
    name: "dashboard"
    BoxLayout:
        orientation: "vertical"
        padding: dp(12)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: (0.94, 0.97, 0.99, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            orientation: "vertical"
            padding: dp(14)
            spacing: dp(8)
            size_hint_y: None
            height: self.minimum_height
            canvas.before:
                Color:
                    rgba: (0.15, 0.28, 0.40, 1)
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [24]
            Label:
                text: "Centro de Control"
                color: (1, 1, 1, 1)
                bold: True
                font_size: "26sp"
                size_hint_y: None
                height: self.texture_size[1] + dp(4)
            Label:
                text: root.usuario_texto + " | " + root.estado_general
                color: (0.84, 0.92, 0.97, 1)
                text_size: self.width, None
                halign: "left"
                size_hint_y: None
                height: self.texture_size[1] + dp(4)
            BoxLayout:
                size_hint_y: None
                height: dp(42)
                spacing: dp(6)
                SBtn:
                    text: "Inicio"
                    on_release: root.mostrar_panel("inicio")
                SBtn:
                    text: "Vacas"
                    on_release: root.mostrar_panel("vacas")
                SBtn:
                    text: "Detalle"
                    on_release: root.mostrar_panel("detalle")
                SBtn:
                    text: "Cerrar"
                    on_release: app.cerrar_sesion()
        BoxLayout:
            size_hint_y: None
            height: dp(84)
            spacing: dp(6)
            BoxLayout:
                orientation: "vertical"
                padding: dp(10)
                canvas.before:
                    Color:
                        rgba: (0.11, 0.46, 0.83, 1)
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [18]
                Label:
                    text: root.total_vacas
                    color: (1, 1, 1, 1)
                    bold: True
                    font_size: "24sp"
                Label:
                    text: "Vacas"
                    color: (0.88, 0.95, 1, 1)
            BoxLayout:
                orientation: "vertical"
                padding: dp(10)
                canvas.before:
                    Color:
                        rgba: (0.84, 0.29, 0.29, 1)
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [18]
                Label:
                    text: root.vacas_urgentes
                    color: (1, 1, 1, 1)
                    bold: True
                    font_size: "24sp"
                Label:
                    text: "Urgentes"
                    color: (1, 0.91, 0.91, 1)
            BoxLayout:
                orientation: "vertical"
                padding: dp(10)
                canvas.before:
                    Color:
                        rgba: (0.95, 0.69, 0.17, 1)
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [18]
                Label:
                    text: root.vacas_proximas
                    color: (1, 1, 1, 1)
                    bold: True
                    font_size: "24sp"
                Label:
                    text: "Proximas"
                    color: (1, 0.97, 0.88, 1)
            BoxLayout:
                orientation: "vertical"
                padding: dp(10)
                canvas.before:
                    Color:
                        rgba: (0.08, 0.62, 0.54, 1)
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [18]
                Label:
                    text: root.vacas_sin_peso
                    color: (1, 1, 1, 1)
                    bold: True
                    font_size: "24sp"
                Label:
                    text: "Sin peso"
                    color: (0.90, 1, 0.98, 1)
        BoxLayout:
            orientation: "vertical"
            padding: dp(12)
            spacing: dp(8)
            size_hint_y: None
            height: self.minimum_height
            canvas.before:
                Color:
                    rgba: (1, 1, 1, 0.98)
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [20]
            BoxLayout:
                size_hint_y: None
                height: dp(42)
                spacing: dp(6)
                Spinner:
                    id: puerto_spinner
                    text: "Sin puertos"
                    values: root.puertos_disponibles
                SBtn:
                    text: "Buscar USB"
                    on_release: root.refrescar_puertos()
                PBtn:
                    text: root.serial_boton_texto
                    on_release: root.toggle_serial()
            Label:
                text: root.serial_estado
                color: (0.36, 0.43, 0.50, 1)
                text_size: self.width, None
                halign: "left"
                size_hint_y: None
                height: self.texture_size[1] + dp(4)
            BoxLayout:
                size_hint_y: None
                height: dp(42)
                spacing: dp(6)
                SBtn:
                    text: "Refrescar"
                    on_release: root.refrescar_todo()
                SBtn:
                    text: "Descargar"
                    on_release: app.descargar_desde_supabase()
                SBtn:
                    text: "Sincronizar"
                    on_release: app.sincronizar_con_supabase()
        ScrollView:
            do_scroll_x: False
            BoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(10)
                BoxLayout:
                    id: panel_inicio
                    orientation: "vertical"
                    padding: dp(14)
                    spacing: dp(8)
                    size_hint_y: None
                    height: self.minimum_height
                    canvas.before:
                        Color:
                            rgba: (1, 1, 1, 0.98)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [20]
                    Label:
                        text: "Resumen"
                        color: (0.11, 0.17, 0.24, 1)
                        bold: True
                        font_size: "20sp"
                        size_hint_y: None
                        height: self.texture_size[1] + dp(4)
                    Label:
                        text: "Usa Vacas para buscar fichas y Detalle para editar la seleccionada."
                        color: (0.22, 0.30, 0.38, 1)
                        text_size: self.width, None
                        halign: "left"
                        size_hint_y: None
                        height: self.texture_size[1] + dp(6)
                    Label:
                        text: "Alertas\\n" + root.alertas_texto
                        color: (0.15, 0.15, 0.15, 1)
                        text_size: self.width, None
                        halign: "left"
                        size_hint_y: None
                        height: self.texture_size[1] + dp(8)
                BoxLayout:
                    id: panel_vacas
                    orientation: "vertical"
                    padding: dp(14)
                    spacing: dp(8)
                    size_hint_y: None
                    height: 0
                    opacity: 0
                    disabled: True
                    canvas.before:
                        Color:
                            rgba: (1, 1, 1, 0.98)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [20]
                    Label:
                        text: "Rodeo"
                        color: (0.11, 0.17, 0.24, 1)
                        bold: True
                        font_size: "20sp"
                        size_hint_y: None
                        height: self.texture_size[1] + dp(4)
                    DataInput:
                        id: buscar_input
                        hint_text: "Buscar por UID o nombre"
                        on_text: root.filtrar_vacas(self.text)
                    VacasRV:
                        id: vacas_rv
                        size_hint_y: None
                        height: dp(330)
                    Label:
                        text: root.vaca_resumen_texto
                        color: (0.22, 0.30, 0.38, 1)
                        text_size: self.width, None
                        halign: "left"
                        size_hint_y: None
                        height: self.texture_size[1] + dp(6)
                BoxLayout:
                    id: panel_detalle
                    orientation: "vertical"
                    padding: dp(14)
                    spacing: dp(8)
                    size_hint_y: None
                    height: 0
                    opacity: 0
                    disabled: True
                    canvas.before:
                        Color:
                            rgba: (1, 1, 1, 0.98)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [20]
                    Label:
                        text: "Ficha de la vaca"
                        color: (0.11, 0.17, 0.24, 1)
                        bold: True
                        font_size: "20sp"
                        size_hint_y: None
                        height: self.texture_size[1] + dp(4)
                    DataInput:
                        id: uid_input
                        hint_text: "UID"
                    DataInput:
                        id: nombre_input
                        hint_text: "Nombre"
                    DataInput:
                        id: edad_input
                        hint_text: "Edad"
                    DataInput:
                        id: raza_input
                        hint_text: "Raza"
                    DataInput:
                        id: peso_input
                        hint_text: "Peso actual (kg)"
                    DataInput:
                        id: enf_input
                        hint_text: "Enfermedades"
                    DataInput:
                        id: vac_input
                        hint_text: "Vacunas"
                    BoxLayout:
                        size_hint_y: None
                        height: dp(44)
                        spacing: dp(6)
                        PBtn:
                            text: "Guardar cambios"
                            on_release: root.guardar_vaca()
                        SBtn:
                            text: "Nueva ficha"
                            on_release: root.limpiar_formulario()
                    DataInput:
                        id: pesaje_input
                        hint_text: "Nuevo pesaje (kg)"
                    BoxLayout:
                        size_hint_y: None
                        height: dp(44)
                        spacing: dp(6)
                        ABtn:
                            text: "Registrar pesaje"
                            on_release: root.registrar_pesaje()
                        SBtn:
                            text: "Agendar vacuna"
                            on_release: root.popup_vacuna()
                    Label:
                        text: root.detalle_texto
                        color: (0.15, 0.15, 0.15, 1)
                        text_size: self.width, None
                        halign: "left"
                        size_hint_y: None
                        height: self.texture_size[1] + dp(10)
"""


class AuthScreen(Screen):
    mensaje_estado = StringProperty("Inicia sesion con Supabase o usa modo local.")


class VacasRV(RecycleView):
    pass


class DashboardScreen(Screen):
    usuario_texto = StringProperty("Usuario")
    estado_general = StringProperty("Listo.")
    total_vacas = StringProperty("0")
    vacas_urgentes = StringProperty("0")
    vacas_proximas = StringProperty("0")
    vacas_sin_peso = StringProperty("0")
    serial_estado = StringProperty("Serial USB no conectado.")
    serial_boton_texto = StringProperty("Conectar USB")
    puertos_disponibles = ListProperty(["Sin puertos"])
    vaca_resumen_texto = StringProperty("Selecciona una vaca para ver su ficha.")
    alertas_texto = StringProperty("No hay alertas activas.")
    detalle_texto = StringProperty("Selecciona o escanea un UID.")
    panel_actual = StringProperty("inicio")

    def __init__(self, gestor, **kwargs):
        super().__init__(**kwargs)
        self.gestor = gestor
        self.uid_actual = ""
        self.serial_port = None
        self.serial_thread = None
        self.serial_running = False
        self.ultimo_uid_serial = ""

    def on_enter(self, *args):
        self.refrescar_todo()
        self.mostrar_panel(self.panel_actual)
        Clock.schedule_once(lambda _dt: self.refrescar_puertos(), 0)
        return super().on_enter(*args)

    def popup(self, titulo, mensaje):
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        content.add_widget(Label(text=mensaje))
        btn = Button(text="Cerrar", size_hint_y=None, height=dp(44))
        popup = Popup(title=titulo, content=content, size_hint=(0.88, 0.44))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        popup.open()

    def cargar_usuario(self, sesion):
        if sesion.get("modo") == "local":
            self.usuario_texto = f"Modo local | {sesion.get('nombre', 'Usuario local')}"
            self.estado_general = "Trabajando sin conexion."
        else:
            self.usuario_texto = f"{sesion.get('email', 'usuario')} | Online"
            self.estado_general = "Email confirmado" if sesion.get("email_confirmado") else "Sesion online activa"

    def refrescar_todo(self):
        resumen, alertas = self.gestor.construir_alertas()
        self.total_vacas = str(resumen["total_vacas"])
        self.vacas_urgentes = str(resumen["urgentes"])
        self.vacas_proximas = str(resumen["proximas"])
        self.vacas_sin_peso = str(resumen["sin_peso"])
        self.alertas_texto = "\n\n".join(
            f"[{a['nivel'].upper()}] {a['uid'].upper()} - {a['titulo']}\n{a['detalle']}"
            for a in alertas[:12]
        ) or "No hay alertas activas."
        self.filtrar_vacas(self.ids.buscar_input.text if "buscar_input" in self.ids else "")
        if self.uid_actual and self.gestor.obtener_vaca(self.uid_actual):
            self.cargar_detalle(self.uid_actual)

    def mostrar_panel(self, nombre):
        self.panel_actual = nombre
        paneles = {
            "inicio": self.ids.panel_inicio,
            "vacas": self.ids.panel_vacas,
            "detalle": self.ids.panel_detalle,
        }
        for clave, panel in paneles.items():
            activo = clave == nombre
            panel.opacity = 1 if activo else 0
            panel.disabled = not activo
            panel.height = panel.minimum_height if activo else 0

    def filtrar_vacas(self, texto):
        filtro = (texto or "").strip().lower()
        filas = []
        total = 0
        for uid, vaca in self.gestor.listar_vacas():
            nombre = vaca.get("nombre", "")
            if filtro and filtro not in uid.lower() and filtro not in nombre.lower():
                continue
            total += 1
            filas.append({
                "text": f"{uid.upper()} | {nombre or '-'} | {vaca.get('raza', '-')} | {vaca.get('peso', '-')} kg",
                "on_release": (lambda current_uid=uid: self.seleccionar_vaca(current_uid)),
            })
        self.ids.vacas_rv.data = filas
        self.vaca_resumen_texto = f"Mostrando {total} vaca(s). Toca una para abrir su ficha." if filas else "No hay vacas para ese filtro."

    def limpiar_formulario(self):
        for field_id in ("uid_input", "nombre_input", "edad_input", "raza_input", "peso_input", "enf_input", "vac_input", "pesaje_input"):
            self.ids[field_id].text = ""
        self.uid_actual = ""
        self.detalle_texto = "Selecciona o escanea un UID."
        self.mostrar_panel("detalle")

    def guardar_vaca(self):
        uid = self.ids.uid_input.text.strip().lower()
        if not uid:
            self.popup("Dato faltante", "El UID es obligatorio.")
            return
        datos = {
            "nombre": self.ids.nombre_input.text,
            "edad": self.ids.edad_input.text,
            "raza": self.ids.raza_input.text,
            "peso": self.ids.peso_input.text,
            "enfermedades": self.ids.enf_input.text,
            "vacunas": self.ids.vac_input.text,
        }
        try:
            if self.gestor.obtener_vaca(uid):
                self.gestor.actualizar_vaca(uid, **datos)
            else:
                self.gestor.crear_vaca(uid, **datos)
            self.uid_actual = uid
            self.cargar_detalle(uid)
            self.refrescar_todo()
            self.popup("OK", "Datos guardados.")
        except Exception as exc:
            self.popup("Error", str(exc))

    def seleccionar_vaca(self, uid):
        vaca = self.gestor.obtener_vaca(uid)
        if not vaca:
            return
        self.uid_actual = uid
        self.ids.uid_input.text = uid
        self.ids.nombre_input.text = vaca.get("nombre", "")
        self.ids.edad_input.text = vaca.get("edad", "")
        self.ids.raza_input.text = vaca.get("raza", "")
        self.ids.peso_input.text = vaca.get("peso", "")
        self.ids.enf_input.text = vaca.get("enfermedades", "")
        self.ids.vac_input.text = vaca.get("vacunas", "")
        self.cargar_detalle(uid)
        self.mostrar_panel("detalle")

    def cargar_detalle(self, uid):
        vaca = self.gestor.obtener_vaca(uid)
        if not vaca:
            self.detalle_texto = "No existe esa vaca."
            return
        historial = "\n".join(vaca.get("historial", [])[-8:]) or "Sin historial"
        pesajes = "\n".join(f"{p.get('fecha', '-')}: {p.get('peso', '-')} kg" for p in vaca.get("pesajes", [])[-8:]) or "Sin pesajes"
        self.detalle_texto = (
            f"UID: {uid.upper()}\nNombre: {vaca.get('nombre', '-')}\nEdad: {vaca.get('edad', '-')}\n"
            f"Raza: {vaca.get('raza', '-')}\nPeso actual: {vaca.get('peso', '-')}\n"
            f"Enfermedades: {vaca.get('enfermedades', '-')}\nVacunas: {vaca.get('vacunas', '-')}\n\n"
            f"Pesajes:\n{pesajes}\n\nHistorial:\n{historial}"
        )

    def registrar_pesaje(self):
        uid = self.ids.uid_input.text.strip().lower()
        peso = self.ids.pesaje_input.text.strip()
        if not uid or not peso:
            self.popup("Dato faltante", "Completa UID y nuevo pesaje.")
            return
        try:
            float(peso.replace(",", "."))
            self.gestor.registrar_pesaje(uid, peso, datetime.now())
            self.uid_actual = uid
            self.ids.pesaje_input.text = ""
            self.cargar_detalle(uid)
            self.refrescar_todo()
            self.popup("OK", "Pesaje registrado.")
        except Exception as exc:
            self.popup("Error", str(exc))

    def popup_vacuna(self):
        uid = self.ids.uid_input.text.strip().lower()
        if not uid:
            self.popup("Dato faltante", "Escribe el UID antes de agendar la vacuna.")
            return
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        vacuna = Builder.load_string("TextInput:\\n    multiline: False\\n    hint_text: 'Nombre de la vacuna'\\n    size_hint_y: None\\n    height: dp(42)\\n")
        fecha = Builder.load_string("TextInput:\\n    multiline: False\\n    hint_text: 'YYYY-MM-DD'\\n    size_hint_y: None\\n    height: dp(42)\\n")
        fecha.text = datetime.now().strftime("%Y-%m-%d")
        acciones = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        popup = Popup(title="Agendar vacuna", content=content, size_hint=(0.9, 0.45))
        ok_btn = Button(text="Guardar")
        cancel_btn = Button(text="Cancelar")
        content.add_widget(vacuna)
        content.add_widget(fecha)
        acciones.add_widget(ok_btn)
        acciones.add_widget(cancel_btn)
        content.add_widget(acciones)

        def guardar(*_args):
            try:
                self.gestor.agendar_vacuna(uid, vacuna.text, fecha.text)
                self.uid_actual = uid
                self.cargar_detalle(uid)
                self.refrescar_todo()
                popup.dismiss()
                self.popup("OK", "Vacuna agendada.")
            except Exception as exc:
                self.popup("Error", str(exc))

        ok_btn.bind(on_release=guardar)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()

    def refrescar_puertos(self):
        if not HAS_PYSERIAL:
            self.puertos_disponibles = ["pyserial no instalado"]
            self.ids.puerto_spinner.text = "pyserial no instalado"
            self.serial_estado = "Instala pyserial para leer el ESP32 por USB."
            return
        puertos = [port.device for port in serial.tools.list_ports.comports()]
        self.puertos_disponibles = puertos or ["Sin puertos"]
        if self.ids.puerto_spinner.text not in puertos:
            self.ids.puerto_spinner.text = self.puertos_disponibles[0]
        self.serial_estado = f"Puertos detectados: {len(puertos)}" if puertos else "No se detectaron puertos USB."

    def toggle_serial(self):
        if self.serial_running:
            self.desconectar_serial()
        else:
            self.conectar_serial()

    def conectar_serial(self):
        if not HAS_PYSERIAL:
            self.popup("Serial USB", "Falta instalar pyserial.")
            return
        puerto = self.ids.puerto_spinner.text
        if not puerto or puerto in ("Sin puertos", "pyserial no instalado"):
            self.popup("Serial USB", "Selecciona un puerto valido.")
            return
        try:
            self.serial_port = serial.Serial(puerto, 115200, timeout=1)
        except Exception as exc:
            self.popup("Error serial", f"No se pudo abrir {puerto}.\n\n{exc}")
            return
        self.serial_running = True
        self.serial_boton_texto = "Desconectar USB"
        self.serial_estado = f"Conectado a {puerto}. Esperando UID..."
        self.serial_thread = Thread(target=self._serial_loop, daemon=True)
        self.serial_thread.start()

    def desconectar_serial(self):
        self.serial_running = False
        self.serial_boton_texto = "Conectar USB"
        if self.serial_port:
            try:
                self.serial_port.close()
            except Exception:
                pass
        self.serial_port = None
        self.serial_estado = "Serial USB desconectado."

    def _serial_loop(self):
        while self.serial_running and self.serial_port:
            try:
                raw = self.serial_port.readline()
                if not raw:
                    continue
                texto = raw.decode(errors="ignore").strip().lower()
                if len(texto) >= 8 and all(ch in "0123456789abcdef" for ch in texto):
                    if texto != self.ultimo_uid_serial:
                        self.ultimo_uid_serial = texto
                        Clock.schedule_once(lambda _dt, uid=texto: self.procesar_uid_serial(uid), 0)
                elif texto:
                    Clock.schedule_once(lambda _dt, msg=texto: self._mostrar_estado_serial(msg), 0)
            except Exception as exc:
                Clock.schedule_once(lambda _dt, err=str(exc): self._error_serial(err), 0)
                break

    def _mostrar_estado_serial(self, mensaje):
        self.serial_estado = f"ESP32: {mensaje[:60]}"

    def _error_serial(self, error):
        self.desconectar_serial()
        self.popup("Serial USB", f"Se perdio la conexion serial.\n\n{error}")

    def procesar_uid_serial(self, uid):
        self.serial_estado = f"UID recibido: {uid.upper()}"
        self.ids.uid_input.text = uid
        self.uid_actual = uid
        vaca = self.gestor.obtener_vaca(uid)
        if vaca:
            self.ids.nombre_input.text = vaca.get("nombre", "")
            self.ids.edad_input.text = vaca.get("edad", "")
            self.ids.raza_input.text = vaca.get("raza", "")
            self.ids.peso_input.text = vaca.get("peso", "")
            self.ids.enf_input.text = vaca.get("enfermedades", "")
            self.ids.vac_input.text = vaca.get("vacunas", "")
            self.gestor.registrar_evento(uid, "Ingreso detectado por RFID via serial USB")
            self.cargar_detalle(uid)
            self.refrescar_todo()
            self.mostrar_panel("detalle")
        else:
            self.detalle_texto = f"UID: {uid.upper()}\n\nNo existe una vaca registrada con ese UID. Completa la ficha y guarda."
            self.mostrar_panel("detalle")


class GanaderoApp(App):
    def build(self):
        self.title = "Sistema Ganadero"
        Builder.load_string(KV)
        self.gestor = GestorDatos()
        self.gestor_sesion = GestorSesion()
        self.supabase = GestorSupabase()
        self.sm = ScreenManager()
        self.auth_screen = AuthScreen()
        self.dashboard_screen = DashboardScreen(gestor=self.gestor)
        self.sm.add_widget(self.auth_screen)
        self.sm.add_widget(self.dashboard_screen)
        self.restaurar_sesion()
        return self.sm

    def popup(self, titulo, mensaje):
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        content.add_widget(Label(text=mensaje))
        btn = Button(text="Cerrar", size_hint_y=None, height=dp(44))
        popup = Popup(title=titulo, content=content, size_hint=(0.88, 0.44))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        popup.open()

    def restaurar_sesion(self):
        sesion = self.gestor_sesion.cargar()
        if not sesion:
            self.sm.current = "auth"
            return
        if sesion.get("modo") == "local":
            self.dashboard_screen.cargar_usuario(sesion)
            self.dashboard_screen.refrescar_todo()
            self.sm.current = "dashboard"
            return
        if self.supabase.restaurar_sesion(sesion):
            nueva = self.supabase.exportar_sesion() or sesion
            self.gestor_sesion.guardar(nueva)
            self.dashboard_screen.cargar_usuario(nueva)
            try:
                remotas = self.supabase.descargar_vacas()
                if remotas:
                    self.gestor.reemplazar_vacas(remotas)
            except Exception:
                pass
            self.dashboard_screen.refrescar_todo()
            self.sm.current = "dashboard"
            return
        self.gestor_sesion.limpiar()
        self.auth_screen.mensaje_estado = "La sesion online vencio. Inicia sesion otra vez o usa modo local."
        self.sm.current = "auth"

    def login_local(self):
        sesion = self.gestor_sesion.crear_sesion_local()
        self.dashboard_screen.cargar_usuario(sesion)
        self.dashboard_screen.refrescar_todo()
        self.sm.current = "dashboard"

    def login_online(self, email, password):
        email = (email or "").strip()
        password = password or ""
        if not email or not password:
            self.auth_screen.mensaje_estado = "Completa email y contrasena."
            return
        try:
            sesion = self.supabase.login_password(email, password)
            self.gestor_sesion.guardar(sesion)
            self.dashboard_screen.cargar_usuario(sesion)
            remotas = self.supabase.descargar_vacas()
            if remotas:
                self.gestor.reemplazar_vacas(remotas)
            self.dashboard_screen.refrescar_todo()
            self.sm.current = "dashboard"
        except Exception as exc:
            self.auth_screen.mensaje_estado = f"No se pudo iniciar sesion: {exc}"

    def registrar_online(self, email, password):
        email = (email or "").strip()
        password = password or ""
        if not email or not password:
            self.auth_screen.mensaje_estado = "Completa email y contrasena para registrarte."
            return
        if len(password) < 6:
            self.auth_screen.mensaje_estado = "La contrasena debe tener al menos 6 caracteres."
            return
        try:
            sesion = self.supabase.registrar_usuario(email, password)
            self.gestor_sesion.guardar(sesion)
            self.dashboard_screen.cargar_usuario(sesion)
            self.dashboard_screen.refrescar_todo()
            self.sm.current = "dashboard"
            self.popup("Registro completado", "La cuenta fue creada. Revisa tu email si tu proyecto exige confirmacion.")
        except Exception as exc:
            self.auth_screen.mensaje_estado = f"No se pudo crear la cuenta: {exc}"

    def sincronizar_con_supabase(self):
        sesion = self.gestor_sesion.cargar() or {}
        if sesion.get("modo") == "local":
            self.popup("Sincronizacion", "Estas en modo local. Inicia sesion online para sincronizar.")
            return
        if not self.supabase.usuario:
            self.popup("Sincronizacion", "No hay sesion online activa.")
            return
        try:
            total = self.supabase.sincronizar_vacas(self.gestor)
            self.dashboard_screen.refrescar_todo()
            self.popup("Sincronizacion", f"Se sincronizaron {total} vacas con la tabla remota.")
        except Exception as exc:
            self.popup("Sincronizacion", f"No se pudo sincronizar con Supabase.\n\n{exc}")

    def descargar_desde_supabase(self):
        sesion = self.gestor_sesion.cargar() or {}
        if sesion.get("modo") == "local":
            self.popup("Descarga", "Estas en modo local. Inicia sesion online para descargar datos.")
            return
        if not self.supabase.usuario:
            self.popup("Descarga", "No hay sesion online activa.")
            return
        try:
            remotas = self.supabase.descargar_vacas()
            self.gestor.reemplazar_vacas(remotas)
            self.dashboard_screen.refrescar_todo()
            self.popup("Descarga", f"Se descargaron {len(remotas)} vacas desde Supabase.")
        except Exception as exc:
            self.popup("Descarga", f"No se pudo descargar la tabla remota.\n\n{exc}")

    def cerrar_sesion(self):
        self.dashboard_screen.desconectar_serial()
        try:
            self.supabase.cerrar_sesion()
        except Exception:
            pass
        self.gestor_sesion.limpiar()
        self.auth_screen.mensaje_estado = "Sesion cerrada. Puedes iniciar sesion otra vez o usar modo local."
        self.sm.current = "auth"

    def on_stop(self):
        if hasattr(self, "dashboard_screen"):
            self.dashboard_screen.desconectar_serial()


if __name__ == "__main__":
    GanaderoApp().run()
