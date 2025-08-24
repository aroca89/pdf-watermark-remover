#!/usr/bin/env python3
"""
Módulo para eliminar marcas de agua de imágenes usando automatización web
Procesa imágenes individuales a través de watermarkremover.io
"""

import os
import time
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class ImageWatermarkRemover:
    def __init__(self, download_folder, headless=True):
        """
        Inicializar removedor de marcas de agua
        
        Args:
            download_folder (str): Carpeta donde descargar imágenes procesadas
            headless (bool): Ejecutar navegador sin ventana
        """
        self.download_folder = os.path.abspath(download_folder)
        self.headless = headless
        self.driver = None
        self.wait = None
        
        # Configuración
        self.site_url = "https://www.watermarkremover.io/es/image-watermark-remover"
        self.page_timeout = 30
        self.processing_timeout = 120
        self.download_timeout = 60
        
        # Crear carpeta de descarga
        os.makedirs(self.download_folder, exist_ok=True)
        print(f"Carpeta de descarga: {self.download_folder}")
    
    def setup_chrome(self):
        """Configurar y iniciar Chrome"""
        if not SELENIUM_AVAILABLE:
            print("Error: Selenium no está disponible")
            return False
        
        print("Configurando Chrome...")
        
        try:
            chrome_options = Options()
            
            # Configuración básica
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-gpu")
            
            # Configuración de descarga
            download_prefs = {
                "download.default_directory": self.download_folder,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
                "plugins.always_open_pdf_externally": True,
                "profile.default_content_settings.popups": 0
            }
            chrome_options.add_experimental_option("prefs", download_prefs)
            
            # Anti-detección
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Inicializar driver
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Script anti-detección
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            
            # Configurar timeouts
            self.driver.set_page_load_timeout(self.page_timeout)
            self.wait = WebDriverWait(self.driver, self.page_timeout)
            
            print("Chrome configurado correctamente")
            return True
            
        except Exception as e:
            print(f"Error configurando Chrome: {e}")
            return False
    
    def navigate_to_site(self):
        """Navegar al sitio de eliminación de marcas de agua"""
        try:
            print(f"Navegando a: {self.site_url}")
            self.driver.get(self.site_url)
            
            # Esperar que cargue la página
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)
            
            print("Página cargada correctamente")
            return True
            
        except Exception as e:
            print(f"Error navegando al sitio: {e}")
            return False
    
    def find_upload_input(self):
        """Encontrar el input de subida de archivos"""
        selectors = [
            "input[type='file']",
            "#uploadImage", 
            ".upload-input",
            "[accept*='image']",
            ".file-input",
            "[data-testid*='upload']"
        ]
        
        for selector in selectors:
            try:
                element = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                
                if element and element.is_enabled():
                    print(f"Input encontrado: {selector}")
                    return element
                    
            except TimeoutException:
                continue
            except Exception:
                continue
        
        print("No se encontró input de subida")
        return None
    
    def upload_image(self, image_path):
        """
        Subir imagen al sitio web
        
        Args:
            image_path (str): Ruta de la imagen a subir
        
        Returns:
            bool: True si la subida fue exitosa
        """
        if not os.path.exists(image_path):
            print(f"Imagen no encontrada: {image_path}")
            return False
        
        print(f"Subiendo imagen: {os.path.basename(image_path)}")
        
        try:
            # Encontrar input de subida
            file_input = self.find_upload_input()
            if not file_input:
                return False
            
            # Subir archivo
            abs_path = os.path.abspath(image_path)
            file_input.send_keys(abs_path)
            
            print("Imagen subida correctamente")
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"Error subiendo imagen: {e}")
            return False
    
    def handle_popups(self):
        """Manejar popups que puedan aparecer"""
        popup_selectors = [
            ".modal", ".popup", ".overlay", ".hb-modal-img",
            ".advertisement", "[role='dialog']", ".cookie-banner"
        ]
        
        close_selectors = [
            'button[aria-label*="close"]', 'button[aria-label*="Close"]',
            '.close-btn', '.modal-close', 'button.close',
            '[data-dismiss="modal"]', '.popup-close', '[title*="Close"]'
        ]
        
        try:
            for popup_selector in popup_selectors:
                try:
                    popup = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, popup_selector))
                    )
                    
                    if popup.is_displayed():
                        print(f"Popup detectado: {popup_selector}")
                        
                        # Intentar cerrar
                        for close_selector in close_selectors:
                            try:
                                close_button = self.driver.find_element(By.CSS_SELECTOR, close_selector)
                                if close_button.is_displayed() and close_button.is_enabled():
                                    close_button.click()
                                    print("Popup cerrado")
                                    time.sleep(1)
                                    return True
                            except:
                                continue
                        
                        # Si no se pudo cerrar, intentar ESC
                        try:
                            self.driver.find_element(By.TAG_NAME, 'body').send_keys('\x1b')
                            print("Popup cerrado con ESC")
                        except:
                            pass
                        
                        break
                        
                except TimeoutException:
                    continue
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"Error manejando popups: {e}")
        
        return False
    
    def wait_for_processing_completion(self):
        """Esperar a que se complete el procesamiento"""
        print("Esperando procesamiento...")
        
        # Selectores para indicadores de procesamiento
        processing_selectors = [
            ".loading", ".processing", ".spinner", ".progress",
            "[data-processing='true']", ".uploading"
        ]
        
        # Selectores para botones de descarga
        download_selectors = [
            'button[data-test-id*="download"]',
            'button[data-testid*="download"]',
            '.download-btn', '.btn-download',
            'button[download]', 'a[download]',
            'button:contains("Download")',
            'button:contains("Descargar")',
            '.download-button'
        ]
        
        try:
            # Esperar que desaparezcan indicadores de procesamiento
            for selector in processing_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        print(f"Esperando que termine: {selector}")
                        WebDriverWait(self.driver, self.processing_timeout).until(
                            EC.invisibility_of_element(element)
                        )
                except:
                    continue
            
            # Buscar botón de descarga
            for selector in download_selectors:
                try:
                    download_button = WebDriverWait(self.driver, self.processing_timeout).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    if download_button:
                        print(f"Botón de descarga encontrado: {selector}")
                        return download_button
                except:
                    continue
            
            print("No se encontró botón de descarga")
            return None
            
        except Exception as e:
            print(f"Error esperando procesamiento: {e}")
            return None
    
    def download_processed_image(self, download_button, original_filename):
        """
        Descargar imagen procesada
        
        Args:
            download_button: Elemento del botón de descarga
            original_filename (str): Nombre original de la imagen
        
        Returns:
            str: Ruta de la imagen descargada o None
        """
        print("Iniciando descarga...")
        
        try:
            # Archivos antes de descarga
            files_before = set(os.listdir(self.download_folder))
            
            # Hacer scroll al botón
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", 
                download_button
            )
            time.sleep(1)
            
            # Intentar click
            try:
                download_button.click()
                print("Click en descarga realizado")
            except Exception as e:
                print(f"Click normal falló: {e}")
                print("Intentando click con JavaScript...")
                self.driver.execute_script("arguments[0].click();", download_button)
            
            # Esperar descarga
            start_time = time.time()
            while time.time() - start_time < self.download_timeout:
                try:
                    current_files = set(os.listdir(self.download_folder))
                    new_files = current_files - files_before
                    
                    if new_files:
                        # Filtrar archivos completos
                        complete_files = [
                            f for f in new_files 
                            if not f.endswith(('.crdownload', '.tmp', '.part'))
                        ]
                        
                        if complete_files:
                            downloaded_file = complete_files[0]
                            downloaded_path = os.path.join(self.download_folder, downloaded_file)
                            
                            # Renombrar con prefijo
                            base_name = Path(original_filename).stem
                            original_ext = Path(original_filename).suffix
                            downloaded_ext = Path(downloaded_file).suffix or original_ext
                            
                            new_name = f"processed_{base_name}{downloaded_ext}"
                            new_path = os.path.join(self.download_folder, new_name)
                            
                            try:
                                os.rename(downloaded_path, new_path)
                                file_size = os.path.getsize(new_path)
                                print(f"Imagen descargada: {new_name} ({file_size:,} bytes)")
                                return new_path
                            except Exception as e:
                                print(f"Error renombrando: {e}")
                                return downloaded_path
                    
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error verificando descargas: {e}")
                    time.sleep(1)
            
            print("Timeout en descarga")
            return None
            
        except Exception as e:
            print(f"Error descargando: {e}")
            return None
    
    def process_single_image(self, image_path):
        """
        Procesar una sola imagen completa
        
        Args:
            image_path (str): Ruta de la imagen a procesar
        
        Returns:
            str: Ruta de la imagen procesada o None
        """
        print(f"Procesando imagen: {os.path.basename(image_path)}")
        
        try:
            # Navegar al sitio
            if not self.navigate_to_site():
                return None
            
            # Subir imagen
            if not self.upload_image(image_path):
                return None
            
            # Manejar popups
            self.handle_popups()
            
            # Esperar procesamiento
            download_button = self.wait_for_processing_completion()
            if not download_button:
                return None
            
            # Manejar popups antes de descarga
            self.handle_popups()
            
            # Descargar imagen procesada
            processed_image = self.download_processed_image(
                download_button, 
                os.path.basename(image_path)
            )
            
            return processed_image
            
        except Exception as e:
            print(f"Error procesando imagen: {e}")
            return None
    
    def process_multiple_images(self, image_paths, delay_between=3):
        """
        Procesar múltiples imágenes
        
        Args:
            image_paths (list): Lista de rutas de imágenes
            delay_between (int): Segundos entre procesamiento de imágenes
        
        Returns:
            list: Lista de imágenes procesadas
        """
        print(f"Procesando {len(image_paths)} imágenes...")
        
        processed_images = []
        
        for i, image_path in enumerate(image_paths, 1):
            print(f"\nImagen {i}/{len(image_paths)}: {os.path.basename(image_path)}")
            
            processed_image = self.process_single_image(image_path)
            
            if processed_image:
                processed_images.append(processed_image)
                print(f"Imagen {i} procesada exitosamente")
            else:
                print(f"Error procesando imagen {i}")
            
            # Pausa entre imágenes
            if i < len(image_paths) and delay_between > 0:
                print(f"Pausa de {delay_between} segundos...")
                time.sleep(delay_between)
        
        print(f"\nResumen: {len(processed_images)}/{len(image_paths)} imágenes procesadas")
        return processed_images
    
    def close(self):
        """Cerrar navegador"""
        if self.driver:
            try:
                self.driver.quit()
                print("Navegador cerrado")
            except Exception as e:
                print(f"Error cerrando navegador: {e}")
            finally:
                self.driver = None
                self.wait = None
    
    def __enter__(self):
        """Context manager entry"""
        if self.setup_chrome():
            return self
        else:
            raise Exception("No se pudo configurar Chrome")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Función de utilidad
def process_images_online(image_paths, download_folder, headless=True):
    """
    Función de conveniencia para procesar imágenes
    
    Args:
        image_paths (list): Lista de rutas de imágenes
        download_folder (str): Carpeta para descargas
        headless (bool): Ejecutar sin ventana
    
    Returns:
        list: Lista de imágenes procesadas
    """
    try:
        with ImageWatermarkRemover(download_folder, headless=headless) as remover:
            return remover.process_multiple_images(image_paths)
    except Exception as e:
        print(f"Error en procesamiento: {e}")
        return []


if __name__ == "__main__":
    # Ejemplo de uso
    import sys
    
    if len(sys.argv) > 1:
        image_file = sys.argv[1]
        download_dir = sys.argv[2] if len(sys.argv) > 2 else "processed_images"
    else:
        image_file = input("Ruta de la imagen: ").strip().strip('"')
        download_dir = input("Carpeta de descarga [processed_images]: ").strip() or "processed_images"
    
    if os.path.exists(image_file):
        print(f"Procesando: {image_file}")
        
        try:
            with ImageWatermarkRemover(download_dir, headless=False) as remover:
                result = remover.process_single_image(image_file)
                
                if result:
                    print(f"Imagen procesada: {result}")
                else:
                    print("Error en el procesamiento")
                    
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"Imagen no encontrada: {image_file}")
