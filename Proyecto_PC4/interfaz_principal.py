import customtkinter as ctk
from tkinter import messagebox  

from ventana_opcion_A import VentanaOpcionA
from ventana_opcion_B import VentanaOpcionB
from ventana_opcion_C import VentanaOpcionC

# Configuración general de CustomTkinter
ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue")  

class VentanaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal
        self.title("TRABAJO 7: ANALISIS DE INERCIA")
        self.geometry("800x600")

        # Variable para almacenar la opción seleccionada
        self.opcion_seleccionada = None

        # Paleta de colores estándar [Modo Claro, Modo Oscuro]
        self.color_azul_base = ["#3B8ED0", "#1F6AA5"]
        self.color_azul_hover = ["#327BAE", "#1A5887"] # El oscurecido al pasar el cursor
        self.color_naranja = "#E67E22"

        # --- EVENTO IMPORTANTE: Clic fuera de los botones deselecciona ---
        # Vinculamos el clic izquierdo en la ventana de fondo para limpiar selección
        self.bind("<Button-1>", self.click_fuera)

        # --- Creación de Widgets ---

        # 1. Encabezado Principal (Título)
        self.label_titulo = ctk.CTkLabel(
            self, 
            text="TRABAJO 7:\nPROGRAMA PARA EL ANALISIS DE FLEXION ASIMETRICA \nY EJES PRINCIPALES DE INERCIA", 
            font=("Arial", 20, "bold", "underline"),
            justify="center"
        )
        self.label_titulo.pack(pady=40)  

        # 2. Instrucción
        self.label_instruccion = ctk.CTkLabel(
            self, 
            text="Seleccione la forma del perfil que desea crear para analizar:", 
            font=("Arial", 14)
        )
        self.label_instruccion.pack(pady=10)

        # 3. Contenedor para las opciones A, B, C (Frame)
        self.frame_opciones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_opciones.pack(pady=30)

        # Evitamos que el clic en el frame transparente deseleccione las opciones
        self.frame_opciones.bind("<Button-1>", lambda e: "break")

        # 3a. Botón Opción A
        self.btn_opcion_a = ctk.CTkButton(
            self.frame_opciones, 
            text="OPCION A:\nPerfiles base", 
            font=("Arial", 12, "bold"),
            height=80, width=180,
            command=lambda: self.seleccionar_opcion("A")
        )
        self.btn_opcion_a.pack(side="left", padx=20) 

        # 3b. Botón Opción B
        self.btn_opcion_b = ctk.CTkButton(
            self.frame_opciones, 
            text="OPCION B:\nCompuestos por bloques", 
            font=("Arial", 12, "bold"),
            height=80, width=180,
            command=lambda: self.seleccionar_opcion("B")
        )
        self.btn_opcion_b.pack(side="left", padx=20)

        # 3c. Botón Opción C
        self.btn_opcion_c = ctk.CTkButton(
            self.frame_opciones, 
            text="OPCION C:\nPolígono libre", 
            font=("Arial", 12, "bold"),
            height=80, width=180,
            command=lambda: self.seleccionar_opcion("C")
        )
        self.btn_opcion_c.pack(side="left", padx=20)

        # 4. CONTENEDOR INFERIOR (Integrantes y Botón Continuar)
        self.frame_inferior = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inferior.pack(side="bottom", fill="x", padx=50, pady=40)
        self.frame_inferior.bind("<Button-1>", lambda e: "break") # Evita deseleccionar al tocar el fondo inferior

        # 4a. Panel de Integrantes
        self.frame_integrantes = ctk.CTkFrame(self.frame_inferior, fg_color="transparent")
        self.frame_integrantes.pack(side="left", anchor="w")

        self.label_integrantes_titulo = ctk.CTkLabel(
            self.frame_integrantes, 
            text="Integrantes:", 
            font=("Arial", 12, "bold"),
            justify="left"
        )
        self.label_integrantes_titulo.pack(anchor="w")

        texto_integrantes = "-  HERRERA SAENZ, JUNIOR ANGEL\n-  MORE ESPINOZA, JUAN JOSE\n-  TRINIDAD FLORES, LENIN YASSEL\n-  FLORES SAAVEDRA, NEIL FERNANDO"
        self.label_integrantes_lista = ctk.CTkLabel(
            self.frame_integrantes, 
            text=texto_integrantes, 
            font=("Arial", 12),
            justify="left"
        )
        self.label_integrantes_lista.pack(anchor="w", pady=5)

        # 4b. Botón CONTINUAR
        self.btn_continuar = ctk.CTkButton(
            self.frame_inferior, 
            text="CONTINUAR", 
            font=("Arial", 14, "bold"),
            fg_color="#2ECC71",  
            hover_color="#27AE60",
            height=40, width=140,
            command=self.procesar_continuar
        )
        self.btn_continuar.pack(side="right", anchor="s")

    # --- Lógica de Control de la Ventana ---

    def seleccionar_opcion(self, opcion):
        """Maneja el cambio visual de los botones eliminando el parpadeo del hover"""
        self.opcion_seleccionada = opcion
        
        # Primero restablecemos todos los botones a su estado original (Azul y Hover Azul)
        self.btn_opcion_a.configure(fg_color=self.color_azul_base, hover_color=self.color_azul_hover)
        self.btn_opcion_b.configure(fg_color=self.color_azul_base, hover_color=self.color_azul_hover)
        self.btn_opcion_c.configure(fg_color=self.color_azul_base, hover_color=self.color_azul_hover)

        # Forzamos que el botón seleccionado mantenga el naranja tanto en base como en hover
        if opcion == "A":
            self.btn_opcion_a.configure(fg_color=self.color_naranja, hover_color=self.color_naranja)
        elif opcion == "B":
            self.btn_opcion_b.configure(fg_color=self.color_naranja, hover_color=self.color_naranja)
        elif opcion == "C":
            self.btn_opcion_c.configure(fg_color=self.color_naranja, hover_color=self.color_naranja)

    def click_fuera(self, evento):
        """Si el usuario hace clic en el fondo vacío, se limpia la selección"""
        # Verificamos si el clic fue directamente en la ventana principal o etiquetas de fondo
        if evento.widget == self or isinstance(evento.widget, ctk.CTkLabel):
            self.opcion_seleccionada = None
            # Restablecemos los tres botones al azul base
            self.btn_opcion_a.configure(fg_color=self.color_azul_base, hover_color=self.color_azul_hover)
            self.btn_opcion_b.configure(fg_color=self.color_azul_base, hover_color=self.color_azul_hover)
            self.btn_opcion_c.configure(fg_color=self.color_azul_base, hover_color=self.color_azul_hover)
            # Quita el foco de teclado del botón para que no se quede una línea punteada
            self.focus()

    def procesar_continuar(self):
        """Verifica la selección antes de pasar a la siguiente etapa"""
        if self.opcion_seleccionada is None:
            messagebox.showwarning("Atención", "Por favor, seleccione una forma de perfil antes de continuar.")
        else:
            if self.opcion_seleccionada == "A":
                # Llama a la ventana intermedia de perfiles base pasando 'self' (la principal)
                VentanaOpcionA(self)
            elif self.opcion_seleccionada == "B":
                # Llama a la ventana de compuestos por bloques pasando 'self' (la principal)
                VentanaOpcionB(self)
            elif self.opcion_seleccionada == "C":
                # Llama a la ventana de polígono libre pasando 'self' (la principal)
                VentanaOpcionC(self)

    def recibir_resultados_geometria(self, datos):
        """Guarda los datos geométricos calculados y avanza a la Sección 2."""
        self.datos_seccion_actual = datos  # Guarda en la memoria del padre
        
        # Ocultamos la interfaz principal temporalmente
        self.withdraw()
        
        # Importamos e instanciamos la nueva Sección 2 tridimensional
        from ventana_seccion_2 import VentanaSeccion2
        ventana_s2 = VentanaSeccion2(self, self.datos_seccion_actual)
        ventana_s2.grab_set()

# Para correr el programa
if __name__ == "__main__":
    app = VentanaPrincipal()
    app.mainloop()