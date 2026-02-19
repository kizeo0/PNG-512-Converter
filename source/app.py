#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import tkinter as tk
from tkinter import messagebox

# -------------------- MANEJO DE RECURSOS (PARA PYINSTALLER) --------------------
def resource_path(relative_path):
    """ Obtiene la ruta absoluta de los recursos para que funcione en el .exe """
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# -------------------- VERIFICACIÓN DE DEPENDENCIAS --------------------
try:
    from PIL import Image, ImageOps
except ImportError:
    messagebox.showerror("Error", "No se encontró Pillow. Instálalo con: pip install Pillow")
    sys.exit(1)

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False

# -------------------- CONFIGURACIÓN DE COLORES --------------------
COLORS = {
    "bg_dark": "#0a0f1a",
    "bg_medium": "#141c2c",
    "bg_light": "#1e2a3a",
    "accent": "#2a4b7c",
    "accent_light": "#3a6ea5",
    "text": "#e0e5f0",
    "text_secondary": "#8a9bb5",
    "border": "#1f3a5f",
    "success": "#2ecc71",
    "shadow": "#05070c"
}

# -------------------- FUNCIÓN DE PROCESAMIENTO --------------------
def process_images(file_list):
    processed = 0
    errors = []
    for file_path in file_list:
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'):
            errors.append(f"{os.path.basename(file_path)}: formato no soportado")
            continue
        try:
            with Image.open(file_path) as img:
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')
                img_fitted = ImageOps.fit(img, (512, 512), method=Image.LANCZOS)
                base = os.path.splitext(file_path)[0]
                output_path = base + "_nuevo.png"
                img_fitted.save(output_path, 'PNG')
                processed += 1
        except Exception as e:
            errors.append(f"{os.path.basename(file_path)}: {str(e)}")
    return processed, errors

# -------------------- BOTÓN PERSONALIZADO --------------------
class RoundedButton(tk.Canvas):
    def __init__(self, master, text, command, width=120, height=35, corner_radius=10,
                 color=COLORS["accent"], hover_color=COLORS["accent_light"],
                 text_color=COLORS["text"], *args, **kwargs):
        super().__init__(master, width=width, height=height, highlightthickness=0,
                         bg=COLORS["bg_dark"], *args, **kwargs)
        self.command = command
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.corner_radius = corner_radius
        self.shadow = self.create_rounded_rect(2, 2, width, height, fill=COLORS["shadow"], outline="")
        self.rect = self.create_rounded_rect(0, 0, width-2, height-2, fill=color, outline="")
        self.text_id = self.create_text((width-2)//2, (height-2)//2, text=text, fill=text_color, font=("Arial", 10, "bold"))
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)

    def create_rounded_rect(self, x1, y1, x2, y2, **kwargs):
        r = self.corner_radius
        points = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, x2, y2, x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)

    def on_enter(self, event):
        self.itemconfig(self.rect, fill=self.hover_color)
        self.move(self.shadow, -1, -1)

    def on_leave(self, event):
        self.itemconfig(self.rect, fill=self.color)
        self.move(self.shadow, 1, 1)

    def on_click(self, event):
        if self.command: self.command()

# -------------------- VENTANA PRINCIPAL --------------------
class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PNG 512 CONVERTER")
        self.root.geometry("600x700")
        self.root.configure(bg=COLORS["bg_dark"])
        
        main_frame = tk.Frame(root, bg=COLORS["bg_dark"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(main_frame, text="CONVERSOR DE IMÁGENES", font=("Arial", 16, "bold"), fg=COLORS["accent_light"], bg=COLORS["bg_dark"]).pack(pady=(0, 10))
        tk.Label(main_frame, text="Cualquier imagen a PNG 512x512 by KiZeo", font=("Arial", 10), fg=COLORS["text_secondary"], bg=COLORS["bg_dark"]).pack(pady=(0, 20))

        drop_shadow = tk.Frame(main_frame, bg=COLORS["shadow"])
        drop_shadow.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        drop_frame = tk.Frame(drop_shadow, bg=COLORS["bg_light"], bd=0)
        drop_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        self.drop_canvas = tk.Canvas(drop_frame, bg=COLORS["bg_medium"], highlightthickness=1, highlightcolor=COLORS["border"], bd=0)
        self.drop_canvas.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.drop_canvas.bind("<Button-1>", lambda e: self.select_files())
        self.drop_canvas.config(cursor="hand2")

        self.drop_text = self.drop_canvas.create_text(300, 150, text="📁 Suelta aquí tus imágenes\n(JPEG, PNG, GIF, BMP, TIFF, WEBP)", fill=COLORS["text_secondary"], font=("Arial", 12), justify=tk.CENTER)

        list_frame = tk.Frame(main_frame, bg=COLORS["bg_dark"])
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        scrollbar = tk.Scrollbar(list_frame, bg=COLORS["bg_light"])
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(list_frame, bg=COLORS["bg_medium"], fg=COLORS["text"], selectbackground=COLORS["accent"], bd=0, font=("Arial", 10), yscrollcommand=scrollbar.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        button_frame = tk.Frame(main_frame, bg=COLORS["bg_dark"])
        button_frame.pack(fill=tk.X, pady=10)

        self.clear_btn = RoundedButton(button_frame, text="LIMPIAR", command=self.clear_list, width=100, color=COLORS["bg_light"])
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        self.select_btn = RoundedButton(button_frame, text="SELECCIONAR", command=self.select_files, color=COLORS["bg_light"])
        self.select_btn.pack(side=tk.LEFT, padx=5)

        self.process_btn = RoundedButton(button_frame, text="CONVERTIR", command=self.process_dropped)
        self.process_btn.pack(side=tk.RIGHT, padx=5)

        self.dropped_files = []
        if HAS_DND:
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.on_drop)
        self.drop_canvas.bind("<Configure>", self.on_canvas_configure)

    def on_canvas_configure(self, event):
        self.drop_canvas.coords(self.drop_text, event.width//2, event.height//2)

    def on_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        for f in files:
            f = f.strip('{}')
            if f not in self.dropped_files:
                self.dropped_files.append(f)
                self.listbox.insert(tk.END, os.path.basename(f))

    def select_files(self):
        from tkinter import filedialog
        files = filedialog.askopenfilenames(title="Selecciona imágenes", filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp")])
        for f in files:
            if f not in self.dropped_files:
                self.dropped_files.append(f)
                self.listbox.insert(tk.END, os.path.basename(f))

    def clear_list(self):
        self.listbox.delete(0, tk.END)
        self.dropped_files = []

    def process_dropped(self):
        if not self.dropped_files:
            messagebox.showinfo("Información", "No hay archivos para procesar.")
            return
        processed, errors = process_images(self.dropped_files)
        msg = f"✅ Se procesaron {processed} imágenes."
        if errors: msg += "\n\n❌ Errores:\n" + "\n".join(errors)
        messagebox.showinfo("Resultado", msg)
        if messagebox.askyesno("Limpiar", "¿Quieres vaciar la lista?"): self.clear_list()

def set_window_icon(root):
    """Establece el icono usando la ruta resuelta para PyInstaller."""
    try:
        icon_path = resource_path("app.ico")
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception:
        pass

def main():
    try:
        root = TkinterDnD.Tk() if HAS_DND else tk.Tk()
    except Exception:
        root = tk.Tk()
    
    set_window_icon(root)
    app = ImageConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
