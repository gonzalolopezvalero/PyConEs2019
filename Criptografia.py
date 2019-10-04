# Este archivo contiene las primitivas criptográficas.

from interfaz import *

import os, random, struct, sys
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto import Random
from Crypto.Hash import SHA256

# Genera clave pública y clave privada RSA.
def generar_claves(self, dir):

    # Crea directorio para almacenar claves.
    if not os.path.exists(dir):
        os.mkdir(dir)

    else:
        for fname in os.listdir(dir):
            os.remove(os.path.join(dir, fname))

    secret_code = self.lineEdit_10.text()
    key = RSA.generate(2048)    # Generamos par de claves RSA de 2048 bits.

    # Ciframos la clave privada con AES128 CBC.
    encrypted_private_key = key.export_key(passphrase=secret_code, pkcs=8, protection="scryptAndAES128-CBC")
    
    # Escribimos la clave privada cifrada en el archivo "private.pem"
    fich = open(dir + "/private.pem", "wb")
    fich.write(encrypted_private_key)
    fich.close()

    # Escribimos la clave pública en el archivo "public.pem"
    public_key = key.publickey().export_key()
    fich = open(dir + "/public.pem", "wb")
    fich.write(public_key)

    # Mostramos mensaje en la interfaz.
    self.listWidget.addItem("Par de claves (pública y privada) generadas correctamente.")

# Calcula el hash de un archivo o documento usando SHA256.
def calcularHash(self, file_name):
    with open(file_name, 'rb') as doc:
        bytes = doc.read()
        hash = SHA256.new(bytes)
    doc.close()

    return hash

# Firmamos el archivo o el documento con la clave privada.
def firmar_documento(self, file_name):
    secret_code = self.lineEdit_2.text()    # Introducimos clave descifrado AES para la clave privada.
    hash = calcularHash(self, file_name)    # Calculamos el hash del archivo.
    
    try:
        fich = open('keys/private.pem', 'rb')

        private_key = RSA.import_key(fich.read(), passphrase=secret_code)   # Obtenemos la clave privada de 'private.pem'.
        fich.close()
        self.listWidget.addItem("Documento firmado")    # Mostramos mensaje en la interfaz.
        
        return pkcs1_15.new(private_key).sign(hash)     # Devolvemos la firma del archivo o documento.

    except FileNotFoundError:
        self.listWidget.addItem("ERROR al firmar el archivo! El archivo de clave privada 'private.pem' no existe.")

    except ValueError:
        self.listWidget.addItem("ERROR! La clave de descifrado de la clave privada no es correcta.")

# Comprobamos la firma del archivo o del documento con la clave pública.
def comprobar_firma(self, file_name, firma):
    fich = open('keys/public.pem', 'rb')
    public_key = RSA.import_key(fich.read())    # Obtenemos la clave pública de 'public.pem'.
    fich.close()

    hash = calcularHash(self, file_name)        # Calculamos el hash del archivo o documento que hemos obtenido.

    try:
        """
        Con la clave pública, obtenemos el hash previamente calculado del archivo (hash del emisor).
        A continuación, comparamos este hash con el que hemos calculado sobre el archivo que hemos recibido (hash del receptor).
        """
        pkcs1_15.new(public_key).verify(hash, firma)
        self.listWidget.addItem("La firma es válida.")

    except (ValueError, TypeError):
        self.listWidget.addItem("La firma no es válida.")

# Cifrado del archivo con AES 128 CBC.
def encrypt_file(self, key, in_filename, out_filename=None, chunksize=64*1024):
    try:
        if not out_filename:
            out_filename = os.path.splitext(in_filename)[0] + '.enc'

        # Generamos un Vector de Inicialización con 16 valores aleatorios
        iv = Random.new().read(16)
        encryptor = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)
        filesize = os.path.getsize(in_filename)

        with open(in_filename, 'rb') as infile:
            with open(out_filename, 'wb') as outfile:
                outfile.write(struct.pack('<Q', filesize))
                outfile.write(iv)

                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        chunk += str.encode(' ' * (16 - len(chunk) % 16))

                    outfile.write(encryptor.encrypt(chunk))

        self.listWidget.addItem("Encriptando fichero " + in_filename)
        self.listWidget.addItem("Fichero encriptado: " + out_filename)

    except IOError:
        self.listWidget.addItem("encrypt_file: ERROR! El fichero " + in_filename + " no existe")

    return outfile

# Descifrado del archivo con AES 128 CBC.
def decrypt_file(self, key, in_filename, out_filename=None, chunksize=24*1024):
    try:
        if not out_filename:
            out_filename = os.path.splitext(in_filename)[0]

        with open(in_filename, 'rb') as infile:
            origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
            iv = infile.read(16)
            decryptor = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)

            with open(out_filename, 'wb') as outfile:
                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break

                    salida = decryptor.decrypt(chunk)
                    outfile.write(salida)

                outfile.truncate(origsize)

        self.listWidget.addItem("Desencriptando fichero " + in_filename)
        self.listWidget.addItem("Fichero desencriptado: " + out_filename)

    except IOError:
        self.listWidget.addItem("decrypt_file: ERROR! El fichero " + in_filename + " no existe")

    except ValueError as ex:
        if str(ex) == "AES key must be either 16, 24, or 32 bytes long":
            self.listWidget.addItem("ERROR! La clave de AES debe tener una longitud de 16, 24 o 32 bytes")
        
        else:
            self.listWidget.addItem("ERROR! Longitud de clave de descifrado incorrecta.")