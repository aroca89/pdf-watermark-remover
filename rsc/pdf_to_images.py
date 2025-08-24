#!/usr/bin/env python3
"""
Módulo para convertir PDFs a imágenes
Maneja la conversión de archivos PDF a imágenes individuales
"""

import os
import tempfile
import shutil
from pathlib import Path

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False


class PDFToImages:
    def __init__(self, dpi=300, image_format='PNG'):
        """
        Inicializar convertidor PDF a imágenes
        
        Args:
            dpi (int): Resolución de las imágenes (300 recomendado)
            image_format (str): Formato de imagen ('PNG', 'JPEG')
        """
        self.dpi = dpi
        self.image_format = image_format.upper()
        self.temp_folder = None
        
    def create_temp_folder(self, prefix="pdf_to_images_"):
        """Crear carpeta temporal para imágenes"""
        try:
            self.temp_folder = tempfile.mkdtemp(prefix=prefix)
            print(f"Carpeta temporal creada: {self.temp_folder}")
            return self.temp_folder
        except Exception as e:
            print(f"Error creando carpeta temporal: {e}")
            return None
    
    def cleanup_temp_folder(self):
        """Limpiar carpeta temporal"""
        if self.temp_folder and os.path.exists(self.temp_folder):
            try:
                shutil.rmtree(self.temp_folder)
                print(f"Carpeta temporal eliminada: {self.temp_folder}")
                self.temp_folder = None
            except Exception as e:
                print(f"Error eliminando carpeta temporal: {e}")
    
    def convert_pdf_to_images(self, pdf_path, output_folder=None):
        """
        Convertir PDF a imágenes individuales
        
        Args:
            pdf_path (str): Ruta del archivo PDF
            output_folder (str): Carpeta destino (usa temp si no se especifica)
        
        Returns:
            list: Lista de rutas de imágenes generadas
        """
        if not os.path.exists(pdf_path):
            print(f"Error: PDF no encontrado - {pdf_path}")
            return []
        
        # Usar carpeta temporal si no se especifica una
        if not output_folder:
            if not self.temp_folder:
                output_folder = self.create_temp_folder()
                if not output_folder:
                    return []
            else:
                output_folder = self.temp_folder
        
        print(f"Convirtiendo PDF a imágenes: {os.path.basename(pdf_path)}")
        print(f"DPI: {self.dpi}, Formato: {self.image_format}")
        
        try:
            if PDF2IMAGE_AVAILABLE:
                return self._convert_with_pdf2image(pdf_path, output_folder)
            else:
                return self._convert_mock(pdf_path, output_folder)
                
        except Exception as e:
            print(f"Error en conversión: {e}")
            return []
    
    def _convert_with_pdf2image(self, pdf_path, output_folder):
        """Convertir usando pdf2image (método real)"""
        try:
            # Convertir PDF a imágenes
            images = convert_from_path(
                pdf_path, 
                dpi=self.dpi, 
                fmt=self.image_format.lower()
            )
            
            image_paths = []
            pdf_name = Path(pdf_path).stem
            
            for i, image in enumerate(images, 1):
                image_filename = f"{pdf_name}_page_{i:03d}.{self.image_format.lower()}"
                image_path = os.path.join(output_folder, image_filename)
                
                # Configurar opciones de guardado
                save_kwargs = {'optimize': True}
                if self.image_format == 'PNG':
                    save_kwargs['compress_level'] = 6
                elif self.image_format == 'JPEG':
                    save_kwargs['quality'] = 95
                
                image.save(image_path, self.image_format, **save_kwargs)
                image_paths.append(image_path)
                print(f"Página {i:2d} -> {image_filename}")
            
            print(f"Conversión completada: {len(image_paths)} imágenes")
            return image_paths
            
        except Exception as e:
            print(f"Error con pdf2image: {e}")
            return []
    
    def _convert_mock(self, pdf_path, output_folder):
        """Convertir usando método mock (sin poppler)"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            print("Usando conversión mock (poppler no disponible)")
            
            # Intentar determinar número de páginas
            try:
                with open(pdf_path, 'rb') as f:
                    content = f.read()
                    page_count = content.count(b'/Type /Page')
                    if page_count == 0:
                        page_count = 1
            except:
                page_count = 1
            
            image_paths = []
            pdf_name = Path(pdf_path).stem
            
            # Crear imágenes mock
            for page_num in range(min(page_count, 20)):  # Máximo 20 páginas
                img = Image.new('RGB', (1200, 1600), color='white')
                draw = ImageDraw.Draw(img)
                
                # Marco
                draw.rectangle([20, 20, 1180, 1580], outline='#cccccc', width=2)
                
                # Contenido
                try:
                    font = ImageFont.load_default()
                except:
                    font = None
                
                # Información
                title = f"PDF: {os.path.basename(pdf_path)}"
                page_info = f"Página {page_num + 1} de {page_count}"
                warning = "Imagen mock - Instalar poppler para conversión real"
                
                draw.text((50, 50), title, fill='black', font=font)
                draw.text((50, 100), page_info, fill='#666666', font=font)
                draw.text((50, 150), warning, fill='red', font=font)
                
                # Contenido simulado
                for i in range(15):
                    y = 250 + i * 40
                    draw.rectangle([50, y, 1150, y + 25], fill='#f0f0f0')
                    draw.text((60, y + 5), f"Línea de contenido simulado {i+1}", 
                             fill='#333333', font=font)
                
                # Guardar imagen
                image_filename = f"{pdf_name}_page_{page_num+1:03d}.png"
                image_path = os.path.join(output_folder, image_filename)
                img.save(image_path, 'PNG')
                image_paths.append(image_path)
                print(f"Página mock {page_num+1:2d} -> {image_filename}")
            
            print(f"Conversión mock completada: {len(image_paths)} imágenes")
            return image_paths
            
        except Exception as e:
            print(f"Error en conversión mock: {e}")
            return []
    
    def get_pdf_info(self, pdf_path):
        """
        Obtener información básica del PDF
        
        Args:
            pdf_path (str): Ruta del PDF
        
        Returns:
            dict: Información del PDF
        """
        if not os.path.exists(pdf_path):
            return None
        
        info = {
            'filename': os.path.basename(pdf_path),
            'file_size': os.path.getsize(pdf_path),
            'size_mb': os.path.getsize(pdf_path) / 1024 / 1024
        }
        
        if PDF2IMAGE_AVAILABLE:
            try:
                # Obtener info real del PDF
                test_images = convert_from_path(pdf_path, dpi=72, last_page=1)
                if test_images:
                    all_images = convert_from_path(pdf_path, dpi=72)
                    info.update({
                        'total_pages': len(all_images),
                        'first_page_size': test_images[0].size,
                        'conversion_method': 'real'
                    })
            except Exception as e:
                print(f"Error obteniendo info real: {e}")
                info['conversion_method'] = 'mock'
        else:
            # Estimación básica
            try:
                with open(pdf_path, 'rb') as f:
                    content = f.read()
                    page_count = content.count(b'/Type /Page')
                    info.update({
                        'total_pages': max(1, page_count),
                        'conversion_method': 'mock'
                    })
            except:
                info.update({
                    'total_pages': 1,
                    'conversion_method': 'mock'
                })
        
        return info


# Funciones de utilidad
def convert_pdf_to_images(pdf_path, output_folder=None, dpi=300):
    """
    Función de conveniencia para convertir PDF a imágenes
    
    Args:
        pdf_path (str): Ruta del PDF
        output_folder (str): Carpeta destino
        dpi (int): Resolución
    
    Returns:
        list: Lista de rutas de imágenes
    """
    converter = PDFToImages(dpi=dpi)
    try:
        return converter.convert_pdf_to_images(pdf_path, output_folder)
    finally:
        if not output_folder:  # Solo limpiar si usamos carpeta temporal
            converter.cleanup_temp_folder()


def get_pdf_info(pdf_path):
    """
    Función de conveniencia para obtener info del PDF
    
    Args:
        pdf_path (str): Ruta del PDF
    
    Returns:
        dict: Información del PDF
    """
    converter = PDFToImages()
    return converter.get_pdf_info(pdf_path)


if __name__ == "__main__":
    # Ejemplo de uso
    import sys
    
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
    else:
        pdf_file = input("Ingresa la ruta del PDF: ").strip().strip('"')
    
    if os.path.exists(pdf_file):
        print(f"\nAnalizando: {pdf_file}")
        
        # Mostrar info
        info = get_pdf_info(pdf_file)
        if info:
            print(f"Archivo: {info['filename']}")
            print(f"Tamaño: {info['size_mb']:.2f} MB")
            print(f"Páginas: {info.get('total_pages', 'N/A')}")
            print(f"Método: {info.get('conversion_method', 'N/A')}")
        
        # Convertir
        print(f"\nConvirtiendo...")
        images = convert_pdf_to_images(pdf_file, dpi=200)
        
        if images:
            print(f"Conversión exitosa: {len(images)} imágenes")
            print(f"Primera imagen: {images[0]}")
        else:
            print("Error en la conversión")
    else:
        print(f"Archivo no encontrado: {pdf_file}")
