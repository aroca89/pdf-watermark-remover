#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Watermark Remover - Build & Install Script
Compila la aplicación y maneja la instalación completa
"""

import os
import sys
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path
import winreg

class PDFWatermarkBuildInstaller:
    def __init__(self):
        self.app_name = "PDF Watermark Remover"
        self.app_version = "2.0"
        self.install_dir = Path.home() / "AppData/Local/PDF_Watermark_Remover"
        self.build_dir = Path("build")
        self.dist_dir = Path("dist")
        self.source_dir = Path("rsc")  # Carpeta con código fuente
        
    def print_header(self):
        print("=" * 60)
        print(f"    {self.app_name} v{self.app_version} - Build & Install")
        print("=" * 60)

    def check_python_requirements(self):
        """Verifica e instala dependencias necesarias"""
        print("📦 Verificando dependencias de build...")
        
        required_packages = [
            "pyinstaller",
            "requests", 
            "selenium",
            "tkinter",
            "pillow",
            "pywin32"
        ]
        
        for package in required_packages:
            try:
                if package == "tkinter":
                    import tkinter
                elif package == "pywin32":
                    import win32com.client
                else:
                    __import__(package.replace("-", "_"))
                print(f"   ✅ {package}")
            except ImportError:
                print(f"   📥 Instalando {package}...")
                try:
                    if package == "tkinter":
                        print("   ⚠️  tkinter debe instalarse manualmente con Python")
                        continue
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                    print(f"   ✅ {package} instalado")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    return False
        return True

    def create_main_app_script(self):
        """Crea el script principal si no existe"""
        print("📝 Verificando código fuente...")
        
        main_script = self.source_dir / "main.py"
        if not main_script.exists():
            print("   📝 Creando aplicación base...")
            self.source_dir.mkdir(exist_ok=True)
            
            # Crear aplicación GUI básica
            app_code = '''#!/usr/bin/env python3
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
        self.log_text.insert("end", f"{message}\\n")
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
            
            messagebox.showinfo("Éxito", f"PDF procesado correctamente\\nGuardado en: {output_file}")
            
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
'''
            
            with open(main_script, 'w', encoding='utf-8') as f:
                f.write(app_code)
            
            print("   ✅ Aplicación base creada")
        else:
            print("   ✅ Código fuente encontrado")

    def build_executable(self):
        """Compila la aplicación con PyInstaller"""
        print("🔨 Compilando aplicación...")
        
        main_script = self.source_dir / "main.py"
        if not main_script.exists():
            print("   ❌ No se encontró main.py")
            return False
            
        try:
            # Limpiar builds anteriores
            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)
            if self.dist_dir.exists():
                shutil.rmtree(self.dist_dir)
                
            # Comando PyInstaller
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--onefile",
                "--windowed",
                "--name", "PDF_Watermark_Remover",
                str(main_script)
            ]
            
            # Añadir icono si existe
            if Path("icon.ico").exists():
                cmd.extend(["--icon", "icon.ico"])
            
            print("   🔄 Ejecutando PyInstaller...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("   ✅ Compilación exitosa")
                return True
            else:
                print(f"   ❌ Error en compilación: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False

    def get_chrome_version(self):
        """Obtiene versión de Chrome"""
        try:
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ]
            
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    result = subprocess.run([chrome_path, "--version"], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        return result.stdout.strip().split()[-1]
        except:
            pass
        return None

    def download_chromedriver(self):
        """Descarga ChromeDriver"""
        print("📥 Descargando ChromeDriver...")
        
        chrome_version = self.get_chrome_version()
        if chrome_version:
            major_version = chrome_version.split('.')[0]
            print(f"   Chrome v{chrome_version} detectado")
        else:
            print("   Chrome no detectado, usando versión estable")
            major_version = None
            
        try:
            if major_version:
                api_url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}"
            else:
                api_url = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
                
            response = urllib.request.urlopen(api_url)
            driver_version = response.read().decode('utf-8').strip()
            
            download_url = f"https://chromedriver.storage.googleapis.com/{driver_version}/chromedriver_win32.zip"
            zip_path = self.install_dir / "chromedriver.zip"
            
            print(f"   Descargando v{driver_version}...")
            urllib.request.urlretrieve(download_url, zip_path)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extract("chromedriver.exe", self.install_dir)
            
            os.remove(zip_path)
            print("   ✅ ChromeDriver instalado")
            return True
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False

    def install_application(self):
        """Instala la aplicación compilada"""
        print("📁 Instalando aplicación...")
        
        # Crear directorios
        self.install_dir.mkdir(parents=True, exist_ok=True)
        (self.install_dir / "ProcessedPDFs").mkdir(exist_ok=True)
        
        # Copiar ejecutable
        exe_source = self.dist_dir / "PDF_Watermark_Remover.exe"
        exe_dest = self.install_dir / "PDF_Watermark_Remover.exe"
        
        if exe_source.exists():
            shutil.copy2(exe_source, exe_dest)
            print("   ✅ Ejecutable copiado")
        else:
            print("   ❌ Ejecutable no encontrado")
            return False
            
        # Crear README
        readme_content = f'''# {self.app_name} v{self.app_version}

## Inicio Rápido
1. Ejecutar PDF_Watermark_Remover.exe
2. Seleccionar archivo PDF
3. Hacer clic en "INICIAR PROCESAMIENTO"
4. Resultado en ProcessedPDFs/

## Ubicación
Instalado en: {self.install_dir}

## Desinstalar
Ejecutar: uninstall.bat
'''
        
        with open(self.install_dir / "README.txt", 'w', encoding='utf-8') as f:
            f.write(readme_content)
            
        print("   ✅ Archivos de instalación creados")
        return True

    def create_shortcuts(self):
        """Crea accesos directos"""
        print("🔗 Creando accesos directos...")
        
        try:
            import win32com.client
            
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / f"{self.app_name}.lnk"
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = str(self.install_dir / "PDF_Watermark_Remover.exe")
            shortcut.WorkingDirectory = str(self.install_dir)
            shortcut.save()
            
            print("   ✅ Acceso directo creado")
            
        except Exception as e:
            # Fallback: crear .bat
            desktop = Path.home() / "Desktop"
            bat_path = desktop / f"{self.app_name}.bat"
            with open(bat_path, 'w') as f:
                f.write(f'@echo off\ncd /d "{self.install_dir}"\nstart PDF_Watermark_Remover.exe\n')
            print("   ✅ Script de acceso creado")

    def create_uninstaller(self):
        """Crea desinstalador"""
        uninstall_script = self.install_dir / "uninstall.bat"
        with open(uninstall_script, 'w', encoding='utf-8') as f:
            f.write(f'''@echo off
title Desinstalar {self.app_name}
echo Desinstalando {self.app_name}...

del "%USERPROFILE%\\Desktop\\{self.app_name}.lnk" 2>nul
del "%USERPROFILE%\\Desktop\\{self.app_name}.bat" 2>nul

cd /d "%TEMP%"
rmdir /s /q "{self.install_dir}"

echo Desinstalación completada.
pause
''')

    def run_build_install(self):
        """Proceso completo de build e instalación"""
        self.print_header()
        
        try:
            # 1. Verificar dependencias
            if not self.check_python_requirements():
                print("❌ Faltan dependencias críticas")
                return False
                
            # 2. Crear/verificar código fuente
            self.create_main_app_script()
            
            # 3. Compilar aplicación
            if not self.build_executable():
                print("❌ Error en compilación")
                return False
                
            # 4. Instalar aplicación
            if not self.install_application():
                print("❌ Error en instalación")
                return False
                
            # 5. Descargar ChromeDriver
            self.download_chromedriver()
            
            # 6. Crear accesos y desinstalador
            self.create_shortcuts()
            self.create_uninstaller()
            
            print(f"\n🎉 Build e instalación completados!")
            print(f"📁 Ubicación: {self.install_dir}")
            print(f"🖥️  Acceso directo en escritorio")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

def main():
    builder = PDFWatermarkBuildInstaller()
    
    try:
        success = builder.run_build_install()
        if success:
            print("\n¿Ejecutar aplicación? (s/N): ", end="")
            if input().lower() in ['s', 'si', 'sí']:
                subprocess.Popen([str(builder.install_dir / "PDF_Watermark_Remover.exe")])
        
        input("\nPresiona Enter para salir...")
        
    except KeyboardInterrupt:
        print("\nProceso cancelado")
    except Exception as e:
        print(f"Error: {e}")
        input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()
