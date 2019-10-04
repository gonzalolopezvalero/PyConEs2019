# Este archivo contiene funciones para fragmentar y unir archivo o documentos.

from interfaz import *
import sys, os

KB = 1024
MB = 1000 * KB
chunksize = int(2.0 * MB)

# Fragmenta un archivo o documento en fragmentos de un tamaño determinado (por defecto 2 MB).
def fragmentar(self, fromfile, chunksize=chunksize):
    todir = os.path.splitext(fromfile)[0] + "_parts"

    fromfile = fromfile[fromfile.rfind('/') + 1:]   # De la ruta del fichero de origen, nos quedamos solo con el nombre del fichero y su extensión.
    todir = todir[todir.rfind('/') + 1:]            # De la ruta del directorio de destino, nos quedamos solo con el nombre del directorio.

    self.listWidget.addItem("Fragmentando '{}' en directorio '{}'...".format(fromfile, todir))

    # Creamos un directorio (si no existe).
    if not os.path.exists(todir):
        os.mkdir(todir)
    else:
        for fname in os.listdir(todir):
            # Si el directorio existe y tiene contenido, dejamos el directorio y eliminamos el contenido del directorio.
            os.remove(os.path.join(todir, fname))   

    partnum = 0
    input = open(fromfile, 'rb')

    while True:
        chunk = input.read(chunksize)

        if not chunk: break
        partnum += 1
        
        # Cogemos el nombre del fichero o documento (con la extensión incluída) y nos quedamos solo con el nombre.
        nombre_fich = os.path.splitext(input.name)[0]
        
        # Generamos los fragmentos con la extensión .enc y los almacenamo en el directorio.
        filename = os.path.join(todir, (nombre_fich + '_part_%03d' % partnum + '.enc'))
        fileobj = open(filename, 'wb')
        fileobj.write(chunk)
        fileobj.close()
    
    input.close()

    self.listWidget.addItem("Fragmentación finalizada: El archivo se dividió en {} partes. Ubicación: '{}'".format(partnum, todir))

    return todir

# A partir de un directorio, coge todos los fragmentos y los une en un solo archivo o documento.
def unir(self, fromdir):
    readsize = 1024
    dir_name = fromdir[fromdir.rfind('/') + 1:]     # De la ruta del directorio, nos quedamos solo con el nombre del directorio. 
    tofile = 'regenerado_' + dir_name.split('_parts')[0] + '.enc'   # El fichero que vamos a crear a partir de los fragmentos tendrá el prefijo 'regenerado_' seguido del nombre del directorio.

    self.listWidget.addItem("Uniendo fragmentos en el archivo '{}'...".format(tofile))

    output = open(tofile, "wb")
    parts = os.listdir(fromdir)     # Generamos una lista con las partes que existen en el directorio.
    parts.sort()                    # Ordenamos las partes por orden alfabético.
    
    for filename in parts:
        filepath = os.path.join(fromdir, filename)
        fileobj = open(filepath, 'rb')

        while True:
            filebytes = fileobj.read(readsize)  # Leemos el contenido de cada fragmento.
            if not filebytes: break
            output.write(filebytes)             # El contenido de cada fragmento lo escribimos en el fichero de destino.
        fileobj.close()
    output.close()

    self.listWidget.addItem("Unión finalizada: Las {} partes del archivo se unieron correctamente.".format(len(parts)))
    
    return output.name