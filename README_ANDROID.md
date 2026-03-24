# Sistema Ganadero Android con Kivy

Esta base reemplaza la interfaz `PyQt5` por una interfaz `Kivy` para poder avanzar hacia Android.

## Archivos principales

- `app_kivy.py`: interfaz nueva pensada para Android.
- `ganadero_core.py`: lógica reutilizable de vacas, pesajes, vacunación y alertas.
- `requirements-android.txt`: dependencias base para desarrollo.
- `buildozer.spec.example`: ejemplo mínimo para empaquetar APK.

## Librerías para instalar en PC

```bash
pip install kivy==2.3.0
pip install supabase
pip install requests urllib3
```

Si quieres probar la app en Windows:

```bash
python app_kivy.py
```

## Qué quedó migrado

- alta y edición de vacas
- pesajes
- agenda de vacunación
- alertas productivas
- persistencia en JSON

## Qué falta para una migración completa

- login y registro visual con Supabase
- almacenamiento de imágenes
- lectura RFID/ESP32 adaptada a Android
- diseño móvil más avanzado
- empaquetado final con `buildozer` desde Linux

## Para generar APK

Normalmente se hace desde Linux o WSL/Ubuntu:

```bash
pip install buildozer
buildozer init
buildozer android debug
```

## Nota sobre Supabase

En `ganadero_core.py` dejé la URL y una key de ejemplo marcada para reemplazar. No conviene incrustar credenciales sensibles en una app móvil final.
