import os
import customtkinter as ctk
from tkinter import messagebox

# Librerías para incrustar gráficos en Tkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvasTkinterAgg

# Importamos el motor matemático (Junior + Juan)
import calculos_geometria

class VentanaOpcionB(ctk.CTkToplevel):
    def __init__(self, ventana_padre, perfil_tipo="Compuestos por Bloques"):
        super().__init__(ventana_padre)
        
        self.ventana_padre = ventana_padre
        self.title("OPCIÓN B: COMPUESTOS POR BLOQUES")
        self.geometry("950x650")
        
        # Ocultar la ventana de selección mientras se usa esta
        self.ventana_padre.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.regresar)
        
        # --- LISTA DINÁMICA DE BLOQUES ---
        # Guardará los bloques en formato: [b, h, Zc, Yc]
        self.lista_bloques = []
        
        # Configuración del diseño: 2 columnas
        self.grid_columnconfigure(0, weight=1) # Controles
        self.grid_columnconfigure(1, weight=2) # Gráfico de Matplotlib
        self.grid_rowconfigure(0, weight=1)
        
        # --- FRAME IZQUIERDO: CONTROLES ---
        self.frame_izquierdo = ctk.CTkFrame(self, corner_radius=10)
        self.frame_izquierdo.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        self.label_titulo = ctk.CTkLabel(
            self.frame_izquierdo, 
            text="Ingrese base (b), altura (h) y\nposición del centroide (Zc, Yc)", 
            font=("Arial", 14, "bold"),
            justify="center"
        )
        self.label_titulo.pack(pady=15, side="top")
        
        # --- BOTONES FIJOS ABAJO ---
        self.btn_atras = ctk.CTkButton(self.frame_izquierdo, text="ATRÁS", fg_color="#7D7D7D", hover_color="#5A5A5A", command=self.regresar)
        self.btn_atras.pack(side="bottom", pady=15, padx=20, fill="x")
        
        self.btn_continuar = ctk.CTkButton(self.frame_izquierdo, text="CONTINUAR", fg_color="#2ecc71", hover_color="#27ae60", command=self.procesar_y_continuar)
        self.btn_continuar.pack(side="bottom", pady=5, padx=20, fill="x")
        
        # --- CAMPOS DE ENTRADA PERMANENTES ---
        self.entradas = {}
        self.crear_campo_entrada("Base (b):", "b")
        self.crear_campo_entrada("Altura (h):", "h")
        self.crear_campo_entrada("Zc (Centroide Z):", "zc")
        self.crear_campo_entrada("Yc (Centroide Y):", "yc")
        
        # --- BOTÓN DE AÑADIR BLOQUE ---
        self.btn_añadir = ctk.CTkButton(self.frame_izquierdo, text="AÑADIR", fg_color="#3498db", hover_color="#2980b9", command=self.añadir_bloque)
        self.btn_añadir.pack(pady=15, padx=20, fill="x")
        
        # --- LABEL DE ERRORES DINÁMICOS ---
        self.label_error = ctk.CTkLabel(self.frame_izquierdo, text="", font=("Arial", 11, "bold"), text_color="#E74C3C", wraplength=220)
        self.label_error.pack(pady=10, padx=20)

        # --- FRAME DERECHO: MATPLOTLIB CONTENEDOR ---
        self.frame_derecho = ctk.CTkFrame(self, corner_radius=10)
        self.frame_derecho.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        self.fig, self.ax = plt.subplots(figsize=(5, 5), dpi=100)
        self.fig.patch.set_facecolor('#242424') 
        self.ax.set_facecolor('#1e1e1e')
        self.ax.tick_params(colors='white')
        
        self.canvas = FigureCanvasTkinterAgg(self.fig, master=self.frame_derecho)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # Dibujar plano inicial con ejes vacíos
        self.actualizar_grafico()

    def crear_campo_entrada(self, texto_label, clave_variable):
        lbl = ctk.CTkLabel(self.frame_izquierdo, text=texto_label, font=("Arial", 12))
        lbl.pack(pady=(5, 1), padx=20, anchor="w")
        
        txt = ctk.CTkEntry(self.frame_izquierdo)
        txt.pack(pady=(0, 5), padx=20, fill="x")

        # VINCULACIÓN NUEVA: Ejecuta la previsualización al escribir
        txt.bind("<KeyRelease>", self.trazar_previsualizacion)

        self.entradas[clave_variable] = txt

    def trazar_previsualizacion(self, event=None):
        """Intenta leer los campos actuales para dibujar el bloque tentativo."""
        try:
            b = float(self.entradas["b"].get().strip())
            h = float(self.entradas["h"].get().strip())
            zc = float(self.entradas["zc"].get().strip())
            yc = float(self.entradas["yc"].get().strip())
            
            if b > 0 and h > 0:
                bloque_temporal = [b, h, zc, yc]
                # Redibujamos pasando el bloque que se está editando
                self.actualizar_grafico(bloque_temporal)
                return
        except ValueError:
            pass
        
        # Si los campos están incompletos o tienen letras, dibuja solo los guardados
        self.actualizar_grafico()

    def limpiar_entradas(self):
        """Limpia los campos para poder ingresar el siguiente rectángulo."""
        for widget in self.entradas.values():
            widget.delete(0, 'end')
        self.label_error.configure(text="")

    def añadir_bloque(self):
        try:
            # 1. Recuperar y validar que sean números
            b = float(self.entradas["b"].get().strip())
            h = float(self.entradas["h"].get().strip())
            zc = float(self.entradas["zc"].get().strip())
            yc = float(self.entradas["yc"].get().strip())
            
            if b <= 0 or h <= 0:
                self.label_error.configure(text="⚠️ Error: Dimensiones b y h deben ser mayores a cero.")
                return
                
            nuevo_bloque = [b, h, zc, yc]
            
            # 2. Validar Intersecciones (No secciones cruzadas)
            if calculos_geometria.verificar_interseccion(nuevo_bloque, self.lista_bloques):
                self.label_error.configure(text="⚠️ Error: El bloque se intersecta con una sección existente.")
                return
                
            # 3. Validar Conectividad (No bloques flotantes aislados)
            if not calculos_geometria.verificar_conectividad(nuevo_bloque, self.lista_bloques):
                self.label_error.configure(text="⚠️ Error: El bloque no está en contacto con el perfil existente.")
                return
            
            # Si pasa los filtros, se agrega a la memoria
            self.lista_bloques.append(nuevo_bloque)
            self.limpiar_entradas()
            self.actualizar_grafico()
            
        except ValueError:
            self.label_error.configure(text="⚠️ Alerta: Introduce solo valores numéricos válidos.")

    def actualizar_grafico(self, bloque_temporal=None):
        self.ax.clear()
        self.ax.grid(True, color='#444444', linestyle='--')
        self.ax.set_title("Previsualización Geométrica (Z+ Izquierda)", color="white", fontsize=12)
        
        self.ax.invert_xaxis()
        self.ax.axhline(0, color='white', linewidth=1.2)
        self.ax.axvline(0, color='white', linewidth=1.2)
        self.ax.set_xlabel("Eje Z", color="white")
        self.ax.set_ylabel("Eje Y", color="white")
        
        # 1. Dibujar los bloques oficiales que ya se agregaron
        for bloque in self.lista_bloques:
            b, h, zc, yc = bloque
            z_inf_izq = zc - b/2
            y_inf_izq = yc - h/2
            poligono = plt.Rectangle(
                (z_inf_izq, y_inf_izq), b, h, 
                edgecolor='cyan', facecolor='cyan', alpha=0.4, lw=2
            )
            self.ax.add_patch(poligono)
            
        # 2. NUEVO: Dibujar el bloque tentativo si el usuario está escribiendo
        if bloque_temporal is not None:
            b_t, h_t, zc_t, yc_t = bloque_temporal
            z_inf_izq_t = zc_t - b_t/2
            y_inf_izq_t = yc_t - h_t/2
            
            # Lo dibujamos naranja y con borde discontinuo (dashed)
            poligono_temporal = plt.Rectangle(
                (z_inf_izq_t, y_inf_izq_t), b_t, h_t, 
                edgecolor='#E67E22', facecolor='none', linestyle='--', lw=2, alpha=0.8
            )
            self.ax.add_patch(poligono_temporal)
            
        # Ajustar los límites dinámicos de los ejes
        if not self.lista_bloques and bloque_temporal is None:
            self.ax.set_xlim(10, -1)
            self.ax.set_ylim(-1, 10)
        else:
            self.ax.relim()
            self.ax.autoscale_view()
            
        self.canvas.draw()

    def procesar_y_continuar(self):
        if not self.lista_bloques:
            messagebox.showwarning("Sin elementos", "Debe añadir al menos un bloque antes de continuar.")
            return
            
        try:
            # 1. Ejecutamos el motor de Steiner
            resultados = calculos_geometria.calcular_perfil_compuesto(self.lista_bloques)
            print("CÁLCULOS EXITOSOS EN OPCIÓN B:", resultados)
            
            # 2. EXTRAER VALORES CON LAS CLAVES CORRECTAS
            area = resultados.get('area', resultados.get('Area', 0.0))
            izc = resultados.get('Izc', 0.0)
            iyc = resultados.get('Iyc', 0.0)
            izyc = resultados.get('Izyc', 0.0)
            zc_g = resultados.get('Cz', 0.0)
            yc_g = resultados.get('Cy', 0.0)
            
            # 3. CONSTRUIR EL MENSAJE DETALLADO PARA EL DIÁLOGO
            mensaje_resultados = (
                f"Perfil Analizado: Compuesto por Bloques\n"
                f"Área Total: {area:.4f}\n"
                f"Centroide G: ({zc_g:.4f}, {yc_g:.4f})\n\n"
                f"--- Inercias Centroidales ---\n"
                f"Iz: {izc:.4f}\n"
                f"Iy: {iyc:.4f}\n"
                f"Izy: {izyc:.4f}"
            )
            
            # --- NUEVO: MARCAR EL CENTROIDE EN EL GRÁFICO 2D ---
            # Graficamos un punto rojo ('ro') o una cruz naranja en la posición del centroide global
            self.ax.plot(zc_g, yc_g, marker='X', color='#E74C3C', markersize=10, label=f'Centroide G\n({zc_g:.2f}, {yc_g:.2f})')
            self.ax.legend(loc='upper right', labelcolor='white', facecolor='#1e1e1e')
            self.canvas.draw() # Refrescamos el gráfico antes de congelar con el messagebox

            messagebox.showinfo("Sección Completada", mensaje_resultados)
            
            # 4. FUSIÓN GEOMÉTRICA REAL DE POLÍGONOS (Soporta N bloques)
            try:
                from shapely.geometry import box
                from shapely.ops import unary_union
                
                poligonos = []
                v_locales = resultados.get('vertices_locales', [])
                
                # Modificamos la lectura para asegurar que agrupe correctamente los bloques de 4 en 4
                num_bloques = len(v_locales) // 4
                for n in range(num_bloques):
                    bloque_pts = v_locales[n*4 : (n+1)*4]
                    if len(bloque_pts) == 4:
                        xs = [p[0] for p in bloque_pts]
                        ys = [p[1] for p in bloque_pts]
                        poligonos.append(box(min(xs), min(ys), max(xs), max(ys)))
                
                if poligonos:
                    # Fusionamos todos los bloques ingresados en un único sólido
                    perfil_fusionado = unary_union(poligonos)
                    # Extraemos el perímetro exterior real ordenado secuencialmente
                    vertices_ordenados = list(perfil_fusionado.exterior.coords)[:-1]
                else:
                    vertices_ordenados = v_locales
                
            except Exception as e_shapely:
                print("Error con Shapely, usando fallback de vértices por defecto:", e_shapely)
                vertices_ordenados = resultados.get('vertices_locales', [])
            
            datos_geo_formateados = {
                "area": area,
                "Izc": izc,
                "Iyc": iyc,
                "Izyc": izyc,
                "vertices_locales": vertices_ordenados
            }
            
            # Importación local para evitar bucles circulares
            from ventana_seccion_2 import VentanaSeccion2
            
            # 5. LANZAR SECCIÓN 2
            ventana_cargas = VentanaSeccion2(ventana_padre=self.ventana_padre, datos_geometria=datos_geo_formateados)
            ventana_cargas.deiconify()
            
            # 6. CIERRE LIMPIO
            try:
                plt.close(self.fig)
            except Exception:
                pass
            
            self.withdraw()
            self.after(100, self.destroy)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Ocurrió un error en el traspaso de datos: {e}")

    def regresar(self):
        try:
            plt.close(self.fig)
        except Exception:
            pass
        self.ventana_padre.deiconify()
        self.destroy()