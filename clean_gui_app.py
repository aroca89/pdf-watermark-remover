#!/usr/bin/env python3
"""
PDF Watermark Remover GUI - Version limpia
Interfaz grafica para eliminar marcas de agua de PDFs
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import threading
import time
import queue
import subprocess
import tempfile
import shutil
from pathlib import Path

# Importaciones para el procesamiento
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, WebDriverException
    
    from pdf2image import convert_from_path
    from PIL import Image
    
    DEPENDENCIES_OK = True
except ImportError as e:
    DEPENDENCIES_OK = False
    MISSING_DEPS = str(e)


class PDFProcessor:
    """Procesador de PDFs simplificado integrado"""
    
    def __init__(self, output_folder):
        self.output_folder = output_folder
        self.temp_folder = None
        self.driver = None
        self.processing = True
        
    def log(self, message):
        """Log interno para el procesador"""
        print(f"[PROCESSOR] {message}")
        
    def create_temp_folder(self):
        """Crear carpeta temporal"""
        try:
            self.temp_folder = tempfile.mkdtemp(prefix="pdf_watermark_")
            self.log(f"Carpeta temporal: {self.temp_folder}")
            return True
        except Exception as e:
            self.log(f"Error creando carpeta temporal: {e}")
            return False
    
    def cleanup(self):
        """Limpiar recursos"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        if self.temp_folder and os.path.exists(self.temp_folder):
            try:
                shutil.rmtree(self.temp_folder)
            except:
                pass
    
    def setup_chrome(self, headless=True):
        """Configurar Chrome"""
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Configuracion de descarga
            prefs = {
                "download.default_directory": self.temp_folder,
                "download.prompt_for_download": False,
                "plugins.always_open_pdf_externally": True
            }
            chrome_options.add_experimental_option("prefs", prefs)
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return True
            
        except Exception as e:
            self.log(f"Error configurando Chrome: {e}")
            return False
    
    def pdf_to_images(self, pdf_path):
        """Convertir PDF a imagenes"""
        try:
            images = convert_from_path(pdf_path, dpi=300)
            image_paths = []
            
            for i, image in enumerate(images, 1):
                image_path = os.path.join(self.temp_folder, f"page_{i:03d}.png")
                image.save(image_path, 'PNG')
                image_paths.append(image_path)
                
            self.log(f"Convertidas {len(image_paths)} paginas a imagenes")
            return image_paths
            
        except Exception as e:
            self.log(f"Error convirtiendo PDF: {e}")
            return []
    
    def process_image_online(self, image_path):
        """Procesar imagen online"""
        try:
            # Navegar al sitio
            self.driver.get("https://www.watermarkremover.io/es/image-watermark-remover")
            time.sleep(3)
            
            # Subir imagen
            file_input = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
            )
            file_input.send_keys(os.path.abspath(image_path))
            
            # Esperar procesamiento
            time.sleep(5)
            
            # Buscar boton descarga
            download_button = WebDriverWait(self.driver, 120).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".download-btn, button[download]"))
            )
            
            # Descargar
            files_before = set(os.listdir(self.temp_folder))
            download_button.click()
            time.sleep(5)
            
            # Encontrar archivo descargado
            files_after = set(os.listdir(self.temp_folder))
            new_files = files_after - files_before
            
            if new_files:
                downloaded = list(new_files)[0]
                return os.path.join(self.temp_folder, downloaded)
            
            return None
            
        except Exception as e:
            self.log(f"Error procesando imagen: {e}")
            return None
    
    def images_to_pdf(self, image_paths, output_path):
        """Convertir imagenes a PDF"""
        try:
            if not image_paths:
                return False
                
            images = []
            for img_path in sorted(image_paths):
                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    images.append(img)
            
            if images:
                images[0].save(
                    output_path,
                    "PDF",
                    save_all=True,
                    append_images=images[1:] if len(images) > 1 else []
                )
                return True
            return False
            
        except Exception as e:
            self.log(f"Error creando PDF: {e}")
            return False
    
    def process_pdf(self, pdf_path, headless=True):
        """Procesar PDF completo"""
        if not self.processing:
            return None
            
        try:
            # Crear carpeta temporal
            if not self.create_temp_folder():
                return None
            
            # Configurar Chrome
            if not self.setup_chrome(headless):
                return None
            
            # Convertir PDF a imagenes
            image_paths = self.pdf_to_images(pdf_path)
            if not image_paths:
                return None
            
            # Procesar imagenes
            processed_images = []
            for i, img_path in enumerate(image_paths, 1):
                if not self.processing:
                    break
                    
                self.log(f"Procesando imagen {i}/{len(image_paths)}")
                processed = self.process_image_online(img_path)
                
                if processed:
                    processed_images.append(processed)
                
                time.sleep(2)
            
            # Crear PDF final
            if processed_images and self.processing:
                base_name = Path(pdf_path).stem
                output_name = f"Nwm_{base_name}.pdf"
                output_path = os.path.join(self.output_folder, output_name)
                
                if self.images_to_pdf(processed_images, output_path):
                    return output_path
            
            return None
            
        except Exception as e:
            self.log(f"Error general: {e}")
            return None
        finally:
            self.cleanup()


class PDFWatermarkGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Watermark Remover v2.0")
        self.root.geometry("800x600")
        
        # Variables
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar(value=os.path.join(os.getcwd(), "processed_pdfs"))
        self.headless_mode = tk.BooleanVar(value=True)
        self.processing = False
        self.processor = None
        
        # Queue para logs
        self.log_queue = queue.Queue()
        
        # Configurar interfaz
        self.setup_ui()
        self.update_logs()
        
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titulo
        title_label = ttk.Label(main_frame, text="PDF Watermark Remover", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Entrada
        input_frame = ttk.LabelFrame(main_frame, text="Archivo de entrada", padding="5")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        entry_frame = ttk.Frame(input_frame)
        entry_frame.pack(fill=tk.X)
        
        ttk.Entry(entry_frame, textvariable=self.input_path, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(entry_frame, text="Seleccionar PDF", command=self.select_file).pack(side=tk.RIGHT)
        
        # Salida
        output_frame = ttk.LabelFrame(main_frame, text="Carpeta de salida", padding="5")
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        output_entry_frame = ttk.Frame(output_frame)
        output_entry_frame.pack(fill=tk.X)
        
        ttk.Entry(output_entry_frame, textvariable=self.output_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(output_entry_frame, text="Seleccionar", command=self.select_output).pack(side=tk.RIGHT)
        
        # Opciones
        options_frame = ttk.LabelFrame(main_frame, text="Opciones", padding="5")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Checkbutton(options_frame, text="Modo headless (sin ventana del navegador)", 
                       variable=self.headless_mode).pack(anchor=tk.W)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        self.start_btn = ttk.Button(button_frame, text="INICIAR PROCESAMIENTO", 
                                   command=self.start_processing)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.cancel_btn = ttk.Button(button_frame, text="CANCELAR", 
                                    command=self.cancel_processing, state='disabled')
        self.cancel_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Verificar Deps", 
                  command=self.check_dependencies).pack(side=tk.LEFT, padx=5)
        
        # Progreso
        self.progress_var = tk.StringVar(value="Listo")
        ttk.Label(main_frame, textvariable=self.progress_var).pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Logs
        log_frame = ttk.LabelFrame(main_frame, text="Registro", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Botones de log
        log_btn_frame = ttk.Frame(log_frame)
        log_btn_frame.pack(pady=5)
        
        ttk.Button(log_btn_frame, text="Limpiar", command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_btn_frame, text="Guardar", command=self.save_logs).pack(side=tk.LEFT)
    
    def log_message(self, message):
        """Agregar mensaje al log"""
        self.log_queue.put(f"{time.strftime('%H:%M:%S')} - {message}")
    
    def update_logs(self):
        """Actualizar ventana de logs"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, message + "\n")
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        
        self.root.after(100, self.update_logs)
    
    def select_file(self):
        """Seleccionar archivo PDF"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar PDF",
            filetypes=[("PDF files", "*.pdf")]
        )
        if file_path:
            self.input_path.set(file_path)
            self.log_message(f"Archivo seleccionado: {os.path.basename(file_path)}")
    
    def select_output(self):
        """Seleccionar carpeta de salida"""
        folder_path = filedialog.askdirectory(title="Seleccionar carpeta de salida")
        if folder_path:
            self.output_path.set(folder_path)
            self.log_message(f"Carpeta de salida: {folder_path}")
    
    def check_dependencies(self):
        """Verificar dependencias"""
        self.log_message("Verificando dependencias...")
        
        if not DEPENDENCIES_OK:
            self.log_message(f"ERROR: Dependencias faltantes - {MISSING_DEPS}")
            messagebox.showerror("Dependencias", 
                               f"Faltan dependencias:\n{MISSING_DEPS}\n\n"
                               "Instala con:\npip install selenium pdf2image pillow")
            return False
        
        # Verificar ChromeDriver
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome(options=chrome_options)
            driver.quit()
            self.log_message("Chrome/ChromeDriver: OK")
        except Exception as e:
            self.log_message(f"ERROR Chrome/ChromeDriver: {e}")
            messagebox.showerror("ChromeDriver", 
                               "ChromeDriver no encontrado.\n"
                               "Descarga desde: https://chromedriver.chromium.org/")
            return False
        
        self.log_message("Todas las dependencias OK")
        messagebox.showinfo("Dependencias", "Todas las dependencias estan correctas")
        return True
    
    def start_processing(self):
        """Iniciar procesamiento"""
        if not self.input_path.get():
            messagebox.showerror("Error", "Selecciona un archivo PDF")
            return
        
        if not os.path.exists(self.input_path.get()):
            messagebox.showerror("Error", "El archivo no existe")
            return
        
        # Crear carpeta de salida
        try:
            os.makedirs(self.output_path.get(), exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear carpeta de salida: {e}")
            return
        
        # Configurar UI
        self.processing = True
        self.start_btn.config(state='disabled')
        self.cancel_btn.config(state='normal')
        self.progress_bar.start()
        self.progress_var.set("Procesando...")
        
        self.log_message("Iniciando procesamiento...")
        
        # Iniciar hilo de procesamiento
        thread = threading.Thread(target=self.process_worker, daemon=True)
        thread.start()
    
    def process_worker(self):
        """Worker de procesamiento"""
        try:
            self.processor = PDFProcessor(self.output_path.get())
            
            # Redirigir logs del processor a la GUI
            import logging
            logging.basicConfig(level=logging.INFO)
            
            result = self.processor.process_pdf(
                self.input_path.get(), 
                headless=self.headless_mode.get()
            )
            
            if result and self.processing:
                self.log_message(f"EXITO: PDF procesado - {os.path.basename(result)}")
                self.root.after(0, lambda: messagebox.showinfo(
                    "Exito", f"PDF procesado exitosamente!\n\n{os.path.basename(result)}"
                ))
            elif self.processing:
                self.log_message("ERROR: No se pudo procesar el PDF")
                self.root.after(0, lambda: messagebox.showerror(
                    "Error", "No se pudo procesar el PDF"
                ))
            
        except Exception as e:
            self.log_message(f"ERROR: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        
        finally:
            self.root.after(0, self.finish_processing)
    
    def cancel_processing(self):
        """Cancelar procesamiento"""
        self.processing = False
        if self.processor:
            self.processor.processing = False
        self.log_message("Cancelando procesamiento...")
    
    def finish_processing(self):
        """Finalizar procesamiento"""
        self.processing = False
        self.start_btn.config(state='normal')
        self.cancel_btn.config(state='disabled')
        self.progress_bar.stop()
        self.progress_var.set("Listo")
    
    def clear_logs(self):
        """Limpiar logs"""
        self.log_text.delete(1.0, tk.END)
    
    def save_logs(self):
        """Guardar logs"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt")]
            )
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log_message(f"Logs guardados: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar los logs: {e}")


def main():
    """Funcion principal"""
    root = tk.Tk()
    
    # Centrar ventana
    root.update_idletasks()
    width = 800
    height = 600
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Crear app
    app = PDFWatermarkGUI(root)
    
    # Iniciar
    root.mainloop()


if __name__ == "__main__":
    main()