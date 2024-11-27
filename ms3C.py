from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options  # Importar el módulo de opciones de Chrome
from termcolor import colored

import os
import re
import time
import config

DRIVER = webdriver  # Esta variable contiene el driver que se está usando en el momento
MATERIAS = {}  # Este diccionario contiene las materias encontradas
ancho_materia = 35  # Ajusta según el texto más largo
ancho_link = 70  # Ajusta según la longitud máxima del link


# Esta función devuelve el driver de un navegador ya configurado
def inicializarDriver(path=""):
    global DRIVER

    # Opciones de Chrome
    options = Options()

    # Configura el navegador para ser headless (Que se ejecute en consola)
    options.add_argument("--headless")

    # Desactivar el audio del navegador
    options.add_experimental_option("prefs", {
        "media.volume_scale": "0.0"
    })

    # Configurar las preferencias de descarga si se pasó un path
    options.add_experimental_option('prefs', {
        "download.default_directory": path,  # Cambia el directorio predeterminado para las descargas
        "download.prompt_for_download": False,  # Para descargar automáticamente el archivo
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True  # No abrir PDFs dentro del navegador
    })

    #Argumento que limpia de la consola un error de HotJar
    userAgent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.56 Safari/537.36"
    options.add_argument(f'user-agent={userAgent}')

    #Argumentos para mantener limpia la consola
    options.add_argument("--silent")
    options.add_argument("--log-level=3")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # Inicializar el controlador de Chrome con las configuraciones
    DRIVER = webdriver.Chrome(options=options)
    time.sleep(3)


# El resto del código sigue igual, ya que la funcionalidad no cambia, solo el driver.
# Completa el login de Miel
def iniciarSesion():
    global DRIVER

    # Usuario
    complTxtBox(By.CSS_SELECTOR, '#usuario', config.CREDENCIAL_USER)

    # Contraseña
    complTxtBox(By.CSS_SELECTOR, '#clave', config.CREDENCIAL_PASSWORD)

    # Entrar
    clicBoton(By.CSS_SELECTOR, '#btnLogin')

# Busca una texbox y rellena con información
def complTxtBox(tipoSelector, selector, info):
    global DRIVER

    elemento = DRIVER.find_element(tipoSelector, selector)
    elemento.click()
    elemento.send_keys(info)

# Busca un botón y clickea encima
def clicBoton(tipoSelector, selector):
    global DRIVER

    elemento = DRIVER.find_element(tipoSelector, selector)
    elemento.click()

# Busca las materias de miel y las agrega a materias
def cargarMaterias():
    global DRIVER
    global MATERIAS

    # Me aseguro de estar en la página objetivo
    DRIVER.get(config.PAGINA_OBJETIVO)

    # Inicio sesión
    iniciarSesion()

    # Recargo
    time.sleep(5)
    DRIVER.get(config.PAGINA_OBJETIVO)

    # Busco el contenedor de los cursos
    contenedores = DRIVER.find_elements(By.CSS_SELECTOR, 'div.curso-sortable > div')

    # Por cada contenedor, extraigo el nombre y su link
    for contenedor in contenedores:
        nombre = contenedor.find_element(By.CSS_SELECTOR, 'div.w3-col.w3-mobile.w3-padding.materia-descripcion > div.w3-slarge.materia-titulo').text
        link = contenedor.find_element(By.CSS_SELECTOR, 'div.w3-rest.w3-mobile.materia-herramientas > div > a').get_attribute('href')
        MATERIAS[nombre] = link

# Screpea todas las materias
def scrapMaterias():
    global DRIVER
    global MATERIAS

    # Por cada materia, scrapeo
    for materia in MATERIAS:
        scrapMateria(materia, MATERIAS[materia])


# Función para guardar los enlaces en un archivo
def guardarEnArchivo(path, filename, lista):
    with open(f"{path}/{filename}", 'a') as archivo:
        for elemento in lista:
            archivo.write(elemento + "\n")
            print(f'Grabado link: {colored(elemento, "blue")}')


# Función principal de scraping
def scrapMateria(nombreMateria, link):
    global DRIVER
    global ancho_link
    global ancho_materia

    try:
        # Me muevo al directorio correspondiente
        path = os.path.abspath(f".\\{nombreMateria}")
        os.makedirs(path, exist_ok=True)  # Asegurar que el directorio exista

        # Inicializo el driver para cada materia
        inicializarDriver(path)
        DRIVER.get(config.PAGINA_OBJETIVO)

        # Iniciar sesión
        iniciarSesion()

        DRIVER.get(config.PAGINA_OBJETIVO)  # Ir a la página de la materia

        # Listas para los enlaces
        listaOtros = []
        listaDescarga = []
        DRIVER.get(link)  # Cargar el enlace de la materia

        # Buscar los elementos que contienen los enlaces
        contenedoresHead = DRIVER.find_elements(By.CSS_SELECTOR, 'td.w3-center > a')

        # Iterar sobre los enlaces encontrados
        for head in contenedoresHead:
            enlace = head.get_attribute('href')

            # Clasificar los enlaces
            if re.search(r'\.pdf$|descargarElemento', enlace):
                listaDescarga.append(enlace)  # Enlace de descarga
            elif enlace != "javascript:void(0);":
                listaOtros.append(enlace)  # Enlace de otro tipo

        # Mostrar título y línea divisoria
        print("-" * (ancho_materia + ancho_link))  # Línea divisoria
        print(f"{colored(nombreMateria, 'red', attrs=['bold', 'underline'])}:")

        # Escribir los enlaces de descarga en 'descargas_pdf.txt'
        print(f"\n\n{colored('Descarga archivos y grabado de descargas.txt:', 'blue', attrs=['bold'])}")
        enlaces_pdf = [enlace for enlace in listaDescarga if re.search(r'\.pdf', enlace, re.IGNORECASE)]
        guardarEnArchivo(nombreMateria, 'descargas_pdf.txt', enlaces_pdf)

        # Filtrar los enlaces que NO contienen '.pdf' en ninguna parte del enlace y los guarda en 'descargas_no_pdf'
        enlaces_no_pdf = [enlace for enlace in listaDescarga if not re.search(r'\.pdf', enlace, re.IGNORECASE)]
        guardarEnArchivo(nombreMateria, 'descargas_no_pdf.txt', enlaces_no_pdf)

        # Escribir los enlaces en 'links.txt'
        print(f"\n\n{colored('Grabado de Links en \'links.txt\':', 'cyan', attrs=['bold'])}")
        guardarEnArchivo(nombreMateria, 'links.txt', listaOtros)

        # Descarga archivos
        for descarga in listaDescarga:
            DRIVER.get(descarga)

    except Exception as e:
        print(f"Se produjo un error durante el scraping: {e}")

    finally:
        # Asegurarse de cerrar el navegador siempre
        DRIVER.quit()


# Crea las carpetas para las materias
def crearCarpetas():
    global MATERIAS

    print(f"{colored('Creación de Carpetas', 'red', attrs=['bold'])}\n\n")

    for materia in MATERIAS:
        try:
            if not os.path.exists(materia):
                os.makedirs(materia)
                print(f"{colored('Carpeta creada:', 'green')} {materia}")
        except Exception as e:
            print(f"{colored(f'No se pudo crear la carpeta: {str(e)}', 'red')} {materia}")


# Muestra las materias cargadas
def mostrarMaterias():
    global MATERIAS
    global ancho_link
    global ancho_materia

    # Cabecera
    print(f"\n\n {colored('Materia'.ljust(ancho_materia), 'red', attrs=['bold'])} {colored('Link'.ljust(ancho_link), 'red', attrs=['bold'])}")
    print("-" * (ancho_materia + ancho_link))  # Línea divisoria

    # Impresión por materia
    for materia in MATERIAS:
        link = MATERIAS[materia]
        print(f"{materia.ljust(ancho_materia)} {colored(link.ljust(ancho_link), 'blue')}")

    # Otra línea
    print("-" * (ancho_materia + ancho_link))  # Línea divisoria


# Código principal del programa
def main():
    global DRIVER

    inicializarDriver()
    cargarMaterias()
    DRIVER.quit()  # Cierra el navegador

    mostrarMaterias()
    crearCarpetas()
    scrapMaterias()


# Punto de entrada
if __name__ == "__main__":
    error = False

    # Chequeos de configuración
    if not config.CREDENCIAL_USER:
        print("ERROR CONFIG: No se configuró un usuario.")
        error = True

    if not config.PAGINA_OBJETIVO:
        print("ERROR CONFIG: No se configuró una página objetivo.")
        error = True

    if not config.CREDENCIAL_PASSWORD:
        print("ERROR CONFIG: No se configuró una contraseña.")
        error = True

    if not error:
        main()  # Llamada a la función principal si no hay errores
    else:
        print("Abra el archivo 'config.py' para corregir los errores.")
