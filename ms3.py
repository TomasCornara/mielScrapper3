from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from termcolor import colored

import os
import re
import time
import config

DRIVER = webdriver #Esta variable contiene el driver que se esta usando en el momento
MATERIAS = {} #Este diccionario contiene las materias encontradas
ancho_materia = 35  # Ajusta según el texto más largo
ancho_link = 70     # Ajusta según la longitud máxima del link


#Esta funcion devuelve el driver de un navegador ya configurado
def inicializarDriver(path=""):
    global DRIVER

    # Opciones de Firefox
    options = Options()

    # Configura el navegador para ser headless
    # options.add_argument("-headless")

    # Desactivar el audio del navegador
    options.set_preference("media.volume_scale", "0.0")

    # Configurar las preferencias de descarga si se pasó un path
    options.set_preference("browser.download.folderList", 2)  # Usa un directorio personalizado
    options.set_preference("browser.download.dir", path)  # Directorio de descargas
    options.set_preference("browser.download.useDownloadDir", True)  # Usar el directorio de descargas
    options.set_preference("pdfjs.disabled", True)  # Evitar abrir PDFs dentro del navegador

    # Inicializar el controlador de Firefox con las configuraciones
    DRIVER = webdriver.Firefox(options=options)


#Completa el login de Miel
def iniciarSesion():
    global DRIVER

    #Usuario
    complTxtBox(By.CSS_SELECTOR, '#usuario', config.CREDENCIAL_USER)

    #Contraseña
    complTxtBox(By.CSS_SELECTOR, '#clave', config.CREDENCIAL_PASSWORD)

    #Entrar
    clicBoton(By.CSS_SELECTOR,'#btnLogin')

#Busca una texbox y rellena con informacion
def complTxtBox(tipoSelector, selector, info):
    global DRIVER

    elemento = DRIVER.find_element(tipoSelector, selector)
    elemento.click()
    elemento.send_keys(info)

#Busca un boton y clickea encima
def clicBoton(tipoSelector, selector):
    global DRIVER

    elemento = DRIVER.find_element(tipoSelector, selector)
    elemento.click()

#Busca las materias de miel y las agrega a materias
def cargarMaterias():
    global DRIVER
    global MATERIAS

    #Me aseguro de estar en pagina objetivo
    DRIVER.get(config.PAGINA_OBJETIVO)

    #Inicio sesion
    iniciarSesion()

    #Recargo
    time.sleep(5)
    DRIVER.get(config.PAGINA_OBJETIVO)

    #Busco el contenedor de los cursos
    contenedores = DRIVER.find_elements(By.CSS_SELECTOR, 'div.curso-sortable > div')

    #Por cada contenedor, extraigo el nombre y su link
    for contenedor in contenedores:
        nombre = contenedor.find_element(By.CSS_SELECTOR,'div.w3-col.w3-mobile.w3-padding.materia-descripcion > div.w3-slarge.materia-titulo').text
        link = contenedor.find_element(By.CSS_SELECTOR,'div.w3-rest.w3-mobile.materia-herramientas > div > a').get_attribute('href')
        MATERIAS[nombre] = link

#Screpea todas las materias
def scrapMaterias():
    global DRIVER
    global MATERIAS

    #Por cada materia, scrapeo
    for materia in MATERIAS:
        scrapMateria(materia,MATERIAS[materia])


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
        
        # Escribir los enlaces de descarga en 'descargas.txt'
        print(f"\n\n{colored('Descarga archivos y grabado de descargas.txt:', 'blue', attrs=['bold'])}")
        guardarEnArchivo(nombreMateria, 'descargas.txt', listaDescarga)

        # Escribir los enlaces en 'links.txt'
        print(f"\n\n{colored('Grabado de Links en \'links.txt\':', 'cyan', attrs=['bold'])}")
        guardarEnArchivo(nombreMateria, 'links.txt', listaOtros)

        #Descarga archivos
        for descarga in listaDescarga:
            DRIVER.get(descarga)

    except Exception as e:
        print(f"Se produjo un error durante el scraping: {e}")
    
    finally:
        # Asegurarse de cerrar el navegador siempre
        DRIVER.quit()

#Crea las carpetas para las materias
def crearCarpetas():
    global MATERIAS

    print(f"{colored("Creacion de Carpetas",'red',attrs=['bold'])}\n\n")

    for materia in MATERIAS:
        try:
            if not os.path.exists(materia):
                os.makedirs(materia)
                print(f"{colored("Carpeta creada:", 'green')} {materia}")
        except Exception as e:
            print(f"{colored(f"No se pudo crear la carpeta: {str(e)}", 'red')} {materia}")

#Muestra las materias cargadas
def mostrarMaterias():
    global MATERIAS
    global ancho_link
    global ancho_materia

    #Cabecera
    print(f"\n\n {colored('Materia'.ljust(ancho_materia),'red',attrs=['bold'])} {colored('Link'.ljust(ancho_link),'red',attrs=['bold'])}")
    print("-" * (ancho_materia + ancho_link))  # Línea divisoria

    #Impresion por materia
    for materia in MATERIAS:
        link = MATERIAS[materia] 
        print(f"{materia.ljust(ancho_materia)} {colored(link.ljust(ancho_link), 'blue')}")
    
    #Otra linea
    print("-" * (ancho_materia + ancho_link))  # Línea divisoria

#Codigo principal del programa
def main():
    global DRIVER

    inicializarDriver()
    cargarMaterias()
    DRIVER.quit() #Cierra el navegador

    mostrarMaterias()
    crearCarpetas()
    scrapMaterias()


#Punto de entrada
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