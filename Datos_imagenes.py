"""
Este archivo contiene funciones de ocultación contenido de imágenes
y recuperación del contenido almacenado en las imágenes.
"""

from interfaz import *
import sys, os

from PIL import Image
from libxmp import XMPFiles, consts, XMPError
from libxmp import XMPMeta

from stegano import lsb
import codecs

# Leemos el contenido binario de un fichero y lo convertimos en UTF-8.
def procesarFichero(self, file_name):
    fich = open(file_name, "rb")
    hexadecimal = fich.read()
    fich.close()

    byte = codecs.encode(hexadecimal, "hex")

    return byte.decode("utf-8")

# A partir de un contenido, lo convertimos en hexadecimal y lo escribimos en un fichero.
def escribirFichero(self, file_name, content):
    byte = content.encode("utf-8")
    hexadecimal = codecs.decode(byte, "hex")

    fich = open(file_name, "wb")
    fich.write(hexadecimal)
    fich.close()

# A partir de un contenido binario, lo convertimos en UTF-8.
def procesarContenido(self, content):
    byte = codecs.encode(content, "hex")
    
    return byte.decode("utf-8")

# A partir de un contenido, lo convertirmos en hexadecimal y lo devolvemos (solo para la firma).
def procesarFirma(self, firma):
    byte = firma.encode("utf-8")
    hexadecimal = codecs.decode(byte, 'hex')

    return hexadecimal

# Oculta la información pasada por parámetro en los metadatos de una imagen.
def ocultar_informacion(self, img_name, tag, content):
    xmpfile = XMPFiles(file_path=img_name, open_forupdate=True)

    tipo = get_tipo(self, img_name)         # Obtenemos el tipo de la imagen.
        
    if tipo == '.jpg' or tipo == '.jpeg':   # Si la imagen es JPG o JPEG, almacenamos el contenido en los campos consts.XMP_NS_JPEG
        xmp = xmpfile.get_xmp()
        xmp.set_property(consts.XMP_NS_JPEG, tag, content)
        
    else:                                   # Si la imagen es PNG
        if xmpfile.get_xmp() is None:       # Comprobamos si tiene campos XMP, sino, creamos uno vacío.
            xmp = XMPMeta()
        else:                               # Si tiene campos XMP, los cogemos.
            xmp = xmpfile.get_xmp()
        
        xmp.set_property(consts.XMP_NS_PNG, tag, content)   # Almacenamos el contenido en los campos consts.XMP_NS_PNG
        
    xmpfile.put_xmp(xmp)
    xmpfile.close_file()

# Genera tantas imágenes como fragmentos tenga el fichero y en cada una de ellas almacena el contenido correspondiente.
def ocultar_en_imgs(self, fromdir, firma, extension, usar_metadatos):
    error = False
    todir = fromdir[:fromdir.rfind('_')] + '_images/'   # De la ruta del directorio, nos quedamos con el nombre y le añadimos el sufijo '_images'

    # Creamos un directorio (si no existe).
    if not os.path.exists(todir):
        os.mkdir(todir)

    else:
        for fname in os.listdir(todir):
            # Si el directorio existe y tiene contenido, dejamos el directorio y eliminamos el contenido del directorio.
            os.remove(os.path.join(todir, fname))

    parts = os.listdir(fromdir)     # Generamos una lista con los fragmentos que hay en el directorio.
    parts.sort()

    # Generamos tantas imágenes como fragmentos tenga el directorio.
    for index, part in enumerate(parts):
        part = part[:part.rfind('.')]
        img = Image.open(self.lineEdit_3.text())
        img.save(todir + part + '.' + img.format.lower())

        img2 = Image.open(todir + part + '.' + img.format.lower())

        content = procesarFichero(self, fromdir + part + '.enc')
        
        # En la primera imagen almacenamos: la firma del documento, la extensión y el contenido del primer fragmento.
        if 'part_001' in img2.filename:
            firma = procesarContenido(self, firma)

            # Si la opción seleccionada en la interfaz es la de Metadatos.
            if usar_metadatos == True:
                ocultar_informacion(self, img2.filename, 'firma', firma)
                ocultar_informacion(self, img2.filename, 'extension', extension)
                ocultar_informacion(self, img2.filename, 'contenido', content)
            
            # Si la opción seleccionada en la interfaz es la de LSB.
            else:
                try:
                    # En el caso de LSB, emplearemos ##### como separador para distinguir entre la firma, la extensión y el contenido.
                        secret = lsb.hide(img2.filename, firma + "#####" + extension + "#####" + content)
                        secret.save(img2.filename)
                except:
                    self.listWidget.addItem("ERROR! El mensaje que quieres almacenar es demasiado largo.")
                    error = True
                    break
        
        # A partir de la segunda imagen, solo almacenamos el contenido del fragmento (tanto para Metadatos como para LSB).
        else:
            if usar_metadatos == True:
                ocultar_informacion(self, img2.filename, 'contenido', content)
            else:
                try:
                    secret = lsb.hide(img2.filename, content)
                    secret.save(img2.filename)
                except:
                    self.listWidget.addItem("ERROR! El mensaje que quieres almacenar es demasiado largo.")
                    error = True
                    break

    if not error:
        self.listWidget.addItem("La información se ha ocultado en las imágenes del directorio '{}'".format(todir))

# Recupera la información almacenada en los metadatos de la imagen pasada por parámetro.
def recuperar_informacion(self, img_name, tag):
    xmpfile = XMPFiles(file_path=img_name)
    xmp = xmpfile.get_xmp()

    tipo = get_tipo(self, img_name)         # Obtenemos el tipo de la imagen.

    if tipo == '.jpg' or tipo == '.jpeg':   # Si la imagen es JPG o JPEG, obtenemos el contenido almacenado en los campos consts.XMP_NS_JPEG
        info = xmp.get_property(consts.XMP_NS_JPEG, tag)

    else:                                   # Si la imagen es PNG, obtenemos el contenido almacenado en los campos consts.XMP_NS_PNG
        info = xmp.get_property(consts.XMP_NS_PNG, tag)

    xmpfile.close_file()

    return info

# A partir de un directorio, obtenemos el contenido almacenado en cada una de las imágenes.
def recuperar_de_imgs(self, fromdir, usar_metadatos):
    #parts = os.listdir(fromdir)
    #todir = parts[0].split('_part_')[0] + '_parts'
    todir = fromdir + '_parts'

    # Creamos un directorio (si no existe).
    if not os.path.exists(todir):
        os.mkdir(todir)
    else:
        for fname in os.listdir(todir):
            # Si el directorio existe y tiene contenido, dejamos el directorio y eliminamos el contenido del directorio.
            os.remove(os.path.join(todir, fname))

    parts = os.listdir(fromdir)
    parts.sort()

    for index, part in enumerate(parts):
        # De la primera imagen extraemos: la extensión y el contenido.
        if 'part_001' in part:
            if usar_metadatos == True:      # Si la opción seleccionada en la interfaz es la de Metadatos.
                extension = recuperar_informacion(self, fromdir + '/' + part, 'extension')
                content = recuperar_informacion(self, fromdir + '/' + part, 'contenido')
            
            else:                           # Si la opción seleccionada en la interfaz es la de LSB.
                
                if get_tipo(self, fromdir + '/' + part) == '.jpg' or get_tipo(self, fromdir + '/' +part) == '.jpeg':     # Si la imagen es JPG, muestra error.
                    self.listWidget.addItem("Error!! El método LSB sólo permite imágenes PNG.")
                    return
                else:
                    extension = lsb.reveal(fromdir + '/' + part).split("#####")[1]
                    content = lsb.reveal(fromdir + '/' + part).split("#####")[2]
        
        # De las demás imágenes extraemos solo el contenido.
        else:
            if usar_metadatos == True:
                content = recuperar_informacion(self, fromdir + '/' + part, 'contenido')
            else:
                if get_tipo(self, fromdir + '/' + part) == '.jpg' or get_tipo(self, fromdir + '/' + part) == '.jpeg':
                    self.listWidget.addItem("Error!! El método LSB sólo permite imágenes PNG.")
                    return
                else:
                    content = lsb.reveal(fromdir + '/' + part).split("#####")[0]

        nombre_fich = part[:part.rfind('.')] + '.enc'
        filename = os.path.join(todir, nombre_fich)
        escribirFichero(self, filename, content)    # Una vez que hemos extraído todo el contenido de las imágenes, lo escribimos en el fichero de destino.

    return (todir, extension)

# Extraemos la firma del archivo de la primera imagen.
def obtener_firma_img(self, img_name, usar_metadatos):
    if usar_metadatos == True:  # Si el método seleccionado en la interfaz es Metadatos.
        firma = recuperar_informacion(self, img_name, 'firma')
    else:                       # Si el método seleccionado en la interfaz es LSB.

        if get_tipo(self, img_name) == '.jpg' or get_tipo(self, img_name) == '.jpeg':
            self.listWidget.addItem("Error!! El método LSB sólo permite imágenes PNG.")
            return
        else:
            firma = lsb.reveal(img_name).split("#####")[0]

    return firma

# Obtenemos el tipo de un archivo a partir del contenido hexadecimal de este.
def get_tipo(self, file_name):
    tipo = ""

    fich = open(file_name, "rb")
    content = fich.read()

    bytes = codecs.encode(content, 'hex')
    churro = bytes.decode('utf-8').upper()

    tipos = [ 
            ('D0CF11E0A1B11AE1', '576F72642E446F63756D656E742E', '.doc'),
            ('504B030414', '776F7264', '.docx'),
            ('504B030414', '70726573656E746174696F6E', '.pptx'),
            ('504B030414', '776F726B736865657473', '.xlsx'),
            ('25504446', '.pdf'),
            ('2525454F46', '.pdf'),
            ('66747970', '.mp4'),
            ('474946383961', '.gif'),
            ('474946383761', '.gif'),
            ('FFD8FFE800104A46494600', 'FFD9', '.jpg'),
            ('FFD8FFE100104A46494600', 'FFD9', '.jpg'),
            ('FFD8FFE000104A46494600', 'FFD9', '.jpg'),
            ('FFD8FFE300104A46494600', 'FFD9', '.jpeg'),
            ('FFD8FFE200104A46494600', 'FFD9', '.jpeg'),
            ('89504E47', '.png'),
            ]

    i = 0
    cont = 0

    encontrado = False

    while i < len(tipos) and encontrado == False:

        if len(tipos[i]) == 2 and '494433' in churro[:6]:   # Este caso es solo para ficheros .mp3
            encontrado = True
            tipo = '.mp3'

        elif len(tipos[i]) == 2 and 'FFD9' in churro[len(churro)-4:]:
            encontrado = True
            tipo = '.jpg'

        elif len(tipos[i]) == 2 and tipos[i][0] in churro:
            encontrado = True
            tipo = tipos[i][1]

        elif len(tipos[i]) == 3 and tipos[i][0] in churro and tipos[i][1] in churro:
            encontrado = True
            tipo = tipos[i][2]

        i += 1

    if encontrado == False:
        self.listWidget.addItem("Fich no soportado")
        return

    return tipo
