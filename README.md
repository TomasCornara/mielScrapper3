# MielScrapper3

Miel scrapper es un script para backupear localmente los contenidos de las materias de Miel usando la libreria Selenium.

## Descripción del Proyecto

**ms3.py:** Una version basica del bot escrita sobre el driver para Firefox. Dado las limitaciones de este, solo puede descargar los links de a los contenidos.

**ms3C.py:** Esta es una version mas avanzada que usa el driver de Chrome y, aprovechando las caracteristicas experimentales, descarga tanto los links a los contenidos como los archivos en si mismos.

## Instrucciones de uso

1. Instalar las libreria Selenium y Termcolor usando Pip
2. Generar un archivo "config.py"
3. Abrir el archivo, copiar el siguiente formato y completar con los datos propios
```
CREDENCIAL_USER = 'mi_usuario' #Usuario
CREDENCIAL_PASSWORD = '123456789' #Contraseña
PAGINA_OBJETIVO = 'https://miel.unlam.edu.ar/'
```
_Nota: Pagina objetivo puede ser Miel o Historico. En cualquiera de los dos casos, requiere el link completo incluyendo el https. No puede ser de la forma 'miel.unlam.edu.ar'_
4. Colocar este nuevo archivo en el mismo directorio que el script
5. Abrir una nueva consola en el directorio y ejecutar el siguiente comando
```
Python ms3C.py
```

El bot va a crear una carpeta por cada materia **visible** y dentro de cada, van a descargar los archivos de los contenidos y generara tres archivos de texto extra:
- descargas_pdf.txt
_contiene los links a los pdfs a forma de respaldo_
  
- descargas_no_pdf.txt
_contiene los links a los archivos que no pudieron ser descargados_

- link.txt
_Contiene una copia de los links que estan posteados como contenido_

## Preview


![image](https://drive.google.com/uc?export=view&id=1xJ5RGNiJBbxdPaztkz3I32PIeEE83b0P)

