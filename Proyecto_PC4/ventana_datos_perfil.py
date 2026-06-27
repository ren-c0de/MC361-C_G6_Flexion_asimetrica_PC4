import os
import customtkinter as ctk
from tkinter import messagebox

# Librerías para incrustar gráficos en Tkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvasTkinterAgg

# Importamos la librería matemática de Junior
import calculos_geometria

# CONEXIÓN: Importamos la Ventana de la Sección 2
from ventana_seccion_2 import VentanaSeccion2

class VentanaDatosPerfil(ctk.CTkToplevel):
    def __init__(self, ventana_padre, perfil_tipo):
        super().__init__(ventana_padre)
        
        self.ventana_padre = ventana_padre
        self.perfil_tipo = perfil_tipo  # "Perfil L", "Rectángulo", etc.
        
        self.title(f"DATOS DEL PERFIL: {perfil_tipo.upper()}")
        self.geometry("950x650")
        
        # Ocultar la ventana de selección de perfiles mientras esta se usa
        self.ventana_padre.withdraw()
        self.protocol("WM_DELETE_WINDOW", lambda: self.quit())
        
        # Configuración del diseño: 2 columnas
        self.grid_columnconfigure(0, weight=1) # Controles
        self.grid_columnconfigure(1, weight=2) # Gráfico
        self.grid_rowconfigure(0, weight=1)
        
        # --- FRAME IZQUIERDO: CONTROLES ---
        self.frame_izquierdo = ctk.CTkFrame(self, corner_radius=10)
        self.frame_izquierdo.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        self.label_titulo = ctk.CTkLabel(
            self.frame_izquierdo, 
            text=f"Dimensiones del {perfil_tipo}", 
            font=("Arial", 16, "bold")
        )
        self.label_titulo.pack(pady=15, side="top")
        
        # --- SOLUCIÓN VISUAL: Colocamos los botones fijos abajo PRIMERO ---
        self.btn_atras = ctk.CTkButton(self.frame_izquierdo, text="ATRÁS", fg_color="#7D7D7D", hover_color="#5A5A5A", command=self.regresar)
        self.btn_atras.pack(side="bottom", pady=15, padx=20, fill="x")
        
        self.btn_calcular = ctk.CTkButton(self.frame_izquierdo, text="CALCULAR PROPIEDADES", fg_color="#2ecc71", hover_color="#27ae60", command=self.ejecutar_calculos)
        self.btn_calcular.pack(side="bottom", pady=5, padx=20, fill="x")
        
        # --- ETIQUETA DE ADVERTENCIA DINÁMICA ---
        self.label_error = ctk.CTkLabel(
            self.frame_izquierdo,
            text="",
            font=("Arial", 11, "bold"),
            text_color="#E74C3C",
            wraplength=220,
            justify="center"
        )
        self.label_error.pack(side="bottom", pady=10, padx=20)

        self.entradas = {}
        
        # --- MAPEO DE ENTRADAS SEGÚN EL PERFIL (Normalizado) ---
        tipo_normalizado = (self.perfil_tipo.lower()
                    .replace("á", "a")
                    .replace("é", "e")
                    .replace("í", "i")
                    .replace("ó", "o")
                    .replace("ú", "u")
                    .strip())

        if "perfil l" in tipo_normalizado:
            self.crear_campo_entrada("Ancho del ala base (b_ala):", "b_ala")
            self.crear_campo_entrada("Espesor del ala base (a_ala):", "a_ala")
            self.crear_campo_entrada("Espesor del patín vertical (b_patin):", "b_patin")
            self.crear_campo_entrada("Altura del patín vertical (a_patin):", "a_patin")

        elif "perfil z" in tipo_normalizado:
            self.crear_campo_entrada("Ancho ala superior (b_sup):", "b_sup")
            self.crear_campo_entrada("Espesor ala superior (a_sup):", "a_sup")
            self.crear_campo_entrada("Espesor del alma (b_alma):", "b_alma")
            self.crear_campo_entrada("Altura del alma (a_alma):", "a_alma")
            self.crear_campo_entrada("Ancho ala inferior (b_inf):", "b_inf")
            self.crear_campo_entrada("Espesor ala inferior (a_inf):", "a_inf")

        elif "perfil t" in tipo_normalizado:
            self.crear_campo_entrada("Ancho del ala superior (b_ala):", "b_ala")
            self.crear_campo_entrada("Espesor del ala superior (a_ala):", "a_ala")
            self.crear_campo_entrada("Espesor del alma (b_alma):", "b_alma")
            self.crear_campo_entrada("Altura del alma (a_alma):", "a_alma")

        elif "perfil u" in tipo_normalizado:
            self.crear_campo_entrada("Ancho de la base (b_alma):", "b_alma")
            self.crear_campo_entrada("Espesor de la base (a_alma):", "a_alma")
            self.crear_campo_entrada("Espesor de los patines (b_patin):", "b_patin")
            self.crear_campo_entrada("Altura de los patines (a_patin):", "a_patin")

        elif "perfil h" in tipo_normalizado:
            self.crear_campo_entrada("Ancho ala superior (b_sup):", "b_sup")
            self.crear_campo_entrada("Espesor ala superior (a_sup):", "a_sup")
            self.crear_campo_entrada("Espesor del alma (b_alma):", "b_alma")
            self.crear_campo_entrada("Altura del alma (a_alma):", "a_alma")
            self.crear_campo_entrada("Ancho ala inferior (b_inf):", "b_inf")
            self.crear_campo_collapse = "a_inf"
            self.crear_campo_entrada("Espesor ala inferior (a_inf):", "a_inf")

        elif "circulo" in tipo_normalizado:
            self.crear_campo_entrada("Radio del círculo (r):", "r")

        elif "elipse" in tipo_normalizado:
            self.crear_campo_entrada("Semieje horizontal (sz):", "sz")
            self.crear_campo_entrada("Semieje vertical (sy):", "sy")

        elif "rectangulo" in tipo_normalizado:
            self.crear_campo_entrada("Ancho de la base (b):", "b")
            self.crear_campo_entrada("Altura de la sección (h):", "h")
            
        # --- FRAME DERECHO: MATPLOTLIB CON Z+ IZQUIERDA ---
        self.frame_derecho = ctk.CTkFrame(self, corner_radius=10)
        self.frame_derecho.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        self.fig, self.ax = plt.subplots(figsize=(5, 5), dpi=100)
        self.fig.patch.set_facecolor('#242424') 
        self.ax.set_facecolor('#1e1e1e')
        self.ax.tick_params(colors='white')
        
        self.canvas = FigureCanvasTkinterAgg(self.fig, master=self.frame_derecho)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        self.actualizar_grafico()

    def crear_campo_entrada(self, texto_label, clave_variable):
        lbl = ctk.CTkLabel(self.frame_izquierdo, text=texto_label, font=("Arial", 12))
        lbl.pack(pady=(5, 1), padx=20, anchor="w", side="top")
        
        txt = ctk.CTkEntry(self.frame_izquierdo)
        txt.pack(pady=(0, 5), padx=20, fill="x", side="top")
        
        self.entradas[clave_variable] = txt
        txt.bind("<KeyRelease>", lambda event: self.actualizar_grafico())

    def obtener_valores(self):
        try:
            valores = {}
            for k, widget in self.entradas.items():
                val_texto = widget.get().strip()
                if not val_texto:
                    return None 
                valores[k] = float(val_texto)
                
            return valores
        except ValueError:
            return "ERROR_NUMERICO"

    def actualizar_grafico(self):
        self.ax.clear()
        self.ax.grid(True, color='#444444', linestyle='--')
        self.ax.set_title("Previsualización Geométrica (Z+ Izquierda)", color="white", fontsize=12)
        
        self.ax.invert_xaxis()
        self.ax.axhline(0, color='white', linewidth=1.2)
        self.ax.axvline(0, color='white', linewidth=1.2)
        self.ax.set_xlabel("Eje Z", color="white")
        self.ax.set_ylabel("Eje Y", color="white")
        
        datos = self.obtener_valores()
        self.label_error.configure(text="")
        
        tipo_normalizado = (self.perfil_tipo.lower()
                    .replace("á", "a")
                    .replace("é", "e")
                    .replace("í", "i")
                    .replace("ó", "o")
                    .replace("ú", "u")
                    .strip())

        if datos == "ERROR_NUMERICO":
            self.label_error.configure(text="⚠️ Alerta: Introduce solo valores numéricos válidos.")
            self.dibujar_plano_vacio()
            return

        if datos:
            if "perfil l" in tipo_normalizado:
                b_ala, a_ala = datos["b_ala"], datos["a_ala"]
                b_patin, a_patin = datos["b_patin"], datos["a_patin"]
                if b_ala <= 0 or a_ala <= 0 or b_patin <= 0 or a_patin <= 0:
                    self.label_error.configure(text="⚠️ Error: Las cotas deben ser mayores a cero.")
                    self.dibujar_plano_vacio()
                    return
                if b_patin >= b_ala or a_ala >= a_patin:
                    self.label_error.configure(text="⚠️ Error: Proporciones de espesor inválidas.")
                    self.dibujar_plano_vacio()
                    return
                args_junior = ('L', 0.0, 0.0, b_ala, a_ala, b_patin, a_patin)

            elif "perfil z" in tipo_normalizado:
                b_sup, a_sup = datos["b_sup"], datos["a_sup"]
                b_alma, a_alma = datos["b_alma"], datos["a_alma"]
                b_inf, a_inf = datos["b_inf"], datos["a_inf"]
                if b_sup <= 0 or a_sup <= 0 or b_alma <= 0 or a_alma <= 0 or b_inf <= 0 or a_inf <= 0:
                    self.label_error.configure(text="⚠️ Error: Las cotas deben ser mayores a cero.")
                    self.dibujar_plano_vacio()
                    return
                if b_alma >= b_sup or b_alma >= b_inf:
                    self.label_error.configure(text="⚠️ Error: El alma no puede superar las alas.")
                    self.dibujar_plano_vacio()
                    return
                args_junior = ('Z', 0.0, 0.0, b_sup, a_sup, b_alma, a_alma, b_inf, a_inf)

            elif "perfil t" in tipo_normalizado:
                b_ala, a_ala = datos["b_ala"], datos["a_ala"]
                b_alma, a_alma = datos["b_alma"], datos["a_alma"]
                if b_ala <= 0 or a_ala <= 0 or b_alma <= 0 or a_alma <= 0:
                    self.label_error.configure(text="⚠️ Error: Las cotas deben ser mayores a cero.")
                    self.dibujar_plano_vacio()
                    return
                if b_alma >= b_ala:
                    self.label_error.configure(text="⚠️ Error: El alma no puede superar el ala.")
                    self.dibujar_plano_vacio()
                    return
                args_junior = ('T', 0.0, 0.0, b_ala, a_ala, b_alma, a_alma)

            elif "perfil u" in tipo_normalizado:
                b_alma, a_alma = datos["b_alma"], datos["a_alma"]
                b_patin, a_patin = datos["b_patin"], datos["a_patin"]
                if b_alma <= 0 or a_alma <= 0 or b_patin <= 0 or a_patin <= 0:
                    self.label_error.configure(text="⚠️ Error: Las cotas deben ser mayores a cero.")
                    self.dibujar_plano_vacio()
                    return
                if (2 * b_patin) >= b_alma or a_alma >= a_patin:
                    self.label_error.configure(text="⚠️ Error: Espesores exceden las dimensiones base.")
                    self.dibujar_plano_vacio()
                    return
                args_junior = ('U', 0.0, 0.0, b_alma, a_alma, b_patin, a_patin)

            elif "perfil h" in tipo_normalizado:
                b_sup, a_sup = datos["b_sup"], datos["a_sup"]
                b_alma, a_alma = datos["b_alma"], datos["a_alma"]
                b_inf, a_inf = datos["b_inf"], datos["a_inf"]
                if b_sup <= 0 or a_sup <= 0 or b_alma <= 0 or a_alma <= 0 or b_inf <= 0 or a_inf <= 0:
                    self.label_error.configure(text="⚠️ Error: Las cotas deben ser mayores a cero.")
                    self.dibujar_plano_vacio()
                    return
                if b_alma >= b_sup or b_alma >= b_inf:
                    self.label_error.configure(text="⚠️ Error: El alma no puede superar las alas.")
                    self.dibujar_plano_vacio()
                    return
                args_junior = ('H', 0.0, 0.0, b_sup, a_sup, b_alma, a_alma, b_inf, a_inf)

            elif "circulo" in tipo_normalizado:
                r = datos["r"]
                if r <= 0:
                    self.label_error.configure(text="⚠️ Error: El radio debe ser mayor a cero.")
                    self.dibujar_plano_vacio()
                    return
                args_junior = ('circulo', 0.0, 0.0, r)

            elif "elipse" in tipo_normalizado:
                sz, sy = datos["sz"], datos["sy"]
                if sz <= 0 or sy <= 0:
                    self.label_error.configure(text="⚠️ Error: Los semiejes deben ser mayores a cero.")
                    self.dibujar_plano_vacio()
                    return
                args_junior = ('elipse', 0.0, 0.0, sz, sy)

            elif "rectangulo" in tipo_normalizado:
                b, h = datos["b"], datos["h"]
                if b <= 0 or h <= 0:
                    self.label_error.configure(text="⚠️ Error: El ancho y la altura deben ser mayores a cero.")
                    self.dibujar_plano_vacio()
                    return
                args_junior = ('rectangulo', 0.0, 0.0, b, h)

            try:
                resultados = calculos_geometria.calcular_propiedades_geometricas(*args_junior)
                vertices = resultados['vertices_globales']
                
                poligono = plt.Polygon(vertices, edgecolor='cyan', facecolor='cyan', alpha=0.4, lw=2)
                self.ax.add_patch(poligono)
                
                self.ax.relim()
                self.ax.autoscale_view()
                self.canvas.draw()
            except Exception as e:
                self.label_error.configure(text="⚠️ Error: Geometría inconsistente en cálculos.")
                self.dibujar_plano_vacio()
        else:
            self.dibujar_plano_vacio()

    def dibujar_plano_vacio(self):
        self.ax.set_xlim(10, -1) 
        self.ax.set_ylim(-1, 10)
        self.canvas.draw()

    def ejecutar_calculos(self):
        datos = self.obtener_valores()
        if datos == "ERROR_NUMERICO" or self.label_error.cget("text") != "":
            messagebox.showerror("Error de datos", "Corrige los errores geométricos antes de calcular.")
            return
        if not datos:
            messagebox.showwarning("Campos vacíos", "Llena todas las cotas antes de proceder al cálculo.")
            return

        tipo_normalizado = (self.perfil_tipo.lower()
                    .replace("á", "a")
                    .replace("é", "e")
                    .replace("í", "i")
                    .replace("ó", "o")
                    .replace("ú", "u")
                    .strip())

        if "perfil l" in tipo_normalizado:
            args_junior = ('L', 0.0, 0.0, datos["b_ala"], datos["a_ala"], datos["b_patin"], datos["a_patin"])
        elif "perfil z" in tipo_normalizado:
            args_junior = ('Z', 0.0, 0.0, datos["b_sup"], datos["a_sup"], datos["b_alma"], datos["a_alma"], datos["b_inf"], datos["a_inf"])
        elif "perfil t" in tipo_normalizado:
            args_junior = ('T', 0.0, 0.0, datos["b_ala"], datos["a_ala"], datos["b_alma"], datos["a_alma"])
        elif "perfil u" in tipo_normalizado:
            args_junior = ('U', 0.0, 0.0, datos["b_alma"], datos["a_alma"], datos["b_patin"], datos["a_patin"])
        elif "perfil h" in tipo_normalizado:
            args_junior = ('H', 0.0, 0.0, datos["b_sup"], datos["a_sup"], datos["b_alma"], datos["a_alma"], datos["b_inf"], datos["a_inf"])
        elif "circulo" in tipo_normalizado:
            args_junior = ('circulo', 0.0, 0.0, datos["r"])
        elif "elipse" in tipo_normalizado:
            args_junior = ('elipse', 0.0, 0.0, datos["sz"], datos["sy"])
        elif "rectangulo" in tipo_normalizado:
            args_junior = ('rectangulo', 0.0, 0.0, datos["b"], datos["h"])

        try:
            resultados = calculos_geometria.calcular_propiedades_geometricas(*args_junior)
            
            self.ax.plot(resultados['Cz'], resultados['Cy'], marker='o', color='red', markersize=8, label="Centroide (G)")
            self.ax.legend()
            self.canvas.draw()
            
            msg = (
                f"Perfil Analizado: {resultados['nombre']}\n"
                f"Área Total: {resultados['area']:.4f}\n"
                f"Centroide G: ({resultados['Cz']:.4f}, {resultados['Cy']:.4f})\n\n"
                f"--- Inercias Baricéntricas ---\n"
                f"Izc (local): {resultados['Izc']:.4f}\n"
                f"Iyc (local): {resultados['Iyc']:.4f}\n"
                f"Izyc (Producto vital): {resultados['Izyc']:.4f}"
            )
            messagebox.showinfo("Resultados del Análisis Finito", msg)
            
            # --- NUEVA CONEXIÓN EXCLUSIVA A LA SECCIÓN 2 ---
            # 1. FORMATEO CORRECTO DE DATOS (Usando tus variables reales del motor matemático)
            datos_geo_formateados = {
                "Area": resultados['area'],          
                "Iz": resultados['Izc'],            
                "Iy": resultados['Iyc'],            
                "Iyz": resultados['Izyc'],          
                "vertices_locales": resultados['vertices_locales']  
            }
            
            # 2. SEPARAR EL FOCO ANTES DE OCULTAR O DESTRUIR
            # Quitamos el foco de los inputs enviándolo a la ventana padre original
            try:
                self.ventana_padre.focus_set()
                self.grab_release() # Liberamos el grab_set de forma limpia
            except Exception:
                pass
            
            # 3. INSTANCIAR LA SECCIÓN 2 (Pasándole los datos correctos)
            # Primero creamos la ventana y le inyectamos los datos formateados
            ventana_cargas = VentanaSeccion2(ventana_padre=self.ventana_padre, datos_geo=datos_geo_formateados)
            ventana_cargas.deiconify()
            
            # 4. OCULTAR Y DESTRUIR LA VENTANA ACTUAL (Al final del proceso)
            # Retiramos la interfaz de la pantalla primero para que no interfiera visualmente
            self.withdraw()
            
            # Usamos after para retrasar unos milisegundos la destrucción total del widget.
            # Esto le da tiempo a Tkinter de limpiar su cola de eventos internos sin lanzar el TclError.
            self.after(100, self.destroy)
            
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error en el motor matemático: {e}")

    def regresar(self):
        try:
            plt.close(self.fig)
        except Exception:
            pass
        self.ventana_padre.deiconify()
        self.destroy()