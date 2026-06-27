import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# Importamos el módulo de cálculos (donde integraremos lo de Lenin)
import calculos_geometria 

class VentanaOpcionC(ctk.CTkToplevel):
    def __init__(self, ventana_padre):
        super().__init__()
        self.ventana_padre = ventana_padre
        self.ventana_padre.withdraw()  # Ocultamos la principal

        self.title("OPCIÓN C: POLÍGONO LIBRE")
        self.geometry("1000x700")
        
        # Lista dinámica para almacenar los vértices ingresados: [[z1, y1], [z2, y2], ...]
        self.lista_vertices = []
        self.figura_cerrada = False
        self.resultados_geometria = None

        # Protocolo de cierre de ventana física (X)
        self.protocol("WM_DELETE_WINDOW", self.regresar)

        # --- DISEÑO DE LA INTERFAZ (Dos columnas) ---
        # Columna Izquierda: Controles
        self.frame_izquierdo = ctk.CTkFrame(self, width=300)
        self.frame_izquierdo.pack(side="left", fill="y", padx=20, pady=20)

        self.label_titulo = ctk.CTkLabel(
            self.frame_izquierdo, 
            text="Ingrese vértices (z, y)\npara formar su sección:", 
            font=("Arial", 14, "bold")
        )
        self.label_titulo.pack(pady=20, padx=20)

        # Campos de entrada con variables dinámicas para rastreo en tiempo real
        self.label_contador = ctk.CTkLabel(self.frame_izquierdo, text="Vértice 1:", font=("Arial", 12, "italic"))
        self.label_contador.pack(anchor="w", padx=20)

        self.lbl_zc = ctk.CTkLabel(self.frame_izquierdo, text="Coordenada Zc:")
        self.lbl_zc.pack(anchor="w", padx=20)
        
        self.str_zc = ctk.StringVar()
        self.str_zc.trace_add("write", lambda *args: self.previsualizar_vertice_borrador())
        self.txt_zc = ctk.CTkEntry(self.frame_izquierdo, textvariable=self.str_zc)
        self.txt_zc.pack(fill="x", padx=20, pady=(0, 10))

        self.lbl_yc = ctk.CTkLabel(self.frame_izquierdo, text="Coordenada Yc:")
        self.lbl_yc.pack(anchor="w", padx=20)
        
        self.str_yc = ctk.StringVar()
        self.str_yc.trace_add("write", lambda *args: self.previsualizar_vertice_borrador())
        self.txt_yc = ctk.CTkEntry(self.frame_izquierdo, textvariable=self.str_yc)
        self.txt_yc.pack(fill="x", padx=20, pady=(0, 20))

        # Botones de acción izquierda
        self.btn_anadir = ctk.CTkButton(self.frame_izquierdo, text="AÑADIR", fg_color="#3B8ED0", command=self.anadir_vertice)
        self.btn_anadir.pack(fill="x", padx=20, pady=5)

        self.btn_cerrar = ctk.CTkButton(self.frame_izquierdo, text="CERRAR FIGURA", fg_color="#E67E22", command=self.cerrar_poligono)
        self.btn_cerrar.pack(fill="x", padx=20, pady=5)

        self.btn_continuar = ctk.CTkButton(self.frame_izquierdo, text="CONTINUAR", fg_color="#2ECC71", state="disabled", command=self.procesar_continuar)
        self.btn_continuar.pack(side="bottom", fill="x", padx=20, pady=(10, 20))

        self.btn_atras = ctk.CTkButton(self.frame_izquierdo, text="ATRÁS", fg_color="gray", command=self.regresar)
        self.btn_atras.pack(side="bottom", fill="x", padx=20, pady=5)

        # Columna Derecha: Gráfico Matplotlib
        self.frame_derecho = ctk.CTkFrame(self)
        self.frame_derecho.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.fig, self.ax = plt.subplots(figsize=(6, 6), facecolor='#1E1E1E')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_derecho)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        self.inicializar_grafico()

    def inicializar_grafico(self):
        self.ax.clear()
        self.ax.set_facecolor('#1E1E1E')
        self.ax.grid(True, color='#444444', linestyle='--')
        self.ax.set_title("Previsualización Geométrica (Z+ Izquierda)", color="white", fontsize=12)
        self.ax.invert_xaxis()
        self.ax.axhline(0, color='white', linewidth=1.2)
        self.ax.axvline(0, color='white', linewidth=1.2)
        self.ax.set_xlabel("Eje Z", color="white")
        self.ax.set_ylabel("Eje Y", color="white")
        self.ax.tick_params(colors='white')
        self.canvas.draw()

    def anadir_vertice(self):
        if self.figura_cerrada:
            messagebox.showwarning("Atención", "La figura ya está cerrada.")
            return

        try:
            z = float(self.txt_zc.get().strip())
            y = float(self.txt_yc.get().strip())
            nuevo_punto = [z, y]

            if self.lista_vertices and self.lista_vertices[-1] == nuevo_punto:
                messagebox.showerror("Error", "No puede ingresar dos vértices idénticos consecutivos.")
                return

            self.lista_vertices.append(nuevo_punto)
            
            # Desactivamos el trace temporalmente para limpiar sin gatillar eventos fantasmas
            self.txt_zc.delete(0, 'end')
            self.txt_yc.pack_configure() # Fuerza refresco limpio
            self.txt_yc.delete(0, 'end')
            
            self.label_contador.configure(text=f"Vértice {len(self.lista_vertices) + 1}:")
            
            # Forzamos actualización visual consolidada en azul
            self.actualizar_grafico()
            
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos.")

    def actualizar_grafico(self, limpiar_y_dibujar_base=False):
        """Versión optimizada que discrimina entre dibujo base y decoraciones temporales."""
        # Si solo queremos refrescar la base o redibujar completo, limpiamos el eje
        self.ax.clear()
        self.ax.grid(True, color='#444444', linestyle='--')
        self.ax.set_title("Previsualización Geométrica (Z+ Izquierda)", color="white", fontsize=12)
        self.ax.invert_xaxis()
        self.ax.axhline(0, color='white', linewidth=1.2)
        self.ax.axvline(0, color='white', linewidth=1.2)
        self.ax.set_xlabel("Eje Z", color="white")
        self.ax.set_ylabel("Eje Y", color="white")
        self.ax.tick_params(colors='white')

        if self.lista_vertices:
            zs = [p[0] for p in self.lista_vertices]
            ys = [p[1] for p in self.lista_vertices]
            
            # Dibujar los vértices consolidados (Azul/Cyan original)
            self.ax.scatter(zs, ys, color='#3B8ED0', s=50, zorder=5)
            
            if len(self.lista_vertices) > 1:
                self.ax.plot(zs, ys, color='cyan', linestyle='-', linewidth=2)
            
            if self.figura_cerrada:
                self.ax.plot([zs[-1], zs[0]], [ys[-1], ys[0]], color='cyan', linestyle='-', linewidth=2)
                self.ax.fill(zs, ys, color='cyan', alpha=0.3)

        # Si no estamos en un sub-llamado de boceto, forzamos el redibujado estático del lienzo
        if not limpiar_y_dibujar_base:
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()

    def cerrar_poligono(self):
        if len(self.lista_vertices) < 3:
            messagebox.showerror("Error", "Se necesitan al menos 3 vértices para poder cerrar una superficie poligonal.")
            return
        
        # Deshabilitamos la inserción para proteger la consistencia geométrica
        self.figura_cerrada = True
        self.btn_anadir.configure(state="disabled")
        self.btn_cerrar.configure(state="disabled")
        
        # Ejecutamos el motor analítico de Lenin pasando la lista de puntos
        self.resultados_geometria = calculos_geometria.poligono_gauss(self.lista_vertices)
        
        if self.resultados_geometria is None:
            messagebox.showerror("Error", "Ocurrió un error inesperado al procesar la geometría.")
            return

        # Si el área da negativa es porque el usuario ingresó los puntos en sentido HORARIO.
        # El teorema de Green maneja signo por orientación; lo corregimos con valor absoluto de forma segura.
        if self.resultados_geometria["A"] < 0:
            self.resultados_geometria["A"] = abs(self.resultados_geometria["A"])
            # Invertimos el signo del producto de inercia que se altera por la orientación horaria
            self.resultados_geometria["Iyz"] = -self.resultados_geometria["Iyz"]

        # [Ajuste de Inercias] Aseguramos que los momentos de inercia axiales sean siempre positivos
        self.resultados_geometria["Iy"] = abs(self.resultados_geometria["Iy"])
        self.resultados_geometria["Iz"] = abs(self.resultados_geometria["Iz"])

        # Actualizamos el gráfico para pintar el polígono sólido en Cyan
        self.actualizar_grafico()
        
        self.ax.plot(self.resultados_geometria['Zc'], self.resultados_geometria['Yc'], 
                     marker='X', color='#E74C3C', markersize=10, 
                     label=f"Centroide G\n({self.resultados_geometria['Zc']:.2f}, {self.resultados_geometria['Yc']:.2f})")
        self.ax.legend(loc='upper right', labelcolor='white', facecolor='#1e1e1e')
        self.canvas.draw()

        # Mostramos los resultados en un cuadro informativo rápido para que verifiquen
        msg = (
            f"¡Polígono consolidado con éxito!\n\n"
            f"Área (A): {self.resultados_geometria['A']:.4f}\n"
            f"Centroide Zc: {self.resultados_geometria['Zc']:.4f}\n"
            f"Centroide Yc: {self.resultados_geometria['Yc']:.4f}\n\n"
            f"Inercias Centroidales:\n"
            f"Iy: {self.resultados_geometria['Iy']:.4f}\n"
            f"Iz: {self.resultados_geometria['Iz']:.4f}\n"
            f"Iyz: {self.resultados_geometria['Iyz']:.4f}"
        )

        

        messagebox.showinfo("Cálculo Exitoso", msg)
        
        # Habilitamos avanzar a la Sección 2
        self.btn_continuar.configure(state="normal")

    def regresar(self):
        """Limpia los procesos en segundo plano y regresa de forma segura."""
        try:
            # Eliminamos los traces de las variables de texto para evitar errores de fondo
            if hasattr(self, 'str_zc') and hasattr(self, 'str_yc'):
                # Al pasar un diccionario vacío a initialize, o desvinculando:
                # Una forma directa en Tkinter es eliminar los modos de escritura asignados
                for cb in self.str_zc.trace_info():
                    self.str_zc.trace_remove(*cb)
                for cb in self.str_yc.trace_info():
                    self.str_yc.trace_remove(*cb)
        except Exception:
            pass

        # Cerramos los gráficos abiertos en memoria de Matplotlib para no saturar
        plt.close(self.fig)

        # Destruimos la ventana e invocamos la principal de vuelta
        self.destroy()
        self.ventana_padre.deiconify()

    def procesar_continuar(self):
        """
        Envía los resultados unificados a la ventana del menú principal 
        para que los guarde y abra la Sección 2.
        """
        # Validamos por seguridad si existen los cálculos
        if not hasattr(self, 'resultados_geometria') or self.resultados_geometria is None:
            messagebox.showerror("Error", "Primero debes cerrar y consolidar el polígono.")
            return

        # Estructuramos la salida para que sea idéntica al formato que pide tu grupo
        datos_unificados = {
            'area': self.resultados_geometria["A"],
            'Cz': self.resultados_geometria["Zc"],
            'Cy': self.resultados_geometria["Yc"],
            'Izc': self.resultados_geometria["Iz"],
            'Iyc': self.resultados_geometria["Iy"],
            'Izyc': self.resultados_geometria["Iyz"],
            'vertices_locales': self.resultados_geometria["vertices_locales"]
        }
        
        # Agregamos esto: Cerramos el gráfico actual en memoria
        plt.close(self.fig)
        
        # Llamamos al gestor de la ventana padre (interfaz_principal)
        self.destroy()
        self.ventana_padre.recibir_resultados_geometria(datos_unificados)

    def previsualizar_vertice_borrador(self):
        """Dibuja dinámicamente el punto actual en naranja y proyecta el segmento en camino."""
        if self.figura_cerrada:
            return

        try:
            # Intentamos leer lo que escribe el usuario en tiempo real
            z_boceto = float(self.str_zc.get().strip())
            y_boceto = float(self.str_yc.get().strip())
            punto_borrador = [z_boceto, y_boceto]
            
            # Re-renderizamos la base limpia con los puntos fijos azules
            self.actualizar_grafico(limpiar_y_dibujar_base=True)
            
            # 1. Pintar el punto actual en borrador (Naranja)
            self.ax.scatter(z_boceto, y_boceto, color='#E67E22', s=55, zorder=6, label="Borrador")
            
            # 2. Si ya hay al menos un punto fijo, proyectamos la línea segmentada naranja
            if self.lista_vertices:
                ultimo_fijo = self.lista_vertices[-1]
                self.ax.plot(
                    [ultimo_fijo[0], z_boceto], 
                    [ultimo_fijo[1], y_boceto], 
                    color='#E67E22', linestyle='--', linewidth=1.8
                )
                
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()
            
        except ValueError:
            # Si los campos están vacíos o a medio escribir, solo redibujamos el estado base azul seguro
            self.actualizar_grafico(limpiar_y_dibujar_base=True)