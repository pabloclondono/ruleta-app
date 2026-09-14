class EstrategiaTresRepeticiones:
    """Lógica de la estrategia "3 Repeticiones" (sin dependencia de Qt)."""

    def __init__(self, banca=200):
        self.banca = banca
        self.saldo = banca
        self.beneficio = 0
        self.unidad = 1
        self.perdida = 0
        self.juego_tiros = 0
        self.fase = "obs"
        self.juego_count = {}
        self.estrategia = {}
        self.historial = []
        self.bets = {}
        self.chip = 500

    # ------------------------------------------------------------------
    # apuestas manuales
    # ------------------------------------------------------------------

    def set_chip(self, valor):
        self.chip = valor

    def agregar_apuesta(self, loc):
        if self.chip <= 0:
            return
        self.bets[loc] = self.bets.get(loc, 0) + self.chip

    def quitar_apuesta(self, loc):
        if loc in self.bets:
            self.bets[loc] = max(0, self.bets[loc] - self.chip)
            if self.bets[loc] == 0:
                del self.bets[loc]

    def limpiar_apuestas(self):
        self.bets = {}

    # ------------------------------------------------------------------
    # banca / conteo
    # ------------------------------------------------------------------

    def set_banca(self, valor):
        self.banca = valor
        self.saldo = valor
        return "Banca establecida en $%d" % valor

    def reiniciar_conteo(self):
        self.perdida = 0
        self.unidad = 1
        self.estrategia = {k: 1 for k in self.estrategia}
        return ("Conteo de pérdidas reiniciado: vuelves a pagar 1 ficha "
                "por número. Puedes seguir jugando la jugada.")

    # ------------------------------------------------------------------
    # núcleo de la estrategia
    # ------------------------------------------------------------------

    def registrar_numero(self, n):
        self.historial.append(n)
        self.juego_tiros += 1
        return self.procesar_numero(n)

    def procesar_numero(self, n):
        logs = []
        c = self.juego_count.get(n, 0) + 1
        self.juego_count[n] = c
        activos = list(self.estrategia)

        if c >= 3 and n in activos:
            fichas_ganadas = self.unidad * 36
            moneda = self.chip
            ganancia = fichas_ganadas * moneda
            self.saldo += ganancia
            self.beneficio += ganancia
            logs.append("¡¡3ª repetición del %d!! Apostabas %d ficha(s) por "
                        "número → ganas %d × 36 = %d ficha(s), multiplicado "
                        "por la ficha de $%d = +$%d. Beneficio total: $%d. "
                        "Saldo: $%d." %
                        (n, self.unidad, self.unidad, fichas_ganadas, moneda,
                         ganancia, self.beneficio, self.saldo))
            self._fin_juego()
            logs.append("NUEVA JUGADA: observa y apunta los números "
                        "(sin apostar).")
            return logs

        if self.fase == "jug" and activos:
            self.perdida += len(activos) * self.unidad
            self.saldo -= len(activos) * self.unidad * self.chip

        if c == 2:
            self.estrategia[n] = self.unidad
            self.fase = "jug"
            logs.append("¡%d se repite! Añades %d a las apuestas (ficha %d). "
                        "Va %d número(s) apostados." %
                        (n, n, self.unidad, len(self.estrategia)))

        logs.extend(self._ajustar_nivel())
        return logs

    def limite_perdida(self):
        N = len(self.estrategia)
        if N <= 0:
            return None
        return self.unidad * (36 - N) - 12

    def _ajustar_nivel(self):
        logs = []
        while self.estrategia:
            limite = self.limite_perdida()
            if limite is None or self.perdida <= limite:
                break
            self.unidad += 1
            self.estrategia = {k: self.unidad for k in self.estrategia}
            logs.append("Pérdida %d ficha(s): la próxima apuesta superaría "
                        "el límite (-%d). Sumas 1 ficha -> %d ficha(s) "
                        "por número." % (self.perdida, limite, self.unidad))
        return logs

    def _fin_juego(self):
        self.estrategia = {}
        self.juego_count = {}
        self.perdida = 0
        self.unidad = 1
        self.juego_tiros = 0
        self.fase = "obs"

    def _reset_sesion(self):
        self._fin_juego()
        self.bets = {}
        self.historial = []

    # ------------------------------------------------------------------
    # rondas
    # ------------------------------------------------------------------

    def nueva_ronda(self):
        self._reset_sesion()
        return ["Nueva sesión. Observa y apunta los números."]

    def ultimas_rondas(self):
        return list(self.historial[-15:])

    def nueva_ronda_rapida(self, cola):
        self._reset_sesion()
        self.historial = cola
        for n in cola:
            self.juego_count[n] = self.juego_count.get(n, 0) + 1
        heredados = []
        for n, c in self.juego_count.items():
            if c >= 2:
                self.estrategia[n] = self.unidad
                heredados.append(str(n))
        self.fase = "jug" if self.estrategia else "obs"
        logs = ["Nueva ronda rápida: conservados %d números. "
                "Repetidos heredados: %s." %
                (len(cola), ", ".join(heredados) or "ninguno")]
        return logs

    # ------------------------------------------------------------------
    # estado para la vista
    # ------------------------------------------------------------------

    def estado(self):
        return {
            "fase": self.fase,
            "juego_tiros": self.juego_tiros,
            "tiros": len(self.historial),
            "estrategia": dict(self.estrategia),
            "perdida": self.perdida,
            "limite": self.limite_perdida(),
            "unidad": self.unidad,
            "banca": self.banca,
            "saldo": self.saldo,
            "beneficio": self.beneficio,
            "bets": dict(self.bets),
            "chip": self.chip,
            "juego_count": dict(self.juego_count),
        }