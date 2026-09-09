# Ruleta · Estrategia 3 Repeticiones

Aplicación de escritorio para seguir la estrategia **“Tres Repeticiones”** (basada en la ley del tercio) en la ruleta, con mesa interactiva para colocar fichas, historial de números y apuestas automáticas de la progresión.

Se compila automáticamente como aplicación nativa para **Windows**, **macOS** y **Linux** (sin necesidad de Python).

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

1. Coloca la ficha elegida (abajo) sobre la mesa para tus apuestas manuales.
2. Escribe el número que salió y pulsa **Registrar**.
3. La app detecta las repeticiones (R) y gestiona la jugada por ti:
   - 2ª aparición de un número → empiezas a apostar por él.
   - 3ª repetición → ganas la jugada (premio − pérdidas = beneficio ≥ 12).
   - Cuando la pérdida vaya a superar el límite, **sumas 1 ficha** por número (progresión `i×(36−N)−12`).
4. **NUEVA RONDA** reinicia la jugada; **NUEVA RONDA CON ÚLTIMAS RONDAS** conserva los últimos 15 números.

## Compilar localmente

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name ruleta ruleta.py   # Windows/Linux
pyinstaller --windowed --name ruleta ruleta.py             # macOS (.app)
```