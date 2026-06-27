import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from motor_calculo import motor_flexion_y_mohr
from ventana_seccion_3 import VentanaSeccion3

class VentanaSeccion2(ctk.CTkToplevel):
    def __init__(self, ventana_padre, datos_geometria=None, *args, **kwargs):
        super().__init__()
        self.ventana_padre = ventana_padre
        
        # Buscamos si vino como 'datos_geometria', como 'datos_geo' (en kwargs) o si no vino nada
        datos = datos_geometria if datos_geometria is not None else kwargs.get("datos_geo", None)
        
        # Si se encontraron datos, los guardamos; si no, inicializamos un diccionario vacío
        self.datos_geo = datos if datos is not None else {}
        
        self.title("SECCIÓN 2: MOMENTOS FLECTORES Y CARGAS")
        self.geometry("1100x750")
        
        # Lista de momentos: [[M, alpha], ...]
        self.lista_momentos = []
        
        # Protocolo de cierre
        self.protocol("WM_DELETE_WINDOW", self.regresar)

        # --- INTERFAZ ---
        # Columna Izquierda: Entradas
        self.frame_izq = ctk.CTkFrame(self, width=320)
        self.frame_izq.pack(side="left", fill="y", padx=20, pady=20)

        ctk.CTkLabel(self.frame_izq, text="CONFIGURACIÓN DE CARGAS", font=("Arial", 16, "bold")).pack(pady=20)

        # === SECCIÓN: FUERZA AXIAL (P) ===
        ctk.CTkLabel(self.frame_izq, text="Fuerza Axial P (en Xg):").pack(anchor="w", padx=20)
        self.str_axial = ctk.StringVar()
        self.str_axial.trace_add("write", lambda *args: self.previsualizar_momento())
        self.txt_axial = ctk.CTkEntry(self.frame_izq, textvariable=self.str_axial, placeholder_text="Ej: 500 (+ Tracción)")
        self.txt_axial.pack(fill="x", padx=20, pady=(0, 10))

        # --- AQUÍ ESTÁN TUS NUEVOS BOTONES PARA FUERZA AXIAL ---
        self.frame_botones_axial = ctk.CTkFrame(self.frame_izq, fg_color="transparent")
        self.frame_botones_axial.pack(fill="x", padx=20, pady=(0, 20))

        self.btn_fijar = ctk.CTkButton(self.frame_botones_axial, text="Fijar P", command=self.fijar_fuerza_axial)
        self.btn_fijar.pack(side="left", expand=True, padx=(0, 5))

        self.btn_modificar = ctk.CTkButton(self.frame_botones_axial, text="Modificar", state="disabled", fg_color="gray", command=self.modificar_fuerza_axial)
        self.btn_modificar.pack(side="right", expand=True, padx=(5, 0))
        # -------------------------------------------------------------

        # === SECCIÓN: MOMENTOS FLECTORES ===
        # Campos para Momentos
        ctk.CTkLabel(self.frame_izq, text="Momento (M):").pack(anchor="w", padx=20)
        self.str_m = ctk.StringVar()
        self.str_m.trace_add("write", lambda *args: self.previsualizar_momento())
        self.txt_m = ctk.CTkEntry(self.frame_izq, textvariable=self.str_m)
        self.txt_m.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(self.frame_izq, text="Ángulo alpha (desde Yg):").pack(anchor="w", padx=20)
        self.str_a = ctk.StringVar()
        self.str_a.trace_add("write", lambda *args: self.previsualizar_momento())
        self.txt_a = ctk.CTkEntry(self.frame_izq, textvariable=self.str_a)
        self.txt_a.pack(fill="x", padx=20, pady=(0, 10))

        self.btn_anadir = ctk.CTkButton(self.frame_izq, text="AÑADIR MOMENTO", command=self.anadir_momento)
        self.btn_anadir.pack(fill="x", padx=20, pady=20)

        # Botones Inferiores
        self.btn_calcular = ctk.CTkButton(self.frame_izq, text="CALCULAR", fg_color="#E74C3C", hover_color="#C0392B", command=self.ir_a_seccion_3)
        self.btn_calcular.pack(side="bottom", fill="x", padx=20, pady=(10, 30))

        self.btn_atras = ctk.CTkButton(self.frame_izq, text="ATRÁS", fg_color="gray", command=self.regresar)
        self.btn_atras.pack(side="bottom", fill="x", padx=20, pady=5)

        # Columna Derecha: Gráfico en Proyección 3D
        self.frame_der = ctk.CTkFrame(self)
        self.frame_der.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.fig = plt.figure(figsize=(6, 6), facecolor='#1E1E1E')
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_der)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.actualizar_grafico()

    # --- AQUÍ ESTÁN LOS MÉTODOS QUE FALTABAN PARA CONTROLAR LA FUERZA AXIAL ---
    def fijar_fuerza_axial(self):
        val = self.str_axial.get().strip()
        if val:
            try:
                # Validar que sea un número
                float(val)
                self.txt_axial.configure(state="disabled") # Bloquea casilla
                self.btn_fijar.configure(state="disabled", fg_color="gray")     # Bloquea botón Fijar
                self.btn_modificar.configure(state="normal", fg_color="#2CC985")   # Habilita botón Modificar
                self.actualizar_grafico()
            except ValueError:
                messagebox.showerror("Error", "Ingrese un valor numérico válido para la fuerza axial P.")
        else:
            messagebox.showwarning("Atención", "Ingrese un valor para la fuerza axial P antes de fijar.")

    def modificar_fuerza_axial(self):
        self.txt_axial.configure(state="normal")     # Desbloquea casilla
        self.btn_fijar.configure(state="normal", fg_color="#1F6AA5")       # Habilita botón Fijar
        self.btn_modificar.configure(state="disabled", fg_color="gray") # Bloquea botón Modificar
    # ----------------------------------------------------------------------------------

    def actualizar_grafico(self, momento_temporal=None):
        self.ax.clear()
        self.ax.set_facecolor('#1E1E1E')
        
        # =========================================================================
        # NUEVO: AUTO-SCALE DINÁMICO 3D (Mantiene la orientación original intacta)
        # =========================================================================
        # Valores por defecto en caso de que no haya vértices cargados aún
        lim_x_min, lim_x_max = -5, 5
        lim_z_min, lim_z_max = -5, 5
        lim_y_min, lim_y_max = -5, 5 # El eje axial Xg de la viga
        
        if 'vertices_locales' in self.datos_geo and len(self.datos_geo['vertices_locales']) > 0:
            vl_check = np.array(self.datos_geo['vertices_locales'])
            xs_geo = vl_check[:, 0] # Coordenadas Zc del perfil -> Eje Zg
            ys_geo = vl_check[:, 1] # Coordenadas Yc del perfil -> Eje Yg
            
            # Buscamos las dimensiones máximas del perfil
            dx = max(xs_geo) - min(xs_geo)
            dy = max(ys_geo) - min(ys_geo)
            max_dim = max(dx, dy)
            
            # Un colchón del 40% para que los vectores de carga queden cómodos y visibles
            margin = max_dim * 0.40 if max_dim > 0 else 5.0
            
            # Establecemos límites simétricos baricéntricos basados en el tamaño real
            lim_x_min, lim_x_max = min(xs_geo) - margin, max(xs_geo) + margin
            lim_z_min, lim_z_max = min(ys_geo) - margin, max(ys_geo) + margin
            
            # El eje axial (Matplotlib Y) toma la misma escala para no deformar visualmente la pieza
            lim_y_min, lim_y_max = -max_dim - margin, max_dim + margin
            
        # 1. Asignación dinámica de límites manteniendo TU MAPEO EXACTO
        self.ax.set_xlim(lim_x_min, lim_x_max)   # Matplotlib X = Eje Zg
        self.ax.set_ylim(lim_y_min, lim_y_max)   # Matplotlib Y = Eje Xg
        self.ax.set_zlim(lim_z_min, lim_z_max)   # Matplotlib Z = Eje Yg
        # =========================================================================
        
        # 2. Rotulación corregida en los laterales
        self.ax.set_xlabel("Eje Zg (Base)", color="white", labelpad=10)
        self.ax.set_ylabel("Eje Xg (Axial)", color="white", labelpad=10)
        self.ax.set_zlabel("Eje Yg (Altura)", color="white", labelpad=10)
        self.ax.tick_params(colors='white')
        
        # Dibujar líneas de referencia baricéntricas en verde
        self.ax.plot([-5, 5], [0, 0], [0, 0], color='green', linewidth=1.5)                 # Eje Zg
        self.ax.plot([0, 0], [-5, 5], [0, 0], color='green', linewidth=1.5, linestyle='--') # Eje Xg
        self.ax.plot([0, 0], [0, 0], [-5, 5], color='green', linewidth=1.5)                 # Eje Yg

        # 3. Dibujar la sección transversal sólida en el plano axial Xg = 0 (Matplotlib Y = 0)
        if 'vertices_locales' in self.datos_geo:
            vl = np.array(self.datos_geo['vertices_locales'])
            poligono = np.vstack([vl, vl[0]])
            
            zg_pol = poligono[:, 0] # Coordenada Zc del perfil -> Eje Zg
            yg_pol = poligono[:, 1] # Coordenada Yc del perfil -> Eje Yg
            xg_pol = np.zeros_like(zg_pol) # Contenida en Xg = 0 (Matplotlib Y = 0)
            
            # Pasamos los arreglos en el orden: Matplotlib X (Zg), Matplotlib Y (Xg), Matplotlib Z (Yg)
            self.ax.plot(zg_pol, xg_pol, yg_pol, color='cyan', linewidth=2.5)
            
            # Polígono sólido 3D
            pts_3d = [[(p[0], 0, p[1]) for p in poligono]]
            cara_solida = Poly3DCollection(pts_3d, facecolors='cyan', alpha=0.15)
            self.ax.add_collection3d(cara_solida)

        # 4. Renderizar vector de Fuerza Axial P (Actúa en Eje Xg -> Matplotlib Y)
        try:
            val_p = float(self.str_axial.get().strip()) if self.str_axial.get() else 0.0
            if val_p != 0:
                dir_y = 3.5 if val_p > 0 else -3.5 
                # El vector va a lo largo del eje Matplotlib Y (Xg)
                self.dibujar_vector_3d(0, 0, 0, 0, dir_y, 0, color='#9B59B6')
        except ValueError:
            pass

        # 5. Dibujar momentos consolidados acumulados (Vectores Rojos)
        for m_data in self.lista_momentos:
            self.calcular_y_dibujar_momento(m_data[0], m_data[1], color='red')

        # 6. Dibujar momento en borrador interactivo (Vector Naranja)
        if momento_temporal:
            self.calcular_y_dibujar_momento(momento_temporal[0], momento_temporal[1], color='#E67E22')

        # Vista isométrica calibrada
        self.ax.view_init(elev=20, azim=60)
        self.canvas.draw()

    def calcular_y_dibujar_momento(self, M, alpha_deg, color):
        """Descompone el momento plano vectorialmente en el plano de la sección."""
        # Colocamos un signo negativo a "alpha_deg" para corregir la inversión 
        # y forzar que el sentido antihorario sea positivo y horario sea hacia la derecha.
        rad = np.radians(90 - alpha_deg)
        longitud = 4.0 if M > 0 else -4.0
        
        dz = longitud * np.cos(rad) # Componente en Eje Zg (Matplotlib X)
        dy = longitud * np.sin(rad) # Componente en Eje Yg (Matplotlib Z)
        
        # Dibujamos enviando: x=dz (Zg), y=0 (Xg), z=dy (Yg)
        self.dibujar_vector_3d(0, 0, 0, dz, 0, dy, color=color)

    def dibujar_vector_3d(self, x1, y1, z1, x2, y2, z2, color):
        """Dibuja un vector tridimensional usando Quiver."""
        self.ax.quiver(x1, y1, z1, x2-x1, y2-y1, z2-z1, 
                       color=color, linewidth=2.5, arrow_length_ratio=0.2)

    def previsualizar_momento(self):
        try:
            m = float(self.str_m.get().strip()) if self.str_m.get() else 0.0
            a = float(self.str_a.get().strip()) if self.str_a.get() else 0.0
            self.actualizar_grafico(momento_temporal=[m, a])
        except ValueError:
            self.actualizar_grafico()

    def anadir_momento(self):
        try:
            m = float(self.txt_m.get().strip())
            a = float(self.txt_a.get().strip())
            self.lista_momentos.append([m, a])
            
            # Limpieza limpia de campos de momentos
            self.str_m.set("")
            self.str_a.set("")
            self.actualizar_grafico()
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores numéricos para el momento y ángulo.")

    def regresar(self):
        plt.close(self.fig)
        self.destroy()
        self.ventana_padre.deiconify()

    def ir_a_seccion_3(self):
        try:
            if self.txt_axial.cget("state") == "normal":
                messagebox.showwarning("Atención", "Por favor, fije la Fuerza Axial P antes de calcular.")
                return

            axial_p = float(self.str_axial.get().strip()) if self.str_axial.get() else 0.0
            
            # 1. Unificamos los momentos ingresados (Paso 2 de tu Colab)
            My_total = 0.0
            Mz_total = 0.0
            for mag, ang_deg in self.lista_momentos:
                ang_rad = np.radians(ang_deg)
                Mz_total += mag * np.sin(ang_rad)
                My_total += mag * np.cos(ang_rad)

            # 2. Extraemos los datos geométricos del perfil
            # Nota: Asegúrate de que las llaves correspondan a los nombres que te pasan tus compañeros
            A = self.datos_geo.get("area", self.datos_geo.get("Area", 1.0))
            Iy = self.datos_geo.get("Iyc", self.datos_geo.get("Iy", 1.0))
            Iz = self.datos_geo.get("Izc", self.datos_geo.get("Iz", 1.0))
            Iyz = self.datos_geo.get("Izyc", self.datos_geo.get("Iyz", 0.0))
            vertices = self.datos_geo.get("vertices_locales", [])

            # 3. Corremos tu motor matemático
            resultados_finales = motor_flexion_y_mohr(axial_p, A, Iy, Iz, Iyz, My_total, Mz_total, vertices)

            # 4. Escondemos la Sección 2 y abrimos la Ventana de la Sección 3 pasándole los resultados
            self.withdraw()
            ventana_3 = VentanaSeccion3(self, resultados_finales, vertices)
            ventana_3.grab_set() # Mantiene el foco en la ventana de resultados

        except ValueError:
            messagebox.showerror("Error", "Ocurrió un error al procesar los datos numéricos.")