#!/usr/bin/env python3
"""
Compilador para PDF Watermark Remover GUI
Version limpia y simple
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_dependencies():
    """Verificar que PyInstaller este disponible"""
    try:
        import PyInstaller
        print("PyInstaller disponible")
        return True
    except ImportError:
        print("Instalando PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("PyInstaller instalado exitosamente")
            return True
        except subprocess.CalledProcessError:
            print("Error instalando PyInstaller")
            return False


def clean_previous_builds():
    """Limpiar compilaciones anteriores"""
    folders_to_clean = ['dist', 'build', '__pycache__']
    files_to_clean = ['*.spec']
    
    for folder in folders_to_clean:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"Limpiado: {folder}")
    
    for pattern in files_to_clean:
        for file in Path('.').glob(pattern):
            file.unlink()
            print(f"Eliminado: {file}")


def compile_app():
    """Compilar la aplicacion"""
    if not os.path.exists('gui_app.py'):
        print("ERROR: gui_app.py no encontrado")
        return False
    
    print("Iniciando compilacion...")
    
    # Comando de PyInstaller
    cmd = [
        sys.executable, '-m', 'pyinstaller',
        '--onefile',                    # Un solo archivo
        '--windowed',                   # Sin consola
        '--name=PDF_Watermark_Remover', # Nombre del ejecutable
        
        # Modulos ocultos importantes
        '--hidden-import=selenium',
        '--hidden-import=selenium.webdriver',
        '--hidden-import=selenium.webdriver.chrome',
        '--hidden-import=selenium.webdriver.chrome.options',
        '--hidden-import=selenium.webdriver.common.by',
        '--hidden-import=selenium.webdriver.support',
        '--hidden-import=selenium.webdriver.support.ui',
        '--hidden-import=selenium.webdriver.support.expected_conditions',
        '--hidden-import=selenium.common.exceptions',
        
        '--hidden-import=pdf2image',
        '--hidden-import=PIL',
        '--hidden-import=PIL.Image',
        
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=tkinter.messagebox',
        '--hidden-import=tkinter.scrolledtext',
        
        '--hidden-import=threading',
        '--hidden-import=queue',
        '--hidden-import=tempfile',
        '--hidden-import=pathlib',
        
        # Excluir modulos innecesarios
        '--exclude-module=matplotlib',
        '--exclude-module=numpy',
        '--exclude-module=pandas',
        '--exclude-module=scipy',
        '--exclude-module=jupyter',
        '--exclude-module=IPython',
        
        # Optimizaciones
        '--clean',
        '--noconfirm',
        
        # Archivo principal
        'gui_app.py'
    ]
    
    print("Ejecutando PyInstaller...")
    print("Esto puede tomar varios minutos...")
    
    try:
        # Ejecutar con salida en tiempo real
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )
        
        # Mostrar progreso
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line.strip():
                print(f"PyInstaller: {line.rstrip()}")
        
        return_code = process.poll()
        
        if return_code == 0:
            print("\nCompilacion exitosa!")
            return True
        else:
            print(f"\nError en compilacion (codigo: {return_code})")
            return False
            
    except Exception as e:
        print(f"Error ejecutando PyInstaller: {e}")
        return False


def create_distribution():
    """Crear carpeta de distribucion"""
    exe_path = Path('dist/PDF_Watermark_Remover.exe')
    
    if not exe_path.exists():
        print("Ejecutable no encontrado")
        return False
    
    # Crear carpeta de distribucion
    dist_folder = Path('PDF_Watermark_Remover_Portable')
    if dist_folder.exists():
        shutil.rmtree(dist_folder)
    
    dist_folder.mkdir()
    
    # Copiar ejecutable
    shutil.copy2(exe_path, dist_folder / 'PDF_Watermark_Remover.exe')
    
    # Crear carpetas de trabajo
    (dist_folder / 'InputPDFs').mkdir()
    (dist_folder / 'ProcessedPDFs').mkdir()
    
    # Crear README
    readme_content = """# PDF Watermark Remover v2.0

## Inicio Rapido
1. Ejecutar PDF_Watermark_Remover.exe
2. Seleccionar archivo PDF
3. Hacer clic en "INICIAR PROCESAMIENTO"
4. Esperar a que termine

## Requisitos
- Windows 10 o superior
- Conexion a Internet
- ChromeDriver instalado

## Instalacion de ChromeDriver
1. Ir a https://chromedriver.chromium.org/
2. Descargar version compatible con tu Chrome
3. Extraer chromedriver.exe
4. Colocar en una carpeta del PATH o en la misma carpeta

## Solucion de Problemas
- "ChromeDriver not found": Instalar ChromeDriver
- "Dependencias faltantes": Instalar Python y las librerias
- Error de conexion: Verificar Internet

## Contacto
Version: 2.0
"""
    
    with open(dist_folder / 'README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # Script de instalacion de ChromeDriver
    install_script = """@echo off
echo Instalador de ChromeDriver para PDF Watermark Remover
echo.
echo Ve a https://chromedriver.chromium.org/
echo Descarga la version compatible con tu Chrome
echo Extrae chromedriver.exe a esta carpeta
echo.
echo Presiona una tecla cuando hayas instalado ChromeDriver...
pause
"""
    
    with open(dist_folder / 'install_chromedriver.bat', 'w') as f:
        f.write(install_script)
    
    # Mostrar informacion
    size_mb = exe_path.stat().st_size / 1024 / 1024
    print(f"\nDistribucion creada:")
    print(f"Carpeta: {dist_folder}")
    print(f"Ejecutable: PDF_Watermark_Remover.exe ({size_mb:.1f} MB)")
    print(f"README: README.txt")
    
    return True


def main():
    """Funcion principal"""
    print("PDF Watermark Remover - Compilador")
    print("=" * 50)
    
    # Verificar dependencias
    if not check_dependencies():
        print("No se pudo configurar PyInstaller")
        return False
    
    # Limpiar compilaciones anteriores
    print("\nLimpiando compilaciones anteriores...")
    clean_previous_builds()
    
    # Compilar
    print("\nCompilando aplicacion...")
    if not compile_app():
        print("Error en la compilacion")
        return False
    
    # Crear distribucion
    print("\nCreando distribucion...")
    if not create_distribution():
        print("Error creando distribucion")
        return False
    
    print("\n" + "=" * 50)
    print("COMPILACION COMPLETADA!")
    print("\nArchivos generados:")
    print("- PDF_Watermark_Remover_Portable/")
    print("  - PDF_Watermark_Remover.exe")
    print("  - README.txt")
    print("  - install_chromedriver.bat")
    print("  - InputPDFs/ (carpeta de ejemplo)")
    print("  - ProcessedPDFs/ (carpeta de ejemplo)")
    
    print("\nProximos pasos:")
    print("1. Distribuir la carpeta PDF_Watermark_Remover_Portable")
    print("2. Los usuarios deben instalar ChromeDriver")
    print("3. Listo para usar!")
    
    return True


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCompilacion cancelada")
    except Exception as e:
        print(f"\nError: {e}")
    
    input("\nPresiona Enter para salir...")
