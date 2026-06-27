import os
from PIL import Image
import customtkinter as ctk
from tkinter import messagebox
from ventana_datos_perfil import VentanaDatosPerfil

class VentanaOpcionA(ctk.CTkToplevel):
    def __init__(self, ventana_padre):
        super().__init__(ventana_padre)

        self.ventana_padre = ventana_padre
        self.title("OPCIÓN A: PERFILES BASE")
        self.geometry("800x650")
        
        # Ocultar la ventana principal mientras esta esté abierta
        self.ventana_padre.withdraw()
        
        # Al cerrar esta ventana desde la 'X', regresa a la principal
        self.protocol("WM_DELETE_WINDOW", self.regresar)

        # Variable para almacenar el perfil seleccionado
        self.perfil_seleccionado = None
        self.color_azul_base = ["#3B8ED0", "#1F6AA5"]
        self.color_azul_hover = ["#327BAE", "#1A5887"]
        self.color_naranja = "#E67E22"

        # Diccionarios para registrar los botones de cada sección
        self.botones_perfiles = {}

        # Clic en el fondo deselecciona
        self.bind("<Button-1>", self.click_fuera)

        # --- ESTRUCTURA DE WIDGETS ---

        # 1. Encabezado Principal (Se mantiene el título del proyecto)
        self.label_titulo = ctk.CTkLabel(
            self, 
            text="TRABAJO 7:\nPROGRAMA PARA EL ANÁLISIS DE FLEXIÓN ASIMÉTRICA \nY EJES PRINCIPALES DE INERCIA", 
            font=("Arial", 18, "bold", "underline"),
            justify="center"
        )
        self.label_titulo.pack(pady=20)

        # Subtítulo indicador de la opción
        self.label_subtitulo = ctk.CTkLabel(
            self, 
            text="OPCIÓN A: Perfiles base", 
            font=("Arial", 14, "bold")
        )
        self.label_subtitulo.pack(anchor="w", padx=50, pady=5)

        # 2. CONTENEDOR CON SCROLLBAR (Barra de desplazamiento lateral)
        self.scroll_contenedor = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_contenedor.pack(fill="both", expand=True, padx=40, pady=10)
        self.scroll_contenedor.bind("<Button-1>", lambda e: "break")

        # Columnas internas divididas por el separador
        # Columna Izquierda (Asimétricos)
        self.frame_asimetricos = ctk.CTkFrame(self.scroll_contenedor, fg_color="transparent")
        self.frame_asimetricos.grid(row=0, column=0, sticky="nsew", padx=10)
        
        # Línea divisoria central
        self.linea_divisoria = ctk.CTkFrame(self.scroll_contenedor, width=2, fg_color=["#D1D1D1", "#4A4A4A"])
        self.linea_divisoria.grid(row=0, column=1, sticky="ns", padx=20)

        # Columna Derecha (Simétricos)
        self.frame_simetricos = ctk.CTkFrame(self.scroll_contenedor, fg_color="transparent")
        self.frame_simetricos.grid(row=0, column=2, sticky="nsew", padx=10)

        # Ajustar pesos de las columnas para que se distribuyan equitativamente
        self.scroll_contenedor.grid_columnconfigure(0, weight=1)
        self.scroll_contenedor.grid_columnconfigure(2, weight=1)

        # --- SECCIÓN ASIMÉTRICOS ---
        self.label_asim_titulo = ctk.CTkLabel(self.frame_asimetricos, text="ASIMÉTRICOS", font=("Arial", 12, "bold"))
        self.label_asim_titulo.grid(row=0, column=0, columnspan=2, pady=10)

        perfiles_asim = ["Perfil L", "Perfil Z", "Perfil T"]
        self.crear_cuadrícula_botones(perfiles_asim, self.frame_asimetricos, columnas=2)

        # --- SECCIÓN SIMÉTRICOS ---
        self.label_sim_titulo = ctk.CTkLabel(self.frame_simetricos, text="SIMÉTRICOS", font=("Arial", 12, "bold"))
        self.label_sim_titulo.grid(row=0, column=0, columnspan=2, pady=10)

        # --- CAMBIO AQUÍ: Se eliminaron "Semicírculo" y "Cuarto de círculo" de la lista ---
        perfiles_sim = ["Perfil U", "Perfil H", "Círculo", "Elipse", "Rectángulo"]
        self.crear_cuadrícula_botones(perfiles_sim, self.frame_simetricos, columnas=2)

        # 3. CONTENEDOR INFERIOR (Botones ATRÁS y CONTINUAR)
        self.frame_inferior = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inferior.pack(side="bottom", fill="x", padx=50, pady=25)
        self.frame_inferior.bind("<Button-1>", lambda e: "break")

        self.btn_atras = ctk.CTkButton(
            self.frame_inferior, 
            text="ATRÁS", 
            font=("Arial", 14, "bold"),
            fg_color="#95A5A6",
            hover_color="#7F8C8D",
            height=40, width=140,
            command=self.regresar
        )
        self.btn_atras.pack(side="left")

        self.btn_continuar = ctk.CTkButton(
            self.frame_inferior, 
            text="CONTINUAR", 
            font=("Arial", 14, "bold"),
            fg_color="#2ECC71",  
            hover_color="#27AE60",
            height=40, width=140,
            command=self.procesar_continuar
        )
        self.btn_continuar.pack(side="right")

    def crear_cuadrícula_botones(self, lista_perfiles, contenedor_frame, columnas=2):
        """Genera dinámicamente los botones cuadrados con su respectiva imagen y texto"""
        for index, nombre in enumerate(lista_perfiles):
            fila = (index // columnas) + 1
            col = index % columnas

            nombre_archivo = nombre.lower().replace(" ", "_") + ".jpg"
            ruta_imagen = os.path.join("imagenes_perfiles_opcA", nombre_archivo)

            ctk_img = None
            if os.path.exists(ruta_imagen):
                try:
                    pil_img = Image.open(ruta_imagen)
                    ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(60, 60))
                except Exception as e:
                    print(f"Error al cargar la imagen {ruta_imagen}: {e}")

            btn = ctk.CTkButton(
                contenedor_frame,
                text=nombre,
                image=ctk_img,
                compound="top",
                font=("Arial", 11, "bold"),
                height=120, width=120,
                corner_radius=8,
                command=lambda n=nombre: self.seleccionar_perfil(n)
            )
            btn.grid(row=fila, column=col, padx=10, pady=10, sticky="nsew")
            
            self.botones_perfiles[nombre] = btn

    def seleccionar_perfil(self, nombre_perfil):
        """Aplica la misma lógica impecable de selección de color sin parpadeos"""
        self.perfil_seleccionado = nombre_perfil
        
        for btn in self.botones_perfiles.values():
            btn.configure(fg_color=self.color_azul_base, hover_color=self.color_azul_hover)

        self.botones_perfiles[nombre_perfil].configure(
            fg_color=self.color_naranja, 
            hover_color=self.color_naranja
        )

    def click_fuera(self, evento):
        """Permite deseleccionar si haces clic en zonas vacías de la interfaz"""
        if evento.widget == self or isinstance(evento.widget, ctk.CTkLabel):
            self.perfil_seleccionado = None
            for btn in self.botones_perfiles.values():
                btn.configure(fg_color=self.color_azul_base, hover_color=self.color_azul_hover)
            self.focus()

    def regresar(self):
        """Cierra esta ventana y restaura la interfaz principal"""
        self.destroy()
        self.ventana_padre.deiconify()

    def procesar_continuar(self):
        """Valida que exista selección antes de pasar a las subopciones de datos"""
        if self.perfil_seleccionado is None:
            messagebox.showwarning("Atención", "Por favor, seleccione un tipo de perfil antes de continuar.")
        else:
            ventana_datos = VentanaDatosPerfil(self, self.perfil_seleccionado)
            ventana_datos.grab_set()