import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox

ROJO = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
NEGRO = set(range(1, 37)) - ROJO
RANGO = [str(n) for n in range(37)]

FILAS = [
    [3,6,9,12,15,18,21,24,27,30,33,36],
    [2,5,8,11,14,17,20,23,26,29,32,35],
    [1,4,7,10,13,16,19,22,25,28,31,34],
]

VALORES_FICHAS = [50, 500, 2500, 5000, 25000, 50000]
COLOR_FICHA = {50: "#d7dce8", 500: "#c81e1e", 2500: "#1d7c1d",
               5000: "#121212", 25000: "#6a2c91", 50000: "#1b4f8a"}
TEXTO_FICHA = {50: "#1a1a1a", 500: "#ffffff", 2500: "#ffffff",
               5000: "#ffffff", 25000: "#ffffff", 50000: "#ffffff"}

FONDO   = "#141414"
PANEL   = "#1e1e1e"
TEXTO   = "#e8e8e8"
SUB     = "#8f8f8f"
ORO     = "#d9a621"
VERDE   = "#166b16"
ROJO_BG = "#c81e1e"
NEGRO_BG = "#111111"
AZUL    = "#1b4f8a"
GRIS    = "#3a3a3a"

BASE_W, BASE_H = 1000, 720


class RuletaApp:
    def __init__(self, root):
        self.root = root
        root.title("Seguimiento de Ruleta · Estrategia 3 Repeticiones")
        root.configure(bg=FONDO)
        root.geometry("1000x760")
        root.minsize(820, 620)

        self.bets = {}
        self.historial = []
        self.celdas = {}
        self.ultima_celda = None

        self._estado_estrategia()
        self.chip = tk.IntVar(value=500)
        self._s = 1.0
        self.col_fichas = []

        self._crear_fuentes()
        self._crear_widgets()
        self._dibujar_fichas()
        self._cinta()
        root.bind("<Configure>", self._on_configure)

    def _estado_estrategia(self):
        self.banca = tk.StringVar(value="200")
        self.saldo = 200
        self.beneficio = 0
        self.unidad = 1
        self.perdida = 0
        self.juego_tiros = 0
        self.fase = "obs"
        self.juego_count = {}
        self.estrategia = {}
        self.fase_var = tk.StringVar()
        self.apuestas_var = tk.StringVar()
        self.perdida_var = tk.StringVar()
        self.unidad_var = tk.StringVar()
        self.saldo_var = tk.StringVar()
        self.benef_var = tk.StringVar()

    def _crear_fuentes(self):
        self.fonts = []
        def fuente(base, peso):
            f = tkfont.Font(size=int(base * self._s), weight=peso)
            self.fonts.append((f, base))
            return f
        self.f_tit  = fuente(14, "bold")
        self.f_sub  = fuente(10, "normal")
        self.f_num  = fuente(11, "bold")
        self.f_mon  = fuente(9, "bold")
        self.f_chip = fuente(8, "bold")
        self.f_hist = fuente(13, "bold")
        self.f_txt  = fuente(10, "normal")
        self.f_btn  = fuente(13, "bold")
        self.f_peq  = fuente(10, "bold")
        self.f_est  = fuente(8, "bold")

    def _crear_widgets(self):
        self.content = tk.Frame(self.root, bg=FONDO)
        self.content.pack(fill="both", expand=True)
        self.content.grid_rowconfigure(1, weight=1)
        self.content.grid_rowconfigure(3, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self._fila_registro(self.content)
        self._paneles(self.content)
        self._cinta_estrategia(self.content)
        self._marco_mesa(self.content)
        self._barra_fichas(self.content)
        self._btn_nueva(self.content)

    def _fila_registro(self, padre):
        fila = tk.Frame(padre, bg=FONDO)
        fila.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))

        tk.Label(fila, text="REGISTRAR NÚMERO", bg=FONDO, fg=ORO,
                 font=self.f_peq).pack(side="left")
        self.entry_num = tk.Entry(fila, width=5, font=self.f_hist, justify="center",
                                  bg="#0d0d0d", fg="white", relief="flat", bd=0)
        self.entry_num.pack(side="left", padx=(8, 6))
        self.entry_num.bind("<Return>", lambda e: self._registrar())

        tk.Button(fila, text="Registrar", command=self._registrar, font=self.f_peq,
                  bg=ORO, fg="#1a1a1a", relief="flat", bd=0, padx=12, pady=2,
                  activebackground="#e6b73c", cursor="hand2").pack(side="left")

        tk.Button(fila, text="Limpiar apuestas manuales", command=self._limpiar_apuestas,
                  font=self.f_sub, bg=GRIS, fg=TEXTO, relief="flat", bd=0,
                  padx=10, pady=2, activebackground="#4a4a4a", cursor="hand2"
                  ).pack(side="left", padx=(14, 0))

        self.tiros_var = tk.StringVar(value="Tiros: 0")
        self.total_var = tk.StringVar(value="Total: $0")
        tk.Label(fila, textvariable=self.tiros_var, bg=FONDO, fg=TEXTO,
                 font=self.f_sub).pack(side="right", padx=10)
        tk.Label(fila, textvariable=self.total_var, bg=FONDO, fg=ORO,
                 font=self.f_peq).pack(side="right", padx=10)

    def _cinta_estrategia(self, padre):
        cinta = tk.Frame(padre, bg="#101010", highlightbackground="#2c2c2c",
                         highlightthickness=1)
        cinta.grid(row=2, column=0, sticky="ew", padx=12, pady=(2, 6))

        self.lbl_fase = tk.Label(cinta, text="FASE", bg="#101010", fg=SUB, font=self.f_sub)
        self.lbl_fase.pack(side="left", padx=(10, 2))
        self.val_fase = tk.Label(cinta, textvariable=self.fase_var, bg="#101010",
                                 fg=ORO, font=self.f_peq)
        self.val_fase.pack(side="left", padx=(0, 14))

        tk.Label(cinta, text="APOSTADOS", bg="#101010", fg=SUB, font=self.f_sub
                 ).pack(side="left", padx=(0, 2))
        tk.Label(cinta, textvariable=self.apuestas_var, bg="#101010", fg=TEXTO,
                 font=self.f_peq).pack(side="left", padx=(0, 14))

        tk.Label(cinta, text="PÉRDIDA", bg="#101010", fg=SUB, font=self.f_sub
                 ).pack(side="left", padx=(0, 2))
        self.lbl_perdida = tk.Label(cinta, textvariable=self.perdida_var, bg="#101010",
                                    fg=TEXTO, font=self.f_peq)
        self.lbl_perdida.pack(side="left", padx=(0, 6))
        tk.Button(cinta, text="Reiniciar conteo", command=self._reiniciar_conteo,
                  font=self.f_sub, bg="#7a4d1a", fg="white", relief="flat", bd=0,
                  padx=8, pady=1, activebackground="#955d1f", cursor="hand2"
                  ).pack(side="left", padx=(0, 14))

        tk.Label(cinta, text="UNIDAD", bg="#101010", fg=SUB, font=self.f_sub
                 ).pack(side="left", padx=(0, 2))
        tk.Label(cinta, textvariable=self.unidad_var, bg="#101010", fg=TEXTO,
                 font=self.f_peq).pack(side="left", padx=(0, 14))

        tk.Label(cinta, text="BANCA", bg="#101010", fg=SUB, font=self.f_sub
                 ).pack(side="left", padx=(0, 2))
        self.entry_banca = tk.Entry(cinta, width=5, font=self.f_sub, justify="center",
                                    bg="#1a1a1a", fg="white", relief="flat", bd=0,
                                    textvariable=self.banca)
        self.entry_banca.pack(side="left", padx=(0, 4))
        tk.Button(cinta, text="OK", command=self._apl_banca, font=self.f_sub,
                  bg=GRIS, fg=TEXTO, relief="flat", bd=0, padx=6, cursor="hand2"
                  ).pack(side="left", padx=(0, 14))

        tk.Label(cinta, text="SALDO", bg="#101010", fg=SUB, font=self.f_sub
                 ).pack(side="left", padx=(0, 2))
        tk.Label(cinta, textvariable=self.saldo_var, bg="#101010", fg=ORO,
                 font=self.f_peq).pack(side="left", padx=(0, 14))

        tk.Label(cinta, text="BENEFICIO", bg="#101010", fg=SUB, font=self.f_sub
                 ).pack(side="left", padx=(0, 2))
        tk.Label(cinta, textvariable=self.benef_var, bg="#101010", fg="#4caf50",
                 font=self.f_peq).pack(side="right", padx=10)

    def _paneles(self, padre):
        zona = tk.Frame(padre, bg=FONDO)
        zona.grid(row=1, column=0, sticky="nsew", padx=12, pady=(6, 4))
        for c in range(3):
            zona.grid_columnconfigure(c, weight=1, uniform="p")
        zona.grid_rowconfigure(0, weight=1)

        self._panel_historial(zona, 0)
        self._panel_repetidos(zona, 1)
        self._panel_log(zona, 2)

    def _caja_texto(self, padre, titulo, alto=8):
        marco = tk.Frame(padre, bg=PANEL, padx=8, pady=6, highlightthickness=1,
                         highlightbackground="#2c2c2c")
        tk.Label(marco, text=titulo, bg=PANEL, fg=ORO, font=self.f_peq,
                 anchor="w").pack(fill="x")
        txt = tk.Text(marco, bg="#101010", fg=TEXTO, font=self.f_txt,
                      relief="flat", bd=0, padx=6, pady=4, height=alto,
                      highlightthickness=0)
        txt.pack(fill="both", expand=True)
        return marco, txt

    def _panel_historial(self, padre, col):
        marco, txt = self._caja_texto(padre, "HISTORIAL", alto=6)
        marco.grid(row=0, column=col, sticky="nsew", padx=(0, 6), pady=6)
        txt.tag_configure("rojo", foreground="#ff6b6b")
        txt.tag_configure("negro", foreground="#ffffff")
        txt.tag_configure("verde", foreground="#4caf50")
        txt.configure(state="disabled")
        self.txt_historial = txt

    def _panel_repetidos(self, padre, col):
        marco, txt = self._caja_texto(padre, "REPETIDOS EN ESTA JUGADA", alto=6)
        marco.grid(row=0, column=col, sticky="nsew", padx=6, pady=6)
        txt.configure(state="disabled")
        txt.insert("end", "Ninguno todavía")
        txt.configure(state="disabled")
        self.txt_repetidos = txt

    def _panel_log(self, padre, col):
        marco, txt = self._caja_texto(padre, "RESULTADOS", alto=6)
        marco.grid(row=0, column=col, sticky="nsew", padx=(6, 0), pady=6)
        txt.configure(state="disabled")
        self.txt_log = txt

    def _marco_mesa(self, padre):
        contenedor = tk.Frame(padre, bg=FONDO)
        contenedor.grid(row=3, column=0, sticky="nsew", padx=14, pady=(2, 8))
        contenedor.grid_columnconfigure(0, weight=1)
        contenedor.grid_rowconfigure(0, weight=1)

        self.mesa = tk.Frame(contenedor, bg=FONDO)
        self.mesa.grid(row=0, column=0, sticky="nsew")

        cero = self._celda(self.mesa, "0", "0", VERDE)
        cero.grid(row=0, column=0, rowspan=3, sticky="nsew")

        for i, fila in enumerate(FILAS):
            for j, num in enumerate(fila):
                bg = ROJO_BG if num in ROJO else NEGRO_BG
                cel = self._celda(self.mesa, str(num), str(num), bg)
                cel.grid(row=i, column=1 + j, sticky="nsew")
            self._celda(self.mesa, "2:1", f"col{i+1}", AZUL
                        ).grid(row=i, column=13, sticky="nsew")

        docenas = [("1-12", "dozen1"), ("13-24", "dozen2"), ("25-36", "dozen3")]
        for i, (texto, loc) in enumerate(docenas):
            self._celda(self.mesa, texto, loc, AZUL
                        ).grid(row=3, column=1 + i * 4, columnspan=4, sticky="nsew")

        externas = [("1-18", "1-18", GRIS), ("PAR", "par", GRIS),
                    ("ROJO", "rojo", ROJO_BG), ("NEGRO", "negro", NEGRO_BG),
                    ("IMPAR", "impar", GRIS), ("19-36", "19-36", GRIS)]
        for i, (texto, loc, bg) in enumerate(externas):
            self._celda(self.mesa, texto, loc, bg
                        ).grid(row=4, column=1 + i * 2, columnspan=2, sticky="nsew")

        for c in range(14):
            self.mesa.grid_columnconfigure(c, weight=1)
        for r in range(5):
            self.mesa.grid_rowconfigure(r, weight=1)

    def _celda(self, padre, texto, loc, bg):
        marco = tk.Frame(padre, bg=bg, highlightbackground="#2b2b2b",
                         highlightthickness=1, padx=1, pady=1)
        lbl_num = tk.Label(marco, text=texto, bg=bg, fg="white", font=self.f_num,
                           width=3)
        lbl_num.pack(fill="both", expand=True)
        lbl_mon = tk.Label(marco, text=" ", bg=bg, fg=ORO, font=self.f_mon)
        lbl_mon.pack(fill="x")
        lbl_est = tk.Label(marco, text="", bg=bg, fg="#ffd700", font=self.f_est)
        lbl_est.pack(fill="x")
        for w in (marco, lbl_num, lbl_mon, lbl_est):
            w.bind("<Button-1>", lambda e, l=loc: self._agregar_apuesta(l))
            w.bind("<Button-3>", lambda e, l=loc: self._quitar_apuesta(l))
        self.celdas[loc] = (marco, lbl_mon, lbl_est)
        return marco

    def _barra_fichas(self, padre):
        bar = tk.Frame(padre, bg=FONDO)
        bar.grid(row=4, column=0, sticky="ew", pady=(0, 6))
        for valor in VALORES_FICHAS:
            can = tk.Canvas(bar, bg=FONDO, highlightthickness=0)
            can.pack(side="left", padx=5)
            can.bind("<Button-1>", lambda e, v=valor: self._set_chip(v))
            self.col_fichas.append((valor, can))

    def _btn_nueva(self, padre):
        frame = tk.Frame(padre, bg=FONDO)
        frame.grid(row=5, column=0, sticky="ew", padx=14, pady=(0, 12))
        botones = tk.Frame(frame, bg=FONDO)
        botones.pack(fill="x")
        tk.Button(botones, text="NUEVA RONDA", command=self._nueva_ronda,
                  font=self.f_btn, bg="#9c1010", fg="white", relief="flat", bd=0,
                  padx=10, pady=6, activebackground="#b31414", cursor="hand2",
                  ).pack(side="left", fill="both", expand=True, padx=(0, 3))
        tk.Button(botones, text="NUEVA RONDA CON ÚLTIMAS RONDAS",
                  command=self._nueva_ronda_rapida,
                  font=self.f_btn, bg="#7a4d1a", fg="white", relief="flat", bd=0,
                  padx=10, pady=6, activebackground="#955d1f", cursor="hand2",
                  ).pack(side="left", fill="both", expand=True, padx=(3, 0))

    def _dibujar_fichas(self):
        r = max(13, int(21 * self._s))
        for valor, can in self.col_fichas:
            d = r * 2 + 8
            can.configure(width=d, height=d)
            can.delete("all")
            sel = (self.chip.get() == valor)
            can.create_oval(4, 4, d - 4, d - 4, fill=COLOR_FICHA[valor],
                            outline=ORO if sel else "#5a5a5a", width=3 if sel else 2)
            can.create_text(d // 2, d // 2, text=f"${valor}", fill=TEXTO_FICHA[valor],
                            font=self.f_chip)

    def _set_chip(self, valor):
        self.chip.set(valor)
        self._dibujar_fichas()

    # ---------- apuestas manuales ----------

    def _agregar_apuesta(self, loc):
        monto = self.chip.get()
        if monto <= 0:
            return
        self.bets[loc] = self.bets.get(loc, 0) + monto
        self._monito(loc)

    def _quitar_apuesta(self, loc):
        monto = self.chip.get()
        if loc in self.bets:
            self.bets[loc] = max(0, self.bets[loc] - monto)
            if self.bets[loc] == 0:
                del self.bets[loc]
            self._monito(loc)

    def _monito(self, loc):
        marco, lbl, _ = self.celdas[loc]
        monto = self.bets.get(loc, 0)
        lbl.config(text=f"${monto}" if monto else "")
        self.total_var.set(f"Total: ${sum(self.bets.values())}")

    def _limpiar_apuestas(self):
        self.bets = {}
        for marco, lbl, _ in self.celdas.values():
            lbl.config(text="")
        self.total_var.set("Total: $0")

    # ---------- estrategia 3 repeticiones ----------

    def _apl_banca(self):
        try:
            self.saldo = int(self.banca.get())
        except ValueError:
            messagebox.showerror("Error", "Banca inválida.")
            return
        self._cinta()
        self._log(f"Banca establecida en ${self.saldo}")

    def _marcar(self, n):
        marco, _, lbl = self.celdas[str(n)]
        lbl.config(text=f"R{int(self.estrategia[n])}")

    def _desmarcar(self):
        for loc in self.estrategia:
            self.celdas[str(loc)][2].config(text="")

    def _radicar_al_marcar(self):
        for loc, unidad in self.estrategia.items():
            self.celdas[str(loc)][2].config(text=f"R{int(unidad)}")

    def _reiniciar_conteo(self):
        self.perdida = 0
        self._cinta()
        self._log("Conteo de pérdidas reiniciado. Puedes seguir jugando la jugada.")

    def _fin_juego(self):
        self._desmarcar()
        self.estrategia = {}
        self.juego_count = {}
        self.perdida = 0
        self.unidad = 1
        self.juego_tiros = 0
        self.fase = "obs"
        self._actualizar_repetidos()
        self._cinta()
        self._log("NUEVA JUGADA: observa y apunta los números (sin apostar).")

    def _registrar(self):
        texto = self.entry_num.get().strip()
        if not texto:
            return
        try:
            n = int(texto)
        except ValueError:
            messagebox.showerror("Error", "Ingresa un número válido.")
            return
        if n < 0 or n > 36:
            messagebox.showerror("Error", "El número debe estar entre 0 y 36.")
            return

        self.entry_num.delete(0, "end")
        self.historial.append(n)
        self.tiros_var.set(f"Tiros: {len(self.historial)}")
        self.juego_tiros += 1

        color = "rojo" if n in ROJO else ("negro" if n in NEGRO else "verde")
        self._agregar_historial(n, color)
        self._resaltar(str(n))
        self._procesar_jugada(n)
        self._actualizar_repetidos()
        self._cinta()
        self.entry_num.focus_set()

    def _procesar_jugada(self, n):
        c = self.juego_count.get(n, 0) + 1
        self.juego_count[n] = c
        activos = list(self.estrategia)

        if c >= 3 and n in activos:
            N = len(activos)
            ganancia = (36 - N) * self.unidad - self.perdida
            self.beneficio += ganancia
            self._log(f"¡¡3ª repetición del {n}!! Ganas +${ganancia} "
                      f"(pleno {self.unidad} ficha(s), {N} números, pérdida previa "
                      f"{self.perdida} ficha(s)). Beneficio total: ${self.beneficio}.")
            self._fin_juego()
            return

        if self.fase == "jug" and activos:
            self.perdida += len(activos) * self.unidad

        if c == 2:
            self.estrategia[n] = self.unidad
            self.fase = "jug"
            self._marcar(n)
            self._log(f"¡{n} se repite! Añades {n} a las apuestas (ficha {self.unidad}). "
                      f"Va {len(self.estrategia)} número(s) apostados.")

        self._ajustar_nivel()

    def _limite_perdida(self):
        N = len(self.estrategia)
        if N <= 0:
            return None
        return self.unidad * (36 - N) - 12

    def _ajustar_nivel(self):
        cambio = False
        while self.estrategia:
            limite = self._limite_perdida()
            if limite is None or self.perdida <= limite:
                break
            self.unidad += 1
            self.estrategia = {k: self.unidad for k in self.estrategia}
            self._radicar_al_marcar()
            cambio = True
            self._log(f"Pérdida {self.perdida} ficha(s): la próxima apuesta superaría "
                      f"el límite (-{limite}). Sumas 1 ficha -> {self.unidad} ficha(s) "
                      f"por número.")
        if cambio:
            self._cinta()

    # ---------- botones y limpieza ----------

    def _limpiar(self):
        self._desmarcar()
        self.bets = {}
        self.historial = []
        self.estrategia = {}
        self.juego_count = {}
        self.perdida = 0
        self.unidad = 1
        self.juego_tiros = 0
        self.fase = "obs"
        for marco, lbl, _ in self.celdas.values():
            lbl.config(text="")
        if self.ultima_celda and self.ultima_celda in self.celdas:
            self.celdas[self.ultima_celda][0].config(
                highlightbackground="#2b2b2b", highlightthickness=1)
        self.ultima_celda = None
        for w in (self.txt_historial, self.txt_log):
            w.configure(state="normal")
            w.delete("1.0", "end")
            w.configure(state="disabled")

    def _nueva_ronda(self):
        if not messagebox.askyesno("Nueva ronda",
                                   "¿Reiniciar toda la sesión (apuestas, historial, "
                                   "jugada y beneficios)?"):
            return
        self.beneficio = 0
        self._limpiar()
        self.tiros_var.set("Tiros: 0")
        self.total_var.set("Total: $0")
        self.txt_repetidos.configure(state="normal")
        self.txt_repetidos.delete("1.0", "end")
        self.txt_repetidos.insert("end", "Ninguno todavía")
        self.txt_repetidos.configure(state="disabled")
        self._cinta()
        self._log("Nueva sesión. Observa y apunta los números.")

    def _nueva_ronda_rapida(self):
        cola = list(self.historial[-15:])
        if not cola:
            self._nueva_ronda()
            return
        if not messagebox.askyesno(
                "Nueva ronda con últimas rondas",
                f"¿Empezar nueva ronda conservando los últimos {len(cola)} números "
                f"y sus repeticiones?"):
            return
        self.beneficio = 0
        self._limpiar()
        self.historial = cola
        self.tiros_var.set(f"Tiros: {len(self.historial)}")
        self.total_var.set("Total: $0")
        for n in cola:
            tag = "rojo" if n in ROJO else ("negro" if n in NEGRO else "verde")
            self._agregar_historial(n, tag)
        for n in cola:
            self.juego_count[n] = self.juego_count.get(n, 0) + 1
        heredados = []
        for n, c in self.juego_count.items():
            if c >= 2:
                self.estrategia[n] = self.unidad
                self._marcar(n)
                heredados.append(str(n))
        self.fase = "jug" if self.estrategia else "obs"
        self._actualizar_repetidos()
        self._cinta()
        self._log(f"Nueva ronda rápida: conservados {len(cola)} números. "
                  f"Repetidos heredados: {', '.join(heredados) or 'ninguno'}.")

    # ---------- paneles dinámicos ----------

    def _actualizar_repetidos(self):
        repetidos = [(n, c) for n, c in self.juego_count.items() if c >= 2]
        repetidos.sort(key=lambda x: (-x[1], x[0]))
        self.txt_repetidos.configure(state="normal")
        self.txt_repetidos.delete("1.0", "end")
        if repetidos:
            for n, c in repetidos:
                sufijo = "  <- ¡3ª!" if n in self.estrategia and c >= 3 else ""
                self.txt_repetidos.insert("end", f"{n:>3}  ->  {c} veces{sufijo}\n")
        else:
            self.txt_repetidos.insert("end", "Ninguno todavía")
        self.txt_repetidos.configure(state="disabled")

    def _cinta(self):
        if self.fase == "obs":
            self.fase_var.set(f"OBSERVANDO (giro {self.juego_tiros})")
            self.val_fase.config(fg=ORO if self.juego_tiros < 9 else "#ff5252")
            if self.juego_tiros >= 9 and self.juego_tiros <= 20:
                self.fase_var.set(f"OBSERVANDO · zona amarilla (giro {self.juego_tiros})")
        else:
            self.fase_var.set("JUGANDO")
            self.val_fase.config(fg="#4caf50")

        self.apuestas_var.set(", ".join(str(k) for k in self.estrategia) or "—")
        limite = self._limite_perdida()
        if limite is None:
            self.perdida_var.set(f"-{self.perdida} ficha(s)")
            self.lbl_perdida.config(fg=TEXTO)
        else:
            self.perdida_var.set(f"-{self.perdida} / límite -{limite}")
            if self.perdida >= limite * 0.75:
                self.lbl_perdida.config(fg="#ff5252")
            else:
                self.lbl_perdida.config(fg=TEXTO)
        self.unidad_var.set(f"{self.unidad} ficha(s)")
        self.saldo_var.set(f"${self.saldo + self.beneficio}")
        self.benef_var.set(f"+${self.beneficio}")

    def _agregar_historial(self, n, tag):
        self.txt_historial.configure(state="normal")
        self.txt_historial.insert("1.0", f"{n:>3}\n", tag)
        self.txt_historial.configure(state="disabled")

    def _log(self, msj):
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", msj + "\n")
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")

    def _resaltar(self, loc):
        if self.ultima_celda and self.ultima_celda in self.celdas:
            self.celdas[self.ultima_celda][0].config(
                highlightbackground="#2b2b2b", highlightthickness=1)
        self.celdas[loc][0].config(highlightbackground=ORO, highlightthickness=3)
        self.ultima_celda = loc

    def _on_configure(self, e):
        if not hasattr(self, "content"):
            return
        w, h = e.width, e.height
        s = min(w / BASE_W, h / BASE_H)
        s = max(0.55, min(1.8, s))
        if abs(s - self._s) < 0.03:
            return
        self._s = s
        for f, base in self.fonts:
            f.configure(size=max(6, int(round(base * s))))
        self._dibujar_fichas()


def main():
    root = tk.Tk()
    RuletaApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()