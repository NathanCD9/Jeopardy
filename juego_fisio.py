# =========================
# CONSTANTES LÓGICAS DEL JUEGO
# =========================
PUNTOS_RESPUESTA_CORRECTA = 10
TIEMPO_PREGUNTA_SEGUNDOS = 21 

import customtkinter as ctk
import colorsys
import ctypes
import random
import json
import os
import sys

# Configuración de DPI
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

def recurso_ruta(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ================================================================
# LISTA DE TEMAS
# ================================================================
TEMAS_FIJOS = [
    "LÍQUIDOS Y ELECTRÓLITOS", 
    "SISTEMA ARTICULAR",
    "FISIOLOGÍA MUSCULAR", 
    "SISTEMA CARDIOVASCULAR",
    "NEUROFISIOLOGÍA", 
    "COAGULACIÓN Y HEMOFILIA",
    "FISIOLOGÍA RENAL", 
    "FISIOLOGÍA DE LA PIEL",
    "FISIOLOGÍA GASTROINTESTINAL" 
]

ARCHIVO_PREGUNTAS = recurso_ruta("preguntas.json")
ARCHIVO_RECORDS = "highscores.json"

def cargar_banco_datos():
    banco_final = {tema: {} for tema in TEMAS_FIJOS}
    if not os.path.exists(ARCHIVO_PREGUNTAS):
        return {tema: {} for tema in TEMAS_FIJOS}
    try:
        with open(ARCHIVO_PREGUNTAS, "r", encoding="utf-8") as f:
            datos_raw = json.load(f)
            for tema, contenido in datos_raw.items():
                if tema in TEMAS_FIJOS:
                    for clave, valor in contenido.items():
                        col, pts = map(int, clave.split(','))
                        banco_final[tema][(col, pts)] = tuple(valor)
            return banco_final
    except:
        return {tema: {} for tema in TEMAS_FIJOS}

BANCO_DATOS = cargar_banco_datos()
MAPA_MAESTRO = {tema: {} for tema in TEMAS_FIJOS}
MAPA_MAESTRO["THE CHALLENGE"] = {}

preguntas_completadas = {}
jugadores = []
turno_actual = 0
meta_score = 0

# ================================================================
# COMPONENTES VISUALES
# ================================================================

class TextoRGB(ctk.CTkCanvas):
    def __init__(self, master, text, fsize=24, height=70, command=None, border=False, font_name="Arial"):
        super().__init__(master, height=height, highlightthickness=0, bd=0, bg="#000000")
        self.text, self.fsize, self.command = text, fsize, command
        self.border, self.font_name = border, font_name
        self.hue, self.click_count = 0, 0
        if self.command or self.text == "Definitive Neon Edition": 
            self.configure(cursor="hand2")
            self.bind("<Button-1>", self.al_hacer_click)
        self.animar()

    def al_hacer_click(self, event):
        if self.text == "Definitive Neon Edition":
            self.click_count += 1
            if self.click_count >= 5:
                if os.path.exists(ARCHIVO_RECORDS): os.remove(ARCHIVO_RECORDS)
                self.configure(bg="white")
                self.after(100, lambda: self.configure(bg="black"))
                self.click_count = 0
        if self.command: self.command()

    def animar(self):
        try:
            self.hue = (self.hue + 0.01) % 1.0
            r, g, b = colorsys.hsv_to_rgb(self.hue, 1.0, 1.0)
            color = f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
            self.delete("all")
            w, h = self.winfo_width(), self.winfo_height()
            if w > 1:
                if self.border: self.create_rectangle(2, 2, w-2, h-2, outline=color, width=2)
                estilo = "normal" if self.font_name == "Brush Script MT" else "bold"
                self.create_text(w/2, h/2, text=self.text, fill=color, font=(self.font_name, self.fsize, estilo), justify="center", width=w-10)
            self.after(35, self.animar)
        except: pass

class BotonPacman(ctk.CTkCanvas):
    def __init__(self, master, text, command=None, height=110, fsize=17):
        super().__init__(master, height=height, highlightthickness=0, bd=0, cursor="hand2" if command else "arrow", bg="#000000")
        self.text, self.command, self.fsize = text, command, fsize
        self.pos_anim, self.hue = 0, 0
        if self.command: self.bind("<Button-1>", lambda e: self.command())
        self.animar()

    def animar(self):
        try:
            self.pos_anim = (self.pos_anim + 0.01) % 1.0
            self.hue = (self.hue + 0.005) % 1.0
            self.delete("all")
            w, h = self.winfo_width(), self.winfo_height()
            if w > 10:
                for x in range(0, w, 20): self.create_line(x, 0, x, h, fill="#111")
                for y in range(0, h, 20): self.create_line(0, y, w, y, fill="#111")
                r, g, b = colorsys.hsv_to_rgb(self.hue, 1.0, 1.0)
                color_neon = f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
                for i in range(12):
                    t = (self.pos_anim + (i * 0.03)) % 1.0
                    p = 2*((w-10)+(h-10)); d = t*p
                    if d < (w-10): x, y = 5+d, 5
                    elif d < (w-10)+(h-10): x, y = w-5, 5+(d-(w-10))
                    elif d < 2*(w-10)+(h-10): x, y = w-5-(d-((w-10)+(h-10))), h-5
                    else: x, y = 5, h-5-(d-(2*(w-10)+(h-10)))
                    self.create_oval(x-2, y-2, x+2, y+2, fill=color_neon, outline="")
                if self.text: self.create_text(w/2, h/2, text=self.text, fill=color_neon, font=("Impact", self.fsize), width=w-40, justify="center")
            self.after(25, self.animar)
        except: pass

class CuadroRGB(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="black", border_width=2, **kwargs)
        self.hue = 0
        self.animar()
    def animar(self):
        try:
            self.hue = (self.hue + 0.01) % 1.0
            r, g, b = colorsys.hsv_to_rgb(self.hue, 1.0, 1.0)
            self.configure(border_color=f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}')
            self.after(40, self.animar)
        except: pass

# ================================================================
# CLASE: POP-UP DE FIN DE JUEGO
# ================================================================

class PopUpFinJuego(ctk.CTkToplevel):
    def __init__(self, master, app_ref, tema_jugado):
        super().__init__(master)
        self.app_ref = app_ref
        self.tema_jugado = tema_jugado
        self.width, self.height = 800, 550
        self.geometry(f"{self.width}x{self.height}+{(self.winfo_screenwidth()//2)-(self.width//2)}+{(self.winfo_screenheight()//2)-(self.height//2)}")
        self.grab_set()
        self.configure(fg_color="#000")
        self.hue = 0
        self.title("¡RESULTADOS!")
        
        self.exito = False
        msg_titulo = ""
        msg_detalle = ""
        
        if len(jugadores) == 1:
            score = jugadores[0]['score']
            if score >= meta_score:
                self.exito = True
                msg_titulo = "¡OBJETIVO CUMPLIDO!"
                msg_detalle = f"MÓDULO: {tema_jugado}\nPUNTAJE FINAL: {score}\nMETA: {meta_score}"
            else:
                self.exito = False
                msg_titulo = "OBJETIVO NO LOGRADO"
                msg_detalle = f"MÓDULO: {tema_jugado}\nPUNTAJE FINAL: {score}\nNECESITABAS: {meta_score}"
        else:
            max_score = max(p['score'] for p in jugadores)
            ganadores = [p for p in jugadores if p['score'] == max_score]
            self.exito = True 
            if len(ganadores) == 1:
                msg_titulo = f"¡GANADOR: {ganadores[0]['nombre']}!"
                msg_detalle = f"PUNTAJE: {max_score}"
            else:
                msg_titulo = "¡EMPATE!"
                nombres_empate = " Y ".join([g['nombre'] for g in ganadores])
                msg_detalle = f"{nombres_empate}\nPUNTAJE: {max_score}"

        self.guardar_records_con_modulo()

        self.lbl_titulo = ctk.CTkLabel(self, text=msg_titulo, font=("Impact", 50), text_color="white")
        self.lbl_titulo.pack(pady=(60, 20))
        
        self.lbl_detalle = ctk.CTkLabel(self, text=msg_detalle, font=("Arial", 22, "bold"), text_color="white")
        self.lbl_detalle.pack(pady=10)
        
        ctk.CTkButton(self, text="VOLVER AL MENÚ", fg_color="#1a1a1a", border_color="white", border_width=2, 
                      font=("Impact", 20), height=50, width=200, command=self.cerrar).pack(side="bottom", pady=40)
        
        if self.exito: self.animar_fondo()
        else:
            self.configure(fg_color="#330000")
            self.lbl_titulo.configure(text_color="#FF5252")

    def guardar_records_con_modulo(self):
        records = []
        if os.path.exists(ARCHIVO_RECORDS):
            try:
                with open(ARCHIVO_RECORDS, "r") as f: records = json.load(f)
            except: pass
        
        for j in jugadores:
            if j['score'] > 0: 
                records.append({
                    "nombre": j['nombre'], 
                    "score": j['score'],
                    "modulo": self.tema_jugado
                })
        
        try:
            with open(ARCHIVO_RECORDS, "w") as f: 
                json.dump(sorted(records, key=lambda x: x['score'], reverse=True)[:5], f)
        except: pass

    def animar_fondo(self):
        try:
            self.hue = (self.hue + 0.02) % 1.0
            rgb = colorsys.hsv_to_rgb(self.hue, 0.8, 0.8) 
            color = f'#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}'
            self.configure(fg_color=color)
            self.lbl_titulo.configure(text_color="black" if self.hue > 0.5 else "white")
            self.lbl_detalle.configure(text_color="black" if self.hue > 0.5 else "white")
            self.after(50, self.animar_fondo)
        except: pass

    def cerrar(self):
        self.destroy()
        self.app_ref.menu()

# ================================================================
# APLICACIÓN PRINCIPAL
# ================================================================

class JeopardyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Jeopardy!")
        self.configure(fg_color="black")
        self.after(0, lambda: self.state('zoomed'))
        self.main_container = ctk.CTkFrame(self, fg_color="black")
        self.main_container.pack(fill="both", expand=True)
        self.pedir_jugadores()

    def pedir_jugadores(self):
        global preguntas_completadas, turno_actual, jugadores, meta_score
        preguntas_completadas, turno_actual, jugadores, meta_score = {}, 0, [], 0
        for w in self.main_container.winfo_children(): w.destroy()
        BotonPacman(self.main_container, "JEOPARDY DE FISIOLOGÍA", height=120, fsize=45).pack(fill="x", padx=100, pady=(30, 0))
        TextoRGB(self.main_container, "Definitive Neon Edition", fsize=28, height=50, font_name="Brush Script MT").pack(pady=(5, 5))
        ctk.CTkButton(self.main_container, text="🏆 HALL OF FAME 🏆", fg_color="#1a1a1a", border_width=1, border_color="#FFD700", font=("Arial", 14, "bold"), command=self.mostrar_hall).pack(pady=5)
        box = CuadroRGB(self.main_container); box.pack(pady=20, padx=100)
        grid = ctk.CTkFrame(box, fg_color="transparent"); grid.pack(pady=20, padx=40)
        self.entries = []
        for i in range(4):
            r, c = divmod(i, 2)
            e = ctk.CTkEntry(grid, placeholder_text=f"JUGADOR {i+1}", width=280, height=45, font=("Arial", 18, "bold"), fg_color="#000", text_color="white", justify="center", border_color="#333")
            e.grid(row=r, column=c, padx=15, pady=10)
            self.entries.append(e)
        
        TextoRGB(box, "INICIAR JUEGO", fsize=22, height=70, command=self.iniciar, border=True).pack(pady=(10, 5), padx=100, fill="x")
        TextoRGB(box, "SALIR DEL JUEGO", fsize=22, height=70, command=self.destroy, border=True).pack(pady=(5, 25), padx=100, fill="x")

    def mostrar_hall(self):
        for w in self.main_container.winfo_children(): w.destroy()
        BotonPacman(self.main_container, "HALL OF FAME", height=100, fsize=35).pack(fill="x", pady=20)
        frame_records = CuadroRGB(self.main_container); frame_records.pack(pady=20, padx=100, fill="both", expand=True)
        if os.path.exists(ARCHIVO_RECORDS):
            with open(ARCHIVO_RECORDS, "r") as f:
                records = sorted(json.load(f), key=lambda x: x['score'], reverse=True)
                for i, rec in enumerate(records[:5]):
                    col = "#FFD700" if i == 0 else "#C0C0C0" if i == 1 else "#CD7F32" if i == 2 else "white"
                    nombre = rec['nombre']
                    puntos = rec['score']
                    modulo = rec.get('modulo', 'GENERAL') 
                    texto_record = f"{i+1}º {nombre} ({modulo}) --- {puntos} PTS"
                    ctk.CTkLabel(frame_records, text=texto_record, font=("Impact", 30), text_color=col).pack(pady=10)
        ctk.CTkButton(self.main_container, text="VOLVER", font=("Impact", 20), command=self.pedir_jugadores).pack(pady=20)

    def iniciar(self):
        global jugadores
        jugadores = [{'nombre': e.get().upper(), 'score': 0} for e in self.entries if e.get().strip()]
        if not jugadores: return
        self.menu_dificultad() if len(jugadores) == 1 else self.menu()

    def menu_dificultad(self):
        for w in self.main_container.winfo_children(): w.destroy()
        BotonPacman(self.main_container, "ELIGE TU DIFICULTAD", height=100, fsize=35).pack(fill="x", padx=100, pady=20)
        box = CuadroRGB(self.main_container); box.pack(pady=20, padx=100)
        for name, meta in [("ASPIRANTE", 2500), ("ESTUDIOSO", 3750), ("DESTACADO", 4400), ("MASTER", 4900)]:
            TextoRGB(box, name, fsize=28, height=80, border=True, command=lambda m=meta: [globals().update(meta_score=m), self.menu()]).pack(pady=10, padx=50, fill="x")

    def menu(self):
        for w in self.main_container.winfo_children(): w.destroy()
        BotonPacman(self.main_container, "MENÚ DE MÓDULOS", height=90, fsize=32).pack(fill="x", padx=100, pady=(15, 5))
        grid = ctk.CTkFrame(self.main_container, fg_color="transparent"); grid.pack(fill="both", expand=True, padx=80, pady=(10, 80))
        
        for i, t in enumerate(TEMAS_FIJOS):
            BotonPacman(grid, t, command=lambda x=t: [self.preparar_tablero(x), self.ir_a(x)]).grid(row=i//3, column=i%3, padx=8, pady=8, sticky="nsew")
        
        BotonPacman(grid, "THE CHALLENGE", command=self.preparar_challenge).grid(row=3, column=1, padx=8, pady=8, sticky="nsew")
        TextoRGB(self.main_container, "TERMINAR PARTIDA", fsize=18, height=60, command=self.terminar, border=True).place(relx=0.08, rely=0.88, relwidth=0.22)

    def preparar_tablero(self, t):
        preg_tema = BANCO_DATOS.get(t, {})
        pool_por_nivel = {p: [] for p in [100, 200, 300, 400]}
        for (c, p), data in preg_tema.items():
            pool_por_nivel[p].append(data)
        
        nuevo_mapa = {}
        for p, lista in pool_por_nivel.items():
            random.shuffle(lista)
            for c in range(5):
                if c < len(lista):
                    nuevo_mapa[(c, p)] = lista[c]
        MAPA_MAESTRO[t] = nuevo_mapa

    def preparar_challenge(self):
        pool_global = {p: [] for p in [100, 200, 300, 400]}
        for tema_data in BANCO_DATOS.values():
            for (c, p), data in tema_data.items():
                if "PREGUNTA AQUÍ" not in data[0]:
                    pool_global[p].append(data)
        
        nuevo_mapa_challenge = {}
        for p in [100, 200, 300, 400]:
            lista_puntos = pool_global[p]
            random.shuffle(lista_puntos)
            for c in range(5):
                if c < len(lista_puntos):
                    nuevo_mapa_challenge[(c, p)] = lista_puntos[c]
                else:
                    nuevo_mapa_challenge[(c, p)] = ("Pregunta no disponible", "N/A")
        
        MAPA_MAESTRO["THE CHALLENGE"] = nuevo_mapa_challenge
        self.ir_a("THE CHALLENGE")

    def ir_a(self, t):
        for w in self.main_container.winfo_children(): w.destroy()
        FrameModulo(self.main_container, t, self).pack(fill="both", expand=True)

    def terminar(self):
        self.pedir_jugadores()

# ================================================================
# TABLERO DE JUEGO (FRAME MODULO)
# ================================================================

class FrameModulo(ctk.CTkFrame):
    def __init__(self, master, tema, app_ref):
        super().__init__(master, fg_color="#000")
        self.tema, self.app_ref = tema, app_ref
        
        h = ctk.CTkFrame(self, fg_color="transparent")
        h.pack(fill="x", padx=20, pady=10)
        
        for i in range(len(jugadores)):
            h.columnconfigure(i, weight=1)
            
        for i, j in enumerate(jugadores):
            f = ctk.CTkFrame(h, fg_color="transparent")
            f.grid(row=0, column=i, sticky="nsew", padx=5)
            TextoRGB(f, f"{j['nombre']}\n{j['score']}", fsize=28, height=80).pack()
            if len(jugadores) == 1: 
                ctk.CTkLabel(f, text=f"META: {meta_score}", font=("Impact", 18), text_color="#FFD700").pack()

        if len(jugadores) > 1:
            ctk.CTkLabel(self, text=f"TURNO DE: {jugadores[turno_actual]['nombre']}", font=("Impact", 35), text_color="#B71C1C").pack(pady=5)
        
        grid = ctk.CTkFrame(self, fg_color="#050505"); grid.pack(expand=True, fill="both", padx=60, pady=5)
        cols = ["#0D47A1", "#B71C1C", "#1B5E20", "#4A148C", "#E65100"]
        
        for c in range(5):
            grid.grid_columnconfigure(c, weight=1)
            for r, p in enumerate([100, 200, 300, 400]):
                grid.grid_rowconfigure(r, weight=1)
                st = preguntas_completadas.get((tema, c, p))
                txt = "✓" if st == 'check' else "X" if st == 'fail' else str(p)
                # MODIFICADO: state siempre es 'normal' para permitir revisión
                btn = ctk.CTkButton(grid, text=txt, font=("Impact", 55), 
                                  fg_color=cols[c] if not st else "#222", 
                                  corner_radius=0, border_width=4, border_color="#000", 
                                  state="normal", 
                                  command=lambda col=c, pts=p: self.abrir_p(col, pts))
                btn.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")
        
        def reset_scores_and_back():
            preguntas_completadas.clear()
            for j in jugadores: j['score'] = 0
            self.app_ref.menu()

        TextoRGB(self, "<< VOLVER AL MENÚ >>", fsize=24, height=70, command=reset_scores_and_back).pack(pady=20, fill="x", padx=100)

    def abrir_p(self, col, pts):
        pregunta_data = MAPA_MAESTRO[self.tema].get((col, pts), ("Pregunta no encontrada", "Contactar soporte"))
        # Verificar si ya está contestada
        estado_previo = preguntas_completadas.get((self.tema, col, pts))
        
        if estado_previo:
            # MODO REVISIÓN: Ya contestada
            PopUpPregunta(self, pregunta_data[0], pregunta_data[1], self.tema, (col, pts), self.app_ref, modo_revision=True)
        else:
            # MODO JUEGO: Nueva
            PopUpPregunta(self, pregunta_data[0], pregunta_data[1], self.tema, (col, pts), self.app_ref, modo_revision=False)

# ================================================================
# VENTANA DE PREGUNTA (POPUP)
# ================================================================

class PopUpPregunta(ctk.CTkToplevel):
    def __init__(self, master, p, r, tema, key, app_ref, modo_revision=False):
        super().__init__(master)
        self.width, self.height = 850, 600
        self.configure(fg_color="#000")
        self.grab_set()
        self.tema, self.key, self.app_ref = tema, key, app_ref
        self.p, self.r = p, r
        self.modo_revision = modo_revision
        self.tiempo, self.modo_apuesta = TIEMPO_PREGUNTA_SEGUNDOS, False
        self.jugador_activo_idx = turno_actual
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=30, pady=20)
        self.update_idletasks()
        self.geometry(f"{self.width}x{self.height}+{(self.winfo_screenwidth()//2)-(self.width//2)}+{(self.winfo_screenheight()//2)-(self.height//2)}")
        
        if self.modo_revision:
            self.pantalla_revision()
        else:
            if random.random() < 0.10: self.pantalla_apuesta()
            else: self.pantalla_pregunta()

    # --- PANTALLA EXCLUSIVA PARA REPASO ---
    def pantalla_revision(self):
        ctk.CTkLabel(self.container, text="MODO REVISIÓN (SIN PUNTOS)", font=("Impact", 25), text_color="gray").pack(pady=5)
        TextoRGB(self.container, self.p, fsize=28, height=140).pack(fill="x", pady=15)
        TextoRGB(self.container, f"R: {self.r}", fsize=28, height=140).pack(fill="x", pady=15)
        ctk.CTkButton(self.container, text="CERRAR", fg_color="#333", font=("Impact", 25), height=50, command=self.destroy).pack(pady=20)

    # --- FLUJO NORMAL DE JUEGO ---
    def pantalla_apuesta(self, parpadeo=0):
        if parpadeo < 6:
            self.configure(fg_color="#FFD700" if parpadeo % 2 == 0 else "#000")
            self.after(100, lambda: self.pantalla_apuesta(parpadeo + 1))
        else:
            self.configure(fg_color="#000")
            ctk.CTkLabel(self.container, text="¿APUESTA?", font=("Impact", 45), text_color="#FFD700").pack(pady=10)
            ctk.CTkLabel(self.container, text="⚠️ AVISO: SI FALLAS PERDERÁS EL VALOR BASE DE LA PREGUNTA ⚠️", 
                         font=("Arial", 16, "bold"), text_color="#FF3D00").pack(pady=5)
            
            f = ctk.CTkFrame(self.container, fg_color="transparent"); f.pack(pady=20)
            ctk.CTkButton(f, text="SÍ (X2)", fg_color="#1B5E20", font=("Impact", 25), command=self.set_apuesta).pack(side="left", padx=15)
            ctk.CTkButton(f, text="NO", fg_color="#333", font=("Impact", 25), command=self.pantalla_pregunta).pack(side="left", padx=15)

    def set_apuesta(self): self.modo_apuesta = True; self.pantalla_pregunta()

    def pantalla_pregunta(self):
        for w in self.container.winfo_children(): w.destroy()
        ctk.CTkLabel(self.container, text=f"TURNO: {jugadores[self.jugador_activo_idx]['nombre']}", font=("Impact", 30), text_color="#00FF41").pack(pady=5)
        TextoRGB(self.container, self.p, fsize=28, height=140).pack(fill="x", pady=15)
        self.lbl_timer = ctk.CTkLabel(self.container, text=str(self.tiempo), font=("Impact", 80), text_color="#FF3D00"); self.lbl_timer.pack(pady=5)
        self.btn_ver = ctk.CTkButton(self.container, text="RESPUESTA", fg_color="#1a1a1a", font=("Impact", 25), height=60, command=self.ver_respuesta); self.btn_ver.pack(pady=15)
        self.timer_func()

    def timer_func(self):
        if self.tiempo > 0 and self.btn_ver.winfo_exists():
            self.tiempo -= 1; self.lbl_timer.configure(text=str(self.tiempo)); self.after(1000, self.timer_func)
        elif self.tiempo <= 0: self.ver_respuesta()

    def ver_respuesta(self):
        for w in self.container.winfo_children(): w.destroy()
        TextoRGB(self.container, f"R: {self.r}", fsize=28, height=140).pack(fill="x", pady=20)
        f = ctk.CTkFrame(self.container, fg_color="transparent"); f.pack(pady=15)
        ctk.CTkButton(f, text="CORRECTO", fg_color="#1B5E20", font=("Impact", 28), command=lambda: self.final(True)).pack(side="left", padx=15)
        ctk.CTkButton(f, text="INCORRECTO", fg_color="#B71C1C", font=("Impact", 28), command=lambda: self.final(False)).pack(side="left", padx=15)

    def final(self, gano):
        global turno_actual
        puntos_base = self.key[1]
        if gano:
            jugadores[self.jugador_activo_idx]['score'] += (puntos_base * (2 if self.modo_apuesta else 1))
        else:
            if self.modo_apuesta:
                jugadores[self.jugador_activo_idx]['score'] -= puntos_base
        
        preguntas_completadas[(self.tema, self.key[0], self.key[1])] = 'check' if gano else 'fail'
        turno_actual = (turno_actual + 1) % len(jugadores)

        preguntas_de_este_tema = [k for k in preguntas_completadas.keys() if k[0] == self.tema]
        board_complete = (len(preguntas_de_este_tema) == 20)

        if board_complete:
            self.destroy()
            self.app_ref.ir_a(self.tema)
            PopUpFinJuego(self.app_ref, self.app_ref, self.tema) 
        else:
            self.app_ref.ir_a(self.tema)
            self.destroy()

if __name__ == "__main__":
    app = JeopardyApp(); app.mainloop()