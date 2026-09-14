from ruleta.constantes import CORNERES, _NUM_CORNERES, _nom_corner


class EstrategiaCorners:
    """Lógica de la estrategia "12 Corners" (sin dependencia de Qt)."""

    def __init__(self, banca=200):
        self.banca = banca
        self.dinero = banca
        self.saldo = 0
        self.mejor = 0
        self.activos = {}
        self.fase = "pre"
        self.historial = []
        self.juego_tiros = 0
        self.incluir_cero = True
        self.ultimo_corner = None
        self.chip = 500

    # ------------------------------------------------------------------
    # configuración
    # ------------------------------------------------------------------

    def set_banca(self, valor):
        self.banca = valor
        self.dinero = valor
        return ("Banca establecida en %d fichas. Tu dinero actual es "
                "$%d." % (valor, valor))

    def set_incluir_cero(self, v):
        self.incluir_cero = bool(v)
        return "Cero %s del juego." % ("incluido" if self.incluir_cero
                                       else "excluido")

    def set_chip(self, valor):
        self.chip = valor

    # ------------------------------------------------------------------
    # selección de corners
    # ------------------------------------------------------------------

    def _candidatos(self, n):
        ids = list(_NUM_CORNERES.get(n, []) or [])
        if not self.incluir_cero:
            ids = [c for c in ids if c != "C0"]
        return ids

    def _elegir(self, n):
        cand = self._candidatos(n)
        nuevos = [c for c in cand if c not in self.activos]
        if nuevos:
            return nuevos[0]
        return cand[0] if cand else None

    def ficha_nivel(self, k=None):
        k = len(self.activos) if k is None else k
        return 1 if k <= 2 else k - 1

    @property
    def apuesta_total(self):
        return sum(self.activos.values())

    def _add_corner(self, cid):
        k = len(self.activos) + 1
        if k <= 2:
            self.activos[cid] = 1
        else:
            self.activos[cid] = k - 2
            self.activos = {c: v + 1 for c, v in self.activos.items()}

    def _incrementar(self):
        self.activos = {c: v + 1 for c, v in self.activos.items()}

    # ------------------------------------------------------------------
    # núcleo de la estrategia
    # ------------------------------------------------------------------

    def registrar_numero(self, n):
        self.historial.append(n)
        self.juego_tiros += 1
        return self.procesar_numero(n)

    def procesar_numero(self, n):
        logs = []

        if self.fase == "pre":
            cand = self._elegir(n)
            if cand is None:
                logs.append("Sale %d: no hay corner para cubrirlo "
                            "(marca 'Incluir 0-1-2-3' para apostar el cero). "
                            "Se sigue esperando el primer número." % n)
                return logs
            self.activos[cand] = 1
            self.fase = "jug"
            self.ultimo_corner = cand
            logs.append("Primer número %d → apuestas %d ficha en %s. "
                        "CICLO INICIADO." % (n, 1, _nom_corner(cand)))
            return logs

        wins = [c for c in self.activos if n in CORNERES[c]]
        total = self.apuesta_total

        if wins:
            premio = sum(self.activos[c] * 9 for c in wins)
            neto = premio - total
            self.saldo += neto
            self.dinero += neto * self.chip
            anterior = self.mejor
            self.mejor = max(self.mejor, self.saldo)
            doble = " doble" if len(wins) > 1 else ""
            msj = ("¡Sale %d! Acierto%s: premio %d − puesta %d = +%d. "
                   "Saldo %d (mejor %d)."
                   % (n, doble, premio, total, neto, self.saldo, self.mejor))
            if self.saldo >= anterior:
                base = self._elegir(n)
                if base is not None:
                    self.activos = {base: 1}
                    self.ultimo_corner = base
                    msj += (" Alcanzado el mejor saldo → puesta base en %s "
                            "(1 ficha)." % _nom_corner(base))
                else:
                    self.activos = {}
                    self.fase = "pre"
                    self.ultimo_corner = None
                    msj += (" Mejor saldo alcanzado → nueva puesta base: "
                            "registra el número que quieras.")
            else:
                self.ultimo_corner = wins[0]
                msj += (" Aún no recuperas el mejor saldo → mantienes la "
                        "puesta ganadora (sin reducir).")
            logs.append(msj)
            return logs

        self.saldo -= total
        self.dinero -= total * self.chip
        logs.append("Sale %d: pierdes %d. Saldo %d (mejor %d)."
                    % (n, total, self.saldo, self.mejor))
        cand = self._elegir(n)
        self.ultimo_corner = cand
        if cand is not None and cand not in self.activos:
            self._add_corner(cand)
            k = len(self.activos)
            logs.append("Añades corner %s y subes 1 ficha a todos → nivel %d "
                        "(%d ficha(s) por corner, %d en total)."
                        % (_nom_corner(cand), k, self.ficha_nivel(k),
                           self.apuesta_total))
        elif self.activos:
            self._incrementar()
            k = len(self.activos)
            logs.append("Sale %d: su corner ya estaba apostado. Subes 1 ficha "
                        "a todos → nivel %d (%d ficha(s) por corner, %d "
                        "total)." % (n, k, self.ficha_nivel(k),
                                     self.apuesta_total))
        else:
            logs.append("No hay corners activos. Registra el siguiente "
                        "número.")
        return logs

    # ------------------------------------------------------------------
    # acciones globales
    # ------------------------------------------------------------------

    def retirar(self):
        self.activos = {}
        self.fase = "pre"
        self.ultimo_corner = None
        return ("Ciclo cerrado. Saldo %d (mejor %d). Registra un número "
                "para empezar un nuevo ciclo." % (self.saldo, self.mejor))

    def nueva_ronda(self):
        self.saldo = 0
        self.mejor = 0
        self.activos = {}
        self.fase = "pre"
        self.ultimo_corner = None
        self.historial = []
        self.juego_tiros = 0
        return ["Nueva sesión. Registra un número para escoger el primer "
                "corner."]

    # ------------------------------------------------------------------
    # estado para la vista
    # ------------------------------------------------------------------

    def estado(self):
        return {
            "fase": self.fase,
            "saldo": self.dinero,
            "saldo_fichas": self.saldo,
            "beneficio": self.dinero - self.banca,
            "mejor": self.mejor,
            "activos": dict(self.activos),
            "incluir_cero": self.incluir_cero,
            "juego_tiros": self.juego_tiros,
            "tiros": len(self.historial),
            "banca": self.banca,
            "ficha_nivel": self.ficha_nivel(),
            "apuesta_total": self.apuesta_total,
            "ultimo_corner": self.ultimo_corner,
            "chip": self.chip,
        }