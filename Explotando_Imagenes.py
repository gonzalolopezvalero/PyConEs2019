from interfaz import *
import Criptografia, Fragmentar_unir, Datos_imagenes

import os, sys, time
from PyQt5.QtCore import QFileInfo
from PyQt5.QtWidgets import QMessageBox, QFileDialog

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)

        # Sección 'Generar claves RSA':
        self.pushButton_14.clicked.connect(self.comprobarCamposRSA)         # Botón Generar
        
        # Sección 'Cifrar fichero y ocultar la información en imágenes':
        self.pushButton.clicked.connect(self.openDocCifrar)                 # Botón Examinar de Fichero
        self.pushButton_3.clicked.connect(self.openImgCifrar)               # Botón Examinar de Imagen
        
        self.pushButton_4.clicked.connect(self.comprobarCamposCifrado)      # Botón Ejecutar

        # Sección 'Obtener información de las imágenes y recomponer fichero':
        self.pushButton_5.clicked.connect(self.openDirImg)                  # Botón Examinar de Imágenes
        self.pushButton_7.clicked.connect(self.comprobarCamposDescifrado)   # Botón Ejecutar

        # Sección 'Comprobar firma fichero regenerado':
        self.pushButton_8.clicked.connect(self.openDocFirma)                # Botón Examinar de Fichero
        self.pushButton_9.clicked.connect(self.openImgFirma)                # Botón Examinar de Imagen

        self.pushButton_10.clicked.connect(self.comprobarCamposFirma)       # Botón Comprobar

    # Comprueba que no haya ningún campo vacío en la sección "Generar claves RSA".
    def comprobarCamposRSA(self):
        if self.lineEdit_10.text() == "":
            self.mostrarVentanaError("Error RSA", "Error!! Hay campos incompletos.")   # Si hay algún campo incompleto, muestra un mensaje de error.

        else:
            Criptografia.generar_claves(self, 'keys')

    # Comprueba que no haya ningún campo vacío en la sección "Cifrar fichero y ocultar la información en imágenes".
    def comprobarCamposCifrado(self):
        if self.lineEdit.text() == "" or self.lineEdit_2.text() == "" or self.lineEdit_3.text() == "" or self.lineEdit_4.text() == "" or not self.radioButton.isChecked() and not self.radioButton_2.isChecked():
            self.mostrarVentanaError("Error campos ocultación", "Error!! Hay campos incompletos.")     # Si hay algún campo incompleto, muestra un mensaje de error.

        else:
            DOC = self.lineEdit.text()          # Ruta del documento seleccionado.
            key = self.lineEdit_4.text()        # Clave de cifrado AES (para cifrar el contenido del documento).

            try:
                firma = Criptografia.firmar_documento(self, DOC)        # Firma el documento.

                extension = Datos_imagenes.get_tipo(self, DOC)          # Obtiene la extensión.
                ENC_DOC = Criptografia.encrypt_file(self, key, DOC)     # Cifra el contenido del documento.

                if self.radioButton.isChecked():    # Método seleccionado: Metadatos
                    fromdir = Fragmentar_unir.fragmentar(self, ENC_DOC.name, chunksize=2000000) + '/'   # Empleamos fragmentos de 2 MB.
                    Datos_imagenes.ocultar_en_imgs(self, fromdir, firma, extension, True)               # Ocultamos la información en las imágenes.
            
                else:   # Método seleccionado: LSB
                    img = self.lineEdit_3.text()
                
                    if self.errorLSB(img) == False:     # Si la imagen de LSB es PNG funciona correctamente. Sino, el método errorLSB muestra un error.
                        fromdir = Fragmentar_unir.fragmentar(self, ENC_DOC.name, chunksize=200000) + '/'    # Empleamos fragmentos de 200 KB.
                        Datos_imagenes.ocultar_en_imgs(self, fromdir, firma, extension, False)              # Ocultamos la información en las imágenes.
            except TypeError:
                self.listWidget.addItem("ERROR al firmar el documento!")

            except ValueError:
                self.listWidget.addItem("ERROR! La clave de AES debe tener una longitud de 16, 24 o 32 bytes")

    # Comprueba que no haya ningún campo vacío en la sección "Obtener información de las imágenes y recomponer fichero".
    def comprobarCamposDescifrado(self):
        if self.lineEdit_5.text() == "" or self.lineEdit_6.text() == "" or not self.radioButton_3.isChecked() and not self.radioButton_4.isChecked():
            self.mostrarVentanaError("Error campos descifrado", "Error!! Hay campos incompletos.")     # Si hay algún campo incompleto, muestra un mensaje de error.

        else:
            dir_imagenes = self.lineEdit_5.text()       # Ruta del directorio con las imágenes.
            key = self.lineEdit_6.text()                # Clave de descifrado AES (para descifrar el contenido del documento).
            
            try:

                if self.radioButton_3.isChecked():
                    datos = Datos_imagenes.recuperar_de_imgs(self, dir_imagenes, True)  # Método empleado: Metadatos.
                else:
                    datos = Datos_imagenes.recuperar_de_imgs(self, dir_imagenes, False) # Método empleado: LSB

                DIR_FRAGMENTOS = datos[0]   # Directorio con los fragmentos del documento.
                ENC_DOC = Fragmentar_unir.unir(self, DIR_FRAGMENTOS)    # Une los fragmentos y genera el documento cifrado.
                extension = datos[1]
                output_file = ENC_DOC[:ENC_DOC.rfind('.')] + extension  # Nombre que tendrá el fichero cuando se descifre.
                Criptografia.decrypt_file(self, key, ENC_DOC, out_filename=output_file)
            
            except TypeError:
                self.listWidget.addItem("ERROR al recuperar la información de las imágenes!")

            except AttributeError:
                self.listWidget.addItem("ERROR! Los métodos de ocultación y de recuperación no son compatibles.")

            except Datos_imagenes.XMPError:
                self.listWidget.addItem("ERROR! Las imágenes seleccionadas no tienen metadatos.")

    # Comprueba que no haya ningún campo vacío en la sección "Comprobar firma fichero regenerado".
    def comprobarCamposFirma(self):
        if self.lineEdit_8.text() == "" or self.lineEdit_9.text() == "" or not self.radioButton_5.isChecked() and not self.radioButton_6.isChecked():
            self.mostrarVentanaError("Error campos firma", "Error!! Hay campos incompletos.")
        
        else:
            fich = self.lineEdit_8.text()
            img = self.lineEdit_9.text()

            try:

                if self.radioButton_6.isChecked():
                    firma = Datos_imagenes.obtener_firma_img(self, img, True)   # Extrae la firma de la primera imagen empleando Metadatos.
                else:
                    firma = Datos_imagenes.obtener_firma_img(self, img, False)  # Extrae la firma de la primera imagen empleando LSB.

                firma = Datos_imagenes.procesarFirma(self, firma)
                Criptografia.comprobar_firma(self, fich, firma)     # Comprueba la validez de la firma.

            except TypeError:
                self.listWidget.addItem("ERROR al recuperar la información de las imágenes!")

            except AttributeError:
                self.listWidget.addItem("ERROR! Los métodos de ocultación y de recuperación no son compatibles.")

            except Datos_imagenes.XMPError:
                self.listWidget.addItem("ERROR! Las imágenes seleccionadas no tienen metadatos.")

    # Función encargada de mostrar el selector de archivos al hacer click en el botón "Examinar".
    def abrirFichero(self, text, tipo_archivos):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fich = QtWidgets.QFileDialog.getOpenFileName(QFileDialog(), text, "", tipo_archivos, options=options)

        file_path = QFileInfo(fich[0]).filePath()

        return file_path

    # Función encargada de mostrar el selector de directorios al hacer click en el botón "Examinar".
    def abrirDirectorio(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        dir = QtWidgets.QFileDialog.getExistingDirectory(QFileDialog(), "Seleccionar directorio imágenes", options=options)

        return dir

    # Permite seleccionar un archivo y escribe su ruta en el campo de texto.
    def openDocCifrar(self):
        file_path = self.abrirFichero("Seleccionar fichero", "All Files (*)")
        self.lineEdit.setText(file_path)

    # Permite seleccionar una imagen y escribe su ruta en el campo de texto.
    def openImgCifrar(self):
        file_path = self.abrirFichero("Seleccionar imagen", "Image Files (*.png *.jpg *.jpeg)")
        self.lineEdit_3.setText(file_path)

    # Permite seleccionar un directorio y escribe su ruta en el campo de texto.
    def openDirImg(self):
        dir_path = self.abrirDirectorio()
        self.lineEdit_5.setText(dir_path)

    # Permite seleccionar un archivo y escribe su ruta en el campo de texto.
    def openDocFirma(self):
        file_path = self.abrirFichero("Seleccionar fichero", "All Files (*)")
        self.lineEdit_8.setText(file_path)

    # Permite seleccionar una imagen y escribe su ruta en el campo de texto.
    def openImgFirma(self):
        file_path = self.abrirFichero("Seleccionar imagen", "Image Files (*.png *.jpg *.jpeg)")
        self.lineEdit_9.setText(file_path)

    # Permite seleccionar un archivo y escribe su ruta en el campo de texto.
    def openPublicKey(self):
        file_path = self.abrirFichero("Seleccionar fichero clave pública", "All Files (*)")
        self.lineEdit_11.setText(file_path)

    # Muestra una ventana de error cuando hay campos incompletos.
    def mostrarVentanaError(self, title, text):
        self.alertBox = QMessageBox()
        self.alertBox.setWindowTitle(title)
        self.alertBox.setText(text)
        self.alertBox.show()

    def errorLSB(self, img):
        error = False
        extension = Datos_imagenes.get_tipo(self, img)

        if extension == '.jpeg' or extension == '.jpg':
            self.mostrarVentanaError("Error método LSB", "Error!! El método LSB sólo permite imágenes PNG.")
            error = True

        return error

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
