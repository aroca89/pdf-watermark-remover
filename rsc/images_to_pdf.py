#!/usr/bin/env python3
"""
Módulo para convertir imágenes a PDF
Combina múltiples imágenes en un archivo PDF único
"""

import os
from pathlib import Path

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class ImagesToPDF:
    def __init__(self, dpi=300, quality=95):
        """
        Inicializar convertidor de imágenes a PDF
        
        Args:
            dpi (int): Resolución del PDF resultante
            quality (int): Calidad de compresión (1-100)
        """
        self.dpi = dpi
        self.quality = quality
        
    def convert_images_to_pdf(self, image_paths, output_pdf_path):
        """
        Convertir lista de imágenes a PDF
        
        Args:
            image_paths (list): Lista de rutas de imágenes
            output_pdf_path (str): Ruta del PDF de salida
        
        Returns:
            bool: True si la conversión fue exitosa
        """
        if not PIL_AVAILABLE:
            print("Error: PIL/Pillow no está disponible")
            return False
        
        if not image_paths:
            print("Error: No hay imágenes para convertir")
            return False
        
        print(f"Convirtiendo {len(image_paths)} imágenes a PDF...")
        print(f"PDF destino: {os.path.basename(output_pdf_path)}")
        
        try:
            # Ordenar imágenes por nombre para mantener orden correcto
            sorted_paths = sorted(image_paths, key=lambda x: os.path.basename(x))
            
            # Verificar que todas las imágenes existan
            valid_paths = []
            for img_path in sorted_paths:
                if os.path.exists(img_path):
                    valid_paths.append(img_path)
                else:
                    print(f"Advertencia: Imagen no encontrada - {os.path.basename(img_path)}")
            
            if not valid_paths:
                print("Error: No se encontraron imágenes válidas")
                return False
            
            # Procesar imágenes
            processed_images = []
            for i, img_path in enumerate(valid_paths, 1):
                try:
                    img = Image.open(img_path)
                    
                    # Convertir a RGB si es necesario (requerido para PDF)
                    if img.mode != 'RGB':
                        print(f"Convirtiendo imagen {i} de {img.mode} a RGB")
                        img = img.convert('RGB')
                    
                    processed_images.append(img)
                    print(f"Procesada {i:2d}/{len(valid_paths)}: {os.path.basename(img_path)} ({img.size[0]}x{img.size[1]})")
                    
                except Exception as e:
                    print(f"Error procesando {os.path.basename(img_path)}: {e}")
                    continue
            
            if not processed_images:
                print("Error: No se pudieron procesar las imágenes")
                return False
            
            # Crear directorio de salida si no existe
            output_dir = os.path.dirname(output_pdf_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                print(f"Directorio creado: {output_dir}")
            
            # Guardar como PDF
            print("Generando PDF...")
            
            first_image = processed_images[0]
            other_images = processed_images[1:] if len(processed_images) > 1 else []
            
            save_params = {
                "save_all": True,
                "append_images": other_images,
                "optimize": True,
                "resolution": float(self.dpi)
            }
            
            # Aplicar calidad solo para JPEG
            if self.quality < 100:
                save_params["quality"] = self.quality
            
            first_image.save(output_pdf_path, "PDF", **save_params)
            
            # Verificar que el archivo se creó
            if os.path.exists(output_pdf_path):
                file_size = os.path.getsize(output_pdf_path)
                print(f"PDF creado exitosamente:")
                print(f"  Archivo: {os.path.basename(output_pdf_path)}")
                print(f"  Tamaño: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
                print(f"  Páginas: {len(processed_images)}")
                print(f"  Resolución: {self.dpi} DPI")
                return True
            else:
                print("Error: El archivo PDF no se creó")
                return False
                
        except Exception as e:
            print(f"Error convirtiendo imágenes a PDF: {e}")
            return False
    
    def merge_pdfs_from_images(self, image_folder, output_pdf_path, image_extensions=None):
        """
        Crear PDF desde todas las imágenes de una carpeta
        
        Args:
            image_folder (str): Carpeta con imágenes
            output_pdf_path (str): Ruta del PDF de salida
            image_extensions (list): Extensiones válidas
        
        Returns:
            bool: True si fue exitoso
        """
        if image_extensions is None:
            image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif']
        
        if not os.path.exists(image_folder):
            print(f"Error: Carpeta no encontrada - {image_folder}")
            return False
        
        print(f"Buscando imágenes en: {image_folder}")
        
        # Buscar todas las imágenes
        image_paths = []
        for ext in image_extensions:
            pattern = f"*{ext}"
            found = list(Path(image_folder).glob(pattern))
            found.extend(list(Path(image_folder).glob(pattern.upper())))
            image_paths.extend([str(p) for p in found])
        
        if not image_paths:
            print(f"No se encontraron imágenes con extensiones: {image_extensions}")
            return False
        
        print(f"Encontradas {len(image_paths)} imágenes")
        
        return self.convert_images_to_pdf(image_paths, output_pdf_path)
    
    def get_image_info(self, image_path):
        """
        Obtener información de una imagen
        
        Args:
            image_path (str): Ruta de la imagen
        
        Returns:
            dict: Información de la imagen
        """
        if not PIL_AVAILABLE or not os.path.exists(image_path):
            return None
        
        try:
            with Image.open(image_path) as img:
                info = {
                    'filename': os.path.basename(image_path),
                    'size': img.size,
                    'width': img.size[0],
                    'height': img.size[1],
                    'mode': img.mode,
                    'format': img.format,
                    'file_size': os.path.getsize(image_path),
                    'file_size_mb': os.path.getsize(image_path) / 1024 / 1024
                }
                
                # Información adicional si está disponible
                if hasattr(img, 'info'):
                    dpi = img.info.get('dpi', (None, None))
                    if dpi[0]:
                        info['dpi'] = dpi
                
                return info
        except Exception as e:
            print(f"Error obteniendo info de {image_path}: {e}")
            return None
    
    def validate_images(self, image_paths):
        """
        Validar lista de imágenes antes de conversión
        
        Args:
            image_paths (list): Lista de rutas de imágenes
        
        Returns:
            dict: Resultado de validación
        """
        result = {
            'valid_images': [],
            'invalid_images': [],
            'missing_images': [],
            'total_size_mb': 0,
            'different_sizes': [],
            'recommendations': []
        }
        
        if not PIL_AVAILABLE:
            result['recommendations'].append("Instalar Pillow: pip install Pillow")
            return result
        
        sizes_found = {}
        
        for img_path in image_paths:
            if not os.path.exists(img_path):
                result['missing_images'].append(img_path)
                continue
            
            info = self.get_image_info(img_path)
            if info:
                result['valid_images'].append(img_path)
                result['total_size_mb'] += info['file_size_mb']
                
                # Rastrear diferentes tamaños
                size_key = f"{info['width']}x{info['height']}"
                if size_key not in sizes_found:
                    sizes_found[size_key] = []
                sizes_found[size_key].append(img_path)
            else:
                result['invalid_images'].append(img_path)
        
        # Detectar diferentes tamaños
        if len(sizes_found) > 1:
            result['different_sizes'] = list(sizes_found.keys())
            result['recommendations'].append(
                f"Se detectaron {len(sizes_found)} tamaños diferentes de imagen. "
                "Considera redimensionar para consistencia."
            )
        
        # Recomendaciones adicionales
        if result['total_size_mb'] > 50:
            result['recommendations'].append(
                f"Tamaño total: {result['total_size_mb']:.1f} MB. "
                "Considera optimizar las imágenes para un PDF más pequeño."
            )
        
        if len(result['valid_images']) > 100:
            result['recommendations'].append(
                f"{len(result['valid_images'])} páginas. "
                "PDFs muy grandes pueden ser lentos de procesar."
            )
        
        return result


# Funciones de utilidad
def convert_images_to_pdf(image_paths, output_pdf_path, dpi=300, quality=95):
    """
    Función de conveniencia para convertir imágenes a PDF
    
    Args:
        image_paths (list): Lista de rutas de imágenes
        output_pdf_path (str): Ruta del PDF de salida
        dpi (int): Resolución
        quality (int): Calidad de compresión
    
    Returns:
        bool: True si fue exitoso
    """
    converter = ImagesToPDF(dpi=dpi, quality=quality)
    return converter.convert_images_to_pdf(image_paths, output_pdf_path)


def create_pdf_from_folder(image_folder, output_pdf_path, dpi=300):
    """
    Función de conveniencia para crear PDF desde carpeta de imágenes
    
    Args:
        image_folder (str): Carpeta con imágenes
        output_pdf_path (str): Ruta del PDF de salida
        dpi (int): Resolución
    
    Returns:
        bool: True si fue exitoso
    """
    converter = ImagesToPDF(dpi=dpi)
    return converter.merge_pdfs_from_images(image_folder, output_pdf_path)


def validate_images_for_pdf(image_paths):
    """
    Función de conveniencia para validar imágenes
    
    Args:
        image_paths (list): Lista de rutas de imágenes
    
    Returns:
        dict: Resultado de validación
    """
    converter = ImagesToPDF()
    return converter.validate_images(image_paths)


if __name__ == "__main__":
    # Ejemplo de uso
    import sys
    
    print("Convertidor de Imágenes a PDF")
    print("=" * 40)
    
    if len(sys.argv) > 2:
        # Uso desde línea de comandos
        if sys.argv[1] == "--folder":
            folder_path = sys.argv[2]
            pdf_path = sys.argv[3] if len(sys.argv) > 3 else "output.pdf"
            
            if create_pdf_from_folder(folder_path, pdf_path):
                print(f"PDF creado: {pdf_path}")
            else:
                print("Error creando PDF desde carpeta")
        
        else:
            # Lista de archivos
            image_files = sys.argv[1:-1]
            pdf_path = sys.argv[-1]
            
            if convert_images_to_pdf(image_files, pdf_path):
                print(f"PDF creado: {pdf_path}")
            else:
                print("Error creando PDF")
    
    else:
        # Modo interactivo
        print("Opciones:")
        print("1. Convertir imágenes específicas")
        print("2. Convertir toda una carpeta")
        
        choice = input("\nSelecciona opción (1/2): ").strip()
        
        if choice == "1":
            images_input = input("Rutas de imágenes (separadas por comas): ").strip()
            if images_input:
                image_paths = [p.strip().strip('"') for p in images_input.split(',')]
                pdf_path = input("Nombre del PDF de salida: ").strip() or "output.pdf"
                
                # Validar primero
                validation = validate_images_for_pdf(image_paths)
                
                print(f"\nValidación:")
                print(f"  Válidas: {len(validation['valid_images'])}")
                print(f"  Inválidas: {len(validation['invalid_images'])}")
                print(f"  Faltantes: {len(validation['missing_images'])}")
                
                if validation['recommendations']:
                    print("  Recomendaciones:")
                    for rec in validation['recommendations']:
                        print(f"    - {rec}")
                
                if validation['valid_images']:
                    proceed = input(f"\n¿Continuar con {len(validation['valid_images'])} imágenes? (s/N): ")
                    if proceed.lower() == 's':
                        if convert_images_to_pdf(validation['valid_images'], pdf_path):
                            print(f"PDF creado: {pdf_path}")
                        else:
                            print("Error en la conversión")
        
        elif choice == "2":
            folder_path = input("Ruta de la carpeta con imágenes: ").strip().strip('"')
            pdf_path = input("Nombre del PDF de salida: ").strip() or "folder_output.pdf"
            
            if create_pdf_from_folder(folder_path, pdf_path):
                print(f"PDF creado: {pdf_path}")
            else:
                print("Error creando PDF desde carpeta")
        
        else:
            print("Opción inválida")
