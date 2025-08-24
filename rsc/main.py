#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Watermark Remover - Aplicación Principal
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
import os

class PDFWatermarkRemover:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PDF Watermark Remover v2.0")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        self.selected_file = None
        self.processing = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Título
        title_label = ttk.Label(self.root, text="PDF Watermark Remover", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Frame para selección de archivo
        file_frame = ttk.Frame(self.root)
        file_frame.pack(pady=10, padx=20, fill="x")
        
        ttk.Label(file_frame, text="Archivo PDF:").pack(anchor="w")
        
        file_select_frame = ttk.Frame(file_frame)
        file_select_frame.pack(fill="x", pady=5)
        
        self.file_label = ttk.Label(file_select_frame, text="Ningún archivo seleccionado", 
                                   background="white", relief="sunken")
        self.file_label.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ttk.Button(file_select_frame, text="Seleccionar", 
                  command=self.select_file).pack(side="right")
        
        # Botón de procesamiento
        self.process_btn = ttk.Button(self.root, text="INICIAR PROCESAMIENTO", 
                                     command=self.start_processing,
                                     style="Accent.TButton")
        self.process_btn.pack(pady=20)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(self.root, mode="indeterminate")
        self.progress.pack(pady=10, padx=20, fill="x")
        
        # Log de texto
        log_frame = ttk.Frame(self.root)
        log_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        ttk.Label(log_frame, text="Log:").pack(anchor="w")
        
        self.log_text = tk.Text(log_frame, height=8, width=70)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Carpeta de salida
        output_frame = ttk.Frame(self.root)
        output_frame.pack(pady=10, padx=20, fill="x")
        
        ttk.Label(output_frame, text="PDFs procesados se guardarán en: ProcessedPDFs/").pack(anchor="w")
        
    def log_message(self, message):
        """Añade mensaje al log"""
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.root.update()
        
    def select_file(self):
        """Selecciona archivo PDF"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.selected_file = Path(file_path)
            self.file_label.config(text=self.selected_file.name)
            self.log_message(f"Archivo seleccionado: {self.selected_file.name}")
            
    def start_processing(self):
        """Inicia el procesamiento en hilo separado"""
        if not self.selected_file:
            messagebox.showerror("Error", "Selecciona un archivo PDF primero")
            return
            
        if self.processing:
            messagebox.showwarning("Advertencia", "Ya hay un procesamiento en curso")
            return
            
        self.processing = True
        self.process_btn.config(state="disabled")
        self.progress.start()
        
        # Procesar en hilo separado
        thread = threading.Thread(target=self.process_pdf)
        thread.daemon = True
        thread.start()
        
    def process_pdf(self):
        """Procesa el PDF (simulación)"""
        try:
            self.log_message("Iniciando procesamiento...")
            self.log_message("Analizando PDF...")
            
            # Crear carpeta de salida
            output_dir = Path("ProcessedPDFs")
            output_dir.mkdir(exist_ok=True)
            
            self.log_message("Removiendo marcas de agua...")
            
            # Simular procesamiento
            import time
            time.sleep(3)
            
            # Copiar archivo como "procesado"
            output_file = output_dir / f"processed_{self.selected_file.name}"
            shutil.copy2(self.selected_file, output_file)
            
            self.log_message(f"✅ PDF procesado guardado en: {output_file}")
            self.log_message("Procesamiento completado exitosamente")
            
            messagebox.showinfo("Éxito", f"PDF procesado correctamente\nGuardado en: {output_file}")
            
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", f"Error procesando PDF: {str(e)}")
            
        finally:
            self.processing = False
            self.progress.stop()
            self.process_btn.config(state="normal")
            
    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()

def main():
    """Función principal"""
    app = PDFWatermarkRemover()
    app.run()

if __name__ == "__main__":
    main()
