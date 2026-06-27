import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

class VentanaSeccion3(ctk.CTkToplevel):
    def __init__(self, ventana_padre, datos_calculo, lista_vertices):
        super().__init__()
        self.ventana_padre = ventana_padre
        self.datos = datos_calculo
        self.vertices = np.array(lista_vertices)

        self.title("SECCIÓN 3: PRESENTACIÓN DE RESULTADOS")
        self.geometry("850x800")  # Le damos un poco más de ancho para los gráficos

        # Protocolo de cierre
        self.protocol("WM_DELETE_WINDOW", self.cerrar_todo)

        # Contenedor con barra de desplazamiento vertical (Scrollable Frame)
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="#1A1A1A")
        self.scroll_container.pack(fill="both", expand=True, padx=10, pady=10)

        # TÍTULO PRINCIPAL
        lbl_titulo = ctk.CTkLabel(
            self.scroll_container, 
            text="SECCIÓN 3: PRESENTACIÓN DE RESULTADOS", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#FFFFFF"
        )
        lbl_titulo.pack(pady=15)

        # ==========================================
        # BLOQUE 1: CÍRCULO DE MOHR
        # ==========================================
        ctk.CTkLabel(
            self.scroll_container, text="CÍRCULO DE MOHR", 
            font=ctk.CTkFont(size=16, weight="bold", underline=True), text_color="#A0A0A0"
        ).pack(pady=10)

        self.crear_grafico_mohr()

        txt_mohr = (
            f"Imax (Iu): {self.datos['Imax']:.2f}\n"
            f"Imin (Iv): {self.datos['Imin']:.2f}\n"
            f"Ángulo tetha (θ): {self.datos['tetha']:.2f}°"
        )
        ctk.CTkLabel(
            self.scroll_container, text=txt_mohr, 
            font=ctk.CTkFont(family="Courier", size=13), justify="left", text_color="#FFF"
        ).pack(pady=10)

        # Separador visual
        ctk.CTkLabel(self.scroll_container, text="-"*60, text_color="#404040").pack()

        # ==========================================
        # BLOQUE 2: ESFUERZOS EN LA SECCIÓN
        # ==========================================
        ctk.CTkLabel(
            self.scroll_container, text="COMPORTAMIENTO DE LA SECCIÓN (ESFUERZOS)", 
            font=ctk.CTkFont(size=16, weight="bold", underline=True), text_color="#A0A0A0"
        ).pack(pady=10)

        self.crear_grafico_esfuerzos()

        # Generar lista detallada de esfuerzos por cada vértice
        texto_vertices = "\nEsfuerzos en cada vértice:\n"
        for i, v in enumerate(self.vertices):
            z_val = v[0]
            y_val = v[1]
            esf = self.datos["esfuerzos"][i]
            
            # Clasificación de tipo de esfuerzo
            if esf > 1e-4:
                tipo = "Tracción"
            elif esf < -1e-4:
                tipo = "Compresión"
            else:
                tipo = "Neutro"
                
            texto_vertices += f"  Vértice {i+1} ({z_val:.2f}; {y_val:.2f}) → {esf:.2f} ({tipo})\n"

        # Corrección: Asegurar que si el esfuerzo mínimo es compresión se exprese con su signo formal (-)
        val_sigma_min = self.datos['sigma_min']
        if val_sigma_min > 0:  # Si venía guardado por error en valor absoluto lo forzamos a negativo
            val_sigma_min = -val_sigma_min

        txt_esfuerzos = (
            f"Resultados extremos finales:\n"
            f"Inclinación del eje neutro: {self.datos['betha']:.2f}° (Ángulo betha)\n"
            f"Esfuerzo máximo (Tracción): {abs(self.datos['sigma_max']):.2f} → En vértice: [{self.datos['v_max'][0]:.2f}, {self.datos['v_max'][1]:.2f}]\n"
            f"Esfuerzo mínimo (Compresión): {val_sigma_min:.2f} → En vértice: [{self.datos['v_min'][0]:.2f}, {self.datos['v_min'][1]:.2f}]\n"
            f"{texto_vertices}"
        )
        
        ctk.CTkLabel(
            self.scroll_container, text=txt_esfuerzos, 
            font=ctk.CTkFont(family="Courier", size=13), justify="left", text_color="#FFF"
        ).pack(pady=10)

        # ==========================================
        # BOTONES FINALES
        # ==========================================
        frame_botones = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        frame_botones.pack(pady=25)

        btn_reiniciar = ctk.CTkButton(
            frame_botones, text="REINICIAR AL MENÚ", fg_color="#4A4A4A", hover_color="#5A5A5A",
            command=self.accion_reiniciar
        )
        btn_reiniciar.grid(row=0, column=0, padx=20)

        btn_cerrar = ctk.CTkButton(
            frame_botones, text="CERRAR", fg_color="#D9534F", hover_color="#C9302C",
            command=self.cerrar_todo
        )
        btn_cerrar.grid(row=0, column=1, padx=20)

    def crear_grafico_mohr(self):
        # Ajustamos el tamaño de la figura para que no colapse verticalmente
        fig, ax = plt.subplots(figsize=(5.5, 5.5), facecolor="#1A1A1A")
        ax.set_facecolor("#1A1A1A")

        Iprom = self.datos["Iprom"]
        R = self.datos["R_mohr"]
        Iz = self.datos["Iz"]
        Iy = self.datos["Iy"]
        Iyz = self.datos["Iyz"]

        # Si el radio es prácticamente cero, evitamos errores visuales de escala
        if R < 1e-5:
            R = 1.0

        # Dibujar circunferencia completa
        theta_line = np.linspace(0, 2*np.pi, 200)
        ax.plot(Iprom + R*np.cos(theta_line), R*np.sin(theta_line), color="#E74C3C", lw=2)
        
        # Diámetro e inclinación
        ax.plot([Iz, Iy], [Iyz, -Iyz], color="#2980B9", linestyle="--", marker="o", markersize=6)
        ax.plot(Iprom, 0, marker="o", color="#FFFFFF")

        # Configuración estética de los ejes
        ax.axhline(0, color="#555555", lw=1)
        ax.axvline(0, color="#555555", lw=1)
        ax.set_xlabel("Iz, Iy", color="#FFFFFF", fontsize=10)
        ax.set_ylabel("Izy", color="#FFFFFF", fontsize=10)
        
        # Invertir eje Y (positivo hacia abajo para Mohr)
        ax.set_ylim(Iyz + R * 1.2, -Iyz - R * 1.2) if abs(Iyz) > R else ax.set_ylim(R * 1.2, -R * 1.2)
        ax.set_xlim(Iprom - R * 1.2, Iprom + R * 1.2)

        ax.tick_params(colors="#888888", labelsize=9)
        ax.grid(True, color="#333333", linestyle=":")
        ax.set_aspect('equal', 'box')

        # Incrustar en Tkinter asegurando expansión apropiada
        canvas = FigureCanvasTkAgg(fig, master=self.scroll_container)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=5, fill="none", expand=False)

    def crear_grafico_esfuerzos(self):
        fig, ax = plt.subplots(figsize=(5.5, 5.5), facecolor="#1A1A1A")
        ax.set_facecolor("#1A1A1A")

        # Evitar errores si no hay vértices válidos en la lista
        if len(self.vertices) == 0:
            self.vertices = np.array([[1,1], [-1,1], [-1,-1], [1,-1]])

        x_poly = np.append(self.vertices[:, 0], self.vertices[0, 0])
        y_poly = np.append(self.vertices[:, 1], self.vertices[0, 1])
        
        # =========================================================================
        # AGREGADO: RELLENO CONTINUO DE ESFUERZOS (tripcolor)
        # =========================================================================
        try:
            # Extraemos las coordenadas y los esfuerzos de los vértices base
            x_pts = self.vertices[:, 0]
            y_pts = self.vertices[:, 1]
            esfuerzos_pts = np.array(self.datos["esfuerzos"])
            
            # Pintamos el gradiente interior continuo. 'shading="gouraud"' suaviza los colores
            # Usamos el mapa "jet" para que combine perfectamente con tus puntos
            ax.tripcolor(x_pts, y_pts, esfuerzos_pts, cmap="jet", shading="gouraud", alpha=0.75, zorder=2)
        except Exception as e_gradiente:
            print("No se pudo generar el degradado interno (requiere vértices no colineales):", e_gradiente)
        # =========================================================================

        ax.plot(x_poly, y_poly, color="#FFFFFF", lw=2, zorder=3)

        # FIX DEL ERROR: Matplotlib moderno obtiene mapas de color directamente por string o colormaps
        sc = ax.scatter(self.vertices[:, 0], self.vertices[:, 1], c=self.datos["esfuerzos"], cmap="jet", s=50, zorder=4)
        
        # Traza aproximada del Eje Neutro
        b_rad = self.datos["betha_rad"]
        x_en = np.linspace(min(x_poly)*1.2, max(x_poly)*1.2, 10)
        y_en = x_en * np.tan(b_rad)
        ax.plot(x_en, y_en, color="#FF007F", linestyle="-.", lw=1.5)

        ax.axhline(0, color="#2ECC71", lw=1)
        ax.axvline(0, color="#2ECC71", lw=1)
        ax.set_xlabel("Eje Zg (Base)", color="#FFFFFF", fontsize=10)
        ax.set_ylabel("Eje Yg (Altura)", color="#FFFFFF", fontsize=10)
        
        # CORRECCIÓN: Invertir el eje Z para que sea positivo hacia la izquierda (Idéntico a Opción C)
        ax.invert_xaxis()
        
        ax.tick_params(colors="#888888", labelsize=9)
        ax.grid(True, color="#333333", linestyle=":")
        ax.set_aspect('equal', 'box')

        # =========================================================================
        # AGREGADO: AUTO-SCALE INTELIGENTE (Para que no se vea chiquito)
        # =========================================================================
        # Medimos el ancho y alto real del contorno de la pieza
        dx = max(x_poly) - min(x_poly)
        dy = max(y_poly) - min(y_poly)
        
        # Si la pieza es un punto o da cero por error, evitamos dividir entre cero
        margin = max(dx, dy) * 0.15 if max(dx, dy) > 0 else 1.0
        
        # Forzamos los límites del gráfico ajustados al tamaño del polígono + margen
        ax.set_xlim(max(x_poly) + margin, min(x_poly) - margin)
        ax.set_ylim(min(y_poly) - margin, max(y_poly) + margin)
        # =========================================================================

        cbar = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
        cbar.ax.tick_params(labelsize=8, colors="#888888")

        canvas = FigureCanvasTkAgg(fig, master=self.scroll_container)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=5, fill="none", expand=False)

    def accion_reiniciar(self):
        plt.close('all')
        self.destroy()
        raiz = self.ventana_padre
        while hasattr(raiz, 'ventana_padre') and raiz.ventana_padre is not None:
            raiz = raiz.ventana_padre
        raiz.deiconify()

    def cerrar_todo(self):
        plt.close('all')
        self.quit()