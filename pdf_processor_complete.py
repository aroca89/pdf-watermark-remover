#!/usr/bin/env python3
"""
Procesador completo de PDFs
Coordina: PDF → Imágenes → Procesamiento Web → PDF
"""

import os
import time
import tempfile
import shutil
from pathlib import Path

from pdf_to_images import PDFToImages
from image_watermark_remover import ImageWatermarkRemover
from images_to_pdf import ImagesToPDF


class PDFWatermarkProcessor:
    def __init__(self, output_folder, headless=True, dpi=300):
        """
        Inicializar procesador completo
        
        Args:
            output_folder (str): Carpeta para PDFs finales
            headless (bool): Modo sin ventana del navegador
            dpi (int): Resolución para conversiones
        """
        self.output_folder = os.path.abspath(output_folder)
        self.headless = headless
        self.dpi = dpi
        self.temp_folder = None
        
        # Crear carpeta de salida
        os.makedirs(self.output_folder, exist_ok=True)
        
        # Inicializar componentes
        self.pdf_converter = PDFToImages(dpi=dpi)
        self.pdf_creator = ImagesToPDF(dpi=dpi)
        self.watermark_remover = None
        
        print(f"Procesador inicializado")
        print(f"Carpeta de salida: {self.output_folder}")
        print(f"Modo headless: {headless}")
        print(f"DPI: {dpi}")
    
    def create_temp_folder(self):
        """Crear carpeta temporal para el procesamiento"""
        try:
            self.temp_folder = tempfile.mkdtemp(prefix="pdf_watermark_processing_")
            print(f"Carpeta temporal creada: {self.temp_folder}")
            return True
        except Exception as e:
            print(f"Error creando carpeta temporal: {e}")
            return False
    
    def cleanup_temp_folder(self):
        """Limpiar carpeta temporal"""
        if self.temp_folder and os.path.exists(self.temp_folder):
            try:
                shutil.rmtree(self.temp_folder)
                print(f"Carpeta temporal limpiada: {self.temp_folder}")
                self.temp_folder = None
            except Exception as e:
                print(f"Error limpiando carpeta temporal: {e}")
    
    def process_single_pdf(self, pdf_path, output_filename=None):
        """
        Procesar un PDF completo
        
        Args:
            pdf_path (str): Ruta del PDF original
            output_filename (str): Nombre del archivo de salida
        
        Returns:
            str: Ruta del PDF procesado o None si falló
        """
        if not os.path.exists(pdf_path):
            print(f"Error: PDF no encontrado - {pdf_path}")
            return None
        
        pdf_name = os.path.basename(pdf_path)
        print("="*80)
        print(f"PROCESANDO PDF COMPLETO: {pdf_name}")
        print("="*80)
        
        start_time = time.time()
        
        try:
            # Paso 1: Crear carpeta temporal
            print("\nPASO 1: Configuración")
            if not self.create_temp_folder():
                return None
            
            # Paso 2: Obtener información del PDF
            print("\nPASO 2: Análisis del PDF")
            pdf_info = self.pdf_converter.get_pdf_info(pdf_path)
            if pdf_info:
                print(f"Archivo: {pdf_info['filename']}")
                print(f"Tamaño: {pdf_info['size_mb']:.2f} MB")
                print(f"Páginas: {pdf_info.get('total_pages', 'N/A')}")
                print(f"Método de conversión: {pdf_info.get('conversion_method', 'N/A')}")
            
            # Paso 3: Convertir PDF a imágenes
            print("\nPASO 3: Conversión PDF → Imágenes")
            image_paths = self.pdf_converter.convert_pdf_to_images(pdf_path, self.temp_folder)
            
            if not image_paths:
                print("Error: No se pudieron generar imágenes del PDF")
                return None
            
            print(f"Generadas {len(image_paths)} imágenes")
            
            # Paso 4: Procesar imágenes en línea
            print("\nPASO 4: Procesamiento web de imágenes")
            self.watermark_remover = ImageWatermarkRemover(self.temp_folder, headless=self.headless)
            
            if not self.watermark_remover.setup_chrome():
                print("Error: No se pudo configurar el navegador")
                return None
            
            try:
                processed_images = self.watermark_remover.process_multiple_images(image_paths, delay_between=2)
                
                if not processed_images:
                    print("Error: No se procesaron imágenes exitosamente")
                    return None
                
                print(f"Procesadas {len(processed_images)} imágenes")
                
            finally:
                self.watermark_remover.close()
            
            # Paso 5: Convertir imágenes procesadas a PDF
            print("\nPASO 5: Conversión Imágenes → PDF")
            
            # Generar nombre del archivo final
            if not output_filename:
                base_name = Path(pdf_path).stem
                output_filename = f"NoWatermark_{base_name}.pdf"
            
            final_pdf_path = os.path.join(self.output_folder, output_filename)
            
            success = self.pdf_creator.convert_images_to_pdf(processed_images, final_pdf_path)
            
            if success:
                processing_time = time.time() - start_time
                print(f"\nPROCESO COMPLETADO EXITOSAMENTE!")
                print(f"PDF final: {output_filename}")
                print(f"Ubicación: {final_pdf_path}")
                print(f"Tiempo total: {processing_time:.1f} segundos")
                
                # Mostrar estadísticas finales
                if os.path.exists(final_pdf_path):
                    final_size = os.path.getsize(final_pdf_path)
                    original_size = os.path.getsize(pdf_path)
                    
                    print(f"\nEstadísticas:")
                    print(f"  Páginas procesadas: {len(processed_images)}")
                    print(f"  Tamaño original: {original_size:,} bytes")
                    print(f"  Tamaño final: {final_size:,} bytes")
                    print(f"  Ratio de tamaño: {final_size/original_size:.2%}")
                
                return final_pdf_path
            else:
                print("Error: No se pudo crear el PDF final")
                return None
                
        except Exception as e:
            print(f"Error general en procesamiento: {e}")
            return None
        
        finally:
            # Limpiar recursos
            if self.watermark_remover:
                self.watermark_remover.close()
            self.cleanup_temp_folder()
    
    def process_multiple_pdfs(self, input_folder, pattern="*.pdf"):
        """
        Procesar múltiples PDFs de una carpeta
        
        Args:
            input_folder (str): Carpeta con PDFs originales
            pattern (str): Patrón de archivos
        
        Returns:
            list: Resultados del procesamiento
        """
        if not os.path.exists(input_folder):
            print(f"Error: Carpeta no encontrada - {input_folder}")
            return []
        
        # Buscar archivos PDF
        pdf_files = list(Path(input_folder).glob(pattern))
        pdf_files.sort()
        
        if not pdf_files:
            print(f"No se encontraron archivos PDF en: {input_folder}")
            return []
        
        print("="*80)
        print(f"PROCESAMIENTO MASIVO: {len(pdf_files)} archivos")
        print("="*80)
        
        results = []
        successful = 0
        failed = 0
        total_start_time = time.time()
        
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\nArchivo {i}/{len(pdf_files)}: {pdf_file.name}")
            
            file_start_time = time.time()
            result_path = self.process_single_pdf(str(pdf_file))
            processing_time = time.time() - file_start_time
            
            # Registrar resultado
            result = {
                'index': i,
                'input_file': pdf_file.name,
                'input_path': str(pdf_file),
                'output_file': os.path.basename(result_path) if result_path else None,
                'output_path': result_path,
                'success': bool(result_path),
                'processing_time': processing_time
            }
            
            results.append(result)
            
            if result_path:
                successful += 1
                print(f"Archivo {i} completado en {processing_time:.1f}s")
            else:
                failed += 1
                print(f"Archivo {i} falló")
            
            # Pausa entre archivos (excepto el último)
            if i < len(pdf_files):
                pause_time = 5
                print(f"Pausa de {pause_time} segundos...")
                time.sleep(pause_time)
        
        # Resumen final
        total_time = time.time() - total_start_time
        
        print("\n" + "="*80)
        print("RESUMEN FINAL DEL PROCESAMIENTO MASIVO")
        print("="*80)
        print(f"Archivos procesados: {len(pdf_files)}")
        print(f"Exitosos: {successful}")
        print(f"Fallidos: {failed}")
        print(f"Tasa de éxito: {successful/len(pdf_files)*100:.1f}%")
        print(f"Tiempo total: {total_time:.1f}s ({total_time/60:.1f} min)")
        print(f"Tiempo promedio: {total_time/len(pdf_files):.1f}s por archivo")
        
        if successful > 0:
            print(f"\nArchivos exitosos guardados en: {self.output_folder}")
            for result in results:
                if result['success']:
                    print(f"  ✓ {result['input_file']} → {result['output_file']}")
        
        if failed > 0:
            print(f"\nArchivos fallidos:")
            for result in results:
                if not result['success']:
                    print(f"  ✗ {result['input_file']}")
        
        return results


# Funciones de utilidad
def process_pdf_file(pdf_path, output_folder, headless=True):
    """
    Función de conveniencia para procesar un PDF
    
    Args:
        pdf_path (str): Ruta del PDF
        output_folder (str): Carpeta de salida
        headless (bool): Modo sin ventana
    
    Returns:
        str: Ruta del PDF procesado
    """
    processor = PDFWatermarkProcessor(output_folder, headless=headless)
    return processor.process_single_pdf(pdf_path)


def process_pdf_folder(input_folder, output_folder, headless=True):
    """
    Función de conveniencia para procesar carpeta de PDFs
    
    Args:
        input_folder (str): Carpeta con PDFs
        output_folder (str): Carpeta de salida
        headless (bool): Modo sin ventana
    
    Returns:
        list: Resultados del procesamiento
    """
    processor = PDFWatermarkProcessor(output_folder, headless=headless)
    return processor.process_multiple_pdfs(input_folder)


if __name__ == "__main__":
    # Ejemplo de uso
    import sys
    
    if len(sys.argv) > 1:
        # Uso desde línea de comandos
        input_path = sys.argv[1]
        output_folder = sys.argv[2] if len(sys.argv) > 2 else "processed_pdfs"
        headless = "--headless" in sys.argv or "-h" in sys.argv
        
        if os.path.isfile(input_path):
            print(f"Procesando archivo: {input_path}")
            result = process_pdf_file(input_path, output_folder, headless)
            
            if result:
                print(f"PDF procesado: {result}")
            else:
                print("Error en el procesamiento")
        
        elif os.path.isdir(input_path):
            print(f"Procesando carpeta: {input_path}")
            results = process_pdf_folder(input_path, output_folder, headless)
            
            successful = len([r for r in results if r['success']])
            print(f"Procesados: {successful}/{len(results)} archivos")
        
        else:
            print(f"Ruta no válida: {input_path}")
    
    else:
        # Modo interactivo
        print("Procesador de PDFs - Eliminar Marcas de Agua")
        print("="*50)
        
        input_path = input("Ruta del PDF o carpeta: ").strip().strip('"')
        output_folder = input("Carpeta de salida [processed_pdfs]: ").strip() or "processed_pdfs"
        headless_input = input("Modo headless? (S/n): ").strip().lower()
        headless = headless_input != 'n'
        
        if os.path.isfile(input_path):
            result = process_pdf_file(input_path, output_folder, headless)
            if result:
                print(f"Éxito: {result}")
            else:
                print("Procesamiento falló")
        
        elif os.path.isdir(input_path):
            results = process_pdf_folder(input_path, output_folder, headless)
            successful = len([r for r in results if r['success']])
            print(f"Completado: {successful}/{len(results)} archivos")
        
        else:
            print("Ruta no válida")
