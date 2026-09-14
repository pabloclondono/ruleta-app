# Ruleta · 3 Repeticiones y 12 Corners

Aplicación de escritorio (interfaz **Qt / PySide6**) para seguir dos estrategias de ruleta basadas en la **ley del tercio**:

- **3 Repeticiones**: espera la 2ª aparición de un número para empezar a apostar por él; la 3ª repetición cierra la jugada con beneficio. Progresión `i×(36−N)−12`, control de pérdidas y apuestas manuales sobre la mesa.
- **12 Corners**: divide el tapete en corners; según el número que sale se señala el corner a jugar y se coloca la moneda en la intersección que une sus 4 números. Sigue los niveles del video (sumar 1 ficha por corner al perder, volver a puesta base al alcanzar el mejor saldo).

La app se compila automáticamente como aplicación nativa para **Windows**, **macOS** y **Linux** (sin necesidad de Python).

## Videos de referencia

- **3 Repeticiones (parte 1)**: https://youtu.be/6_ZdYiSr5No
- **3 Repeticiones (parte 2 · aclaraciones y progresión)**: https://www.youtube.com/watch?v=2fcX6c0rid8
- **12 Corners**: https://www.youtube.com/watch?v=RHv2Qs5oFx4

## Descargar

Ve a la pestaña **Releases** de este repositorio y descarga el archivo para tu sistema:

| Sistema      | Archivo                     |
|--------------|-----------------------------|
| Windows      | `ruleta-windows.exe`        |
| macOS        | `ruleta-macos.zip`          |
| Linux        | `ruleta-linux`              |

### Avisos de seguridad

Los ejecutables no están firmados (cuesta dinero), así que el sistema mostrará un aviso:

- **Windows**: “Windows protegió su equipo” → clic en **Más información** → **Ejecutar de todas formas**.
- **macOS**: clic derecho sobre el `.app` → **Abrir** → **Abrir** (en vez de doble clic).
- **Linux**: da permiso de ejecución con `chmod +x ruleta-linux` y ejecuta `./ruleta-linux`.

## Uso

1. Escribe el número que salió y pulsa **Registrar**.
2. **Pestaña 3 Repeticiones**:
   - Coloca la ficha elegida (abajo) sobre la mesa para tus apuestas manuales.
   - La app detecta las repeticiones (R) y gestiona la jugada: 2ª aparición → empiezas a apostar; 3ª repetición → ganas (premio − pérdidas ≥ 12).
   - Cuando la pérdida vaya a superar el límite, **sumas 1 ficha** por número.
   - El **saldo** (arriba) baja según lo apostado en cada tirada y sube al acertar; el **beneficio** acumula las ganancias.
   - **NUEVA RONDA** reinicia la jugada; **NUEVA RONDA CON ÚLTIMAS RONDAS** conserva los últimos 15 números.
3. **Pestaña 12 Corners**:
   - El número salido señala el **corner a jugar** (resaltado en blanco) y se coloca una ficha con el dinero apostado en su intersección.
   - Al perder se añade un corner y se suma 1 ficha a todos; al alcanzar el mejor saldo vuelve a la puesta base.
   - El **saldo** (arriba) baja con la puesta de cada tirada y sube con el premio neto; **BENEFICIO** muestra la ganancia/pérdida de toda la partida.

## Compilar localmente

```bash
pip install pyinstaller pyside6
pyinstaller --onefile --windowed --collect-all PySide6 --name ruleta main.py   # Windows/Linux
pyinstaller --windowed --collect-all PySide6 --name ruleta main.py             # macOS (.app)
```

Los ejecutables Qt pesan bastante más (≈100–200 MB) porque incluyen la librería Qt completa.

## Desarrollar (estructura MVC)

```bash
python main.py
```

Código organizado en paquetes: `modelos/` (lógica de las estrategias), `vistas/` (Qt), `controladores/` (cablean modelo y vista).