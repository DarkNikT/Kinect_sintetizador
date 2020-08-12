#!/usr/bin/env python
# coding: utf-8

import cv2
import numpy as np
import math
# Constantes Kinect

# Colores
BLACK = [0, 0, 0]
WHITE = [255, 255, 255]
GREEN = [0, 255, 0]
BLUE = [0, 0, 255]
RED = [255, 0, 0]

# Constantes proyecto
PATH_TECLADO_VIRTUAL = "teclado.png"                #Path imagen del teclado que se muestra en la pantalla.
PATH_TECLADO_COLORES = "coloresTeclado.png"         #Path imagen del teclado con el que segmenta las notas correspondientes.
PATH_MANO_ABIERTA_DER = "abierta_der.png"
PATH_MANO_ABIERTA_IZQ = "abierta_izq.png"
PATH_MANO_CERRADA_DER = "cerrado_der.png"
PATH_MANO_CERRADA_IZQ = "cerrado_izq.png"

####################################################################################################################

class Proceso_nota:
    # Clase para interpretar las notas
    notesArray = np.zeros((480, 640), dtype=np.uint8)   # Array de notas vacío.
    estado_list = []                                    # Array de estado de mano.
    @classmethod
    def update_notes_array(self, base_key, new_base_key, teclado_image, is_update_notes_array):
        """
        Funciona para actualizar el array de notas.
        :param base_key:        Int     Número actual de nota MIDI base de la octava del teclado.
        :param new_base_key:    Int     Número nuevo de nota MIDI base de la octava del teclado.
        :param teclado_image:   String  Path de la imagen de teclado PNG
        :param is_update_notes_array:   Boolean     Variable booleana que define si el array de notas está actualizado.
        :return:
        new_base_key:   Int             Número nuevo de nota MIDI base.
        notesArray:     Array Int       Array de notas.
        """
        # Si el array de notas no esta actualizado:
        if not is_update_notes_array:
            teclado = cv2.imread(teclado_image)  # Lee el teclado con las teclas definidas con colores.
            tecladoHSV = cv2.cvtColor(teclado, cv2.COLOR_BGR2HSV_FULL)  # Convierte la imagen del teclado a HSV.
            teclado_H = tecladoHSV[:, :, 0]  # Toma solo el canal H de la imagen leida.
            # Se tiene que el componente H (Hue-color) es el único que varía en los colores de la imagen
            # y esta relacionado con una tecla. El aumento semitono corresponde a un aumento de 15 en el componente H.
            for i, valorH in enumerate(range(15, 220, 15)):
                mask = np.logical_and(teclado_H >= valorH - 5, teclado_H <= valorH + 5)  # Se encuentran los pixeles que corresponden al valor HSV.
                self.notesArray[mask] = i + new_base_key  # Con la máscara se asigna el valor de la nota que corresponde al color.
                print ("{0}".format("Proceso terminado"))  # Me indica cuando el proceso ha terminado.
        # Si el array de notas ya ha sido creado:
        else:
            mask = self.notesArray >= base_key  # Se encuentran los pixeles que corresponden al valor HSV.
            self.notesArray = self.notesArray + (new_base_key - base_key)  # Se cambia las notas del array, a partir de la primera tecla mostrada de pantalla.
        return new_base_key, self.notesArray  # retorna el número correspondiente a la primera nota.



    # Función para obtener las notas, su posición y la imagen con los contornos detectados.
    @classmethod
    def get_note_from_position(self, positionx_list, positiony_list, estado_nota):  # Se ingresan los frames de profundidad y de color.
        """
        Función para conseguir la nota ubicada en la posición determinada por los centroides.
        :param positionx_list: Arreglo con las posiciones en el eje x.
        :param positiony_list: Arreglo con las posiciones en el eje y.
        :param estado_nota: Arreglo booleano con el estado de la nota detectada.
        :return:
        note_list: Arreglo que contiene las notas detectadas
        """
        # Se recorre el vector de posición puesto que contiene cuantos contornos se detectaron: 1 ó 2.
        note_list = []  # Vector de teclas vacía.
        for i in range(len(estado_nota)):
            # se verifica, si la nota debe reproducirse, la posición y la nota correspondiente.
            if estado_nota[i]:
                note = self.notesArray[positiony_list[i], positionx_list[i]]  # Se busca la nota en la que se encuentra el centroide.
                if note != 0:
                    # Si la nota es 0
                    note_list.append(note)
                else:
                    # Si la nota no corresponde a ninguna, se debe interpretar el gesto que se encuentra haciendo:
                    # debe intrepetar el gesto de control realizado.
                    print ("Fuera del rango de nota")
                    print ("interpretando gesto")
        return note_list
        

class Proceso_video:
    """
    Clase para realizar el procesamiento de los frames de profundidad y de color obtenidos por el Kinect.
    Funciones:
        curvar_distancia (frame_depth)  ---> depth2
        procesa_video (frame_depth, frame_RGB)  --->
    """
    # ATRIBUTOS DE LA CLASE
    estado_list = []            # Arreglo  establecen los estados de las manos.
    area_list = []              # Arreglo en la que se guardan las áreas detectadas.
    positionx_list = []         # Arreglo en la que se guardan la posición del centroide en el eje x.
    positiony_list = []         # Arreglo en la que se guardan la posición del centroide en el eje y.

    # Arreglos de paso de procesamiento
    depth_dist = []             # Reducción de los huecos en el array de distancia obtenida.
    medianDepth = []            # Aplicación de filtro de mediana.
    gaussianDepth32 = []        # Aplicación de filtro gaussiano.
    bilateralDepth = []         # Aplicación de filtro bilateral.
    manosUmbralizadas = []      # Umbralización con distancia y umbral definido.
    manosClosing = []           # Aplicación de operación morfologica de Closing.
    manosDilate = []            # Aplicación de operación morfologica de Dilatación.
    manosErode = []
    manosconcentroide = []      # Umbralización indicando el centroide del contorno hayado.
    manosconcontornos = []      # Umbralización para mostrar el contorno hallado.

    RESOLUTION_KINECT = (640, 480)  # Array con la resolución del Kinect

    THRESHOLD_VALUE = 100   # Valor inicial de umbral.
    DEPTH_VALUE = 600       # Valor inicia de profundidad.

    def area_triangulo(self, pos0, pos1, pos2):
        """
        Se realiza el cálculo del área de un triángulo definido por 3 puntos.
        Parámetros:
            pos0 ---> Arreglo coon posición x, y del punto 0.
            pos1 ---> Arreglo coon posición x, y del punto 1.
            pos2 ---> Arreglo coon posición x, y del punto 2.
        Return:
            area    ----> Valor del área del triángulo.
        """

        # trazando un vector desde pos0 a pos1 y de pos0 a pos2
        vec1 = np.array(pos1 - pos0)                    #
        vec2 = np.array(pos2 - pos0)
        # aplicación formula de área
        area = 0.5 * abs(np.cross(vec1, vec2)[-1])
        return area

    def area_poligono(self, puntos):
        """
        Se realiza el cálculo del área del polígono definido por unos puntos.
        Parámetros:
            puntos  --- > Arreglo con los puntos del polígono
        Return:
            area    ----> Valor del área del polígono
        """
        area = 0
        # Se recorren los puntos obtenido el área de triangulos internos de la figura. Se usa este método, siendo válido
        # para poligonos convexos.
        for i in range(len(puntos) - 2):
            area_t = self.area_triangulo(puntos[0], puntos[i + 1], puntos[i + 2])
            area += area_t
        return area

    def procesa_video(self, frame_depth, frame_RGB):
        """
            Se realiza el procesamiento de los frames obtenidos en la adquisición.
            Parametros:
                frame_depth     --> Frame de profundidad.
                frame_RGB       --> Frame de color.
            Return:
                frame_RGB       --> Frame RGB, con el teclado adicionado.
                positionx_list
                positiony_list
                notes
        """
        #################################################################################################
        # PREPROCESAMIENTO

        self.medianDepth = cv2.medianBlur(frame_depth.astype(np.float32), 5) 
        # Se curva la distancia obtenida.
        self.depth = self.medianDepth #self.curvar_distancia(self.medianDepth)
        self.depth.astype(np.uint16)

        #################################################################################################
        # UMBRALIZACIÓN
        mask_hands = 255*np.logical_and(
            # realiza una operacion AND para definir los pixeles de la imagen dentro del umbral.
            self.depth >= self.DEPTH_VALUE - self.THRESHOLD_VALUE,
            self.depth <= self.DEPTH_VALUE + self.THRESHOLD_VALUE)

        self.manosUmbralizadas = mask_hands.astype(np.uint8)  # Se convierte a formato uint8
        
        ##################################################################################################
        # OPERACIONES MORFOLOGICAS
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))   # Elemento estructurante de forma eliptica.
        kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))     # Elemento estructurante de forma cuadrada.
        
        #self.manosDilate = cv2.morphologyEx(self.manosUmbralizadas, cv2.MORPH_DILATE, kernel2)      # Aplicación de dilatación
        self.manosErode = cv2.morphologyEx(self.manosUmbralizadas, cv2.MORPH_ERODE, kernel2)      # Aplicación de erosion
        self.manosClosing = cv2.morphologyEx(self.manosErode, cv2.MORPH_CLOSE, kernel)             # Aplicación de closing.
        
        #vaciar los contenedores
        self.positionx_list = []    # Vector de posiciones en x vacía.
        self.positiony_list = []    # Vector de posiciones en y vacía.
        self.area_list = []         # Vector de área vacía.
        self.estado_list = []       # Vector de estado vacía.
        
        self.manosconcentroide = cv2.cvtColor(self.manosUmbralizadas, cv2.COLOR_GRAY2BGR)   # Imagen  a la cual se  centroide.
        self.manosconcontornos = np.zeros_like(self.manosconcentroide, dtype = np.uint8)    # Imagen vacía para mostrar los contornos y el poligono

        cx = 0  # Posición x del contorno.
        cy = 0  # Posición y del contorno.


        #############################################################################################
        # DETECCIÓN DE CONTORNOS

        # Se obtienen los contornos de la imagen umbralizada.
        contornos, _ = cv2.findContours(self.manosClosing, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        # Se dibuja el último contorno en la imagen vacía, color ROJO, grosor de 2.
        cv2.drawContours(self.manosconcontornos, contornos, -1, RED, 2)

        #############################################################################################
        # PROPIEDADES DE CONTORNOS

        # Se recorren los contornos detectados, solamente si solo se han detectado uno o dos, dado a que solo se pueden usar ambas manos.
        if len(contornos) > 0 and len(contornos) <= 2:
            # Se recorre el array de contornos
            for cont in contornos:
                ####################################  CONVEX HULL CONTORNOS  #########################################
                hull = cv2.convexHull(cont)
                cv2.polylines(self.manosconcontornos, [hull], True, BLUE, 3)
                ###################################### ÁREA DE CONTORNOS  ############################################
                area_ = self.area_poligono(hull)

                # si el area es mayor a un tamaño mínimo dado:
                if area_ >1500:
                    ################################### ENCONTRAR MOMENTOS ###########################################
                    try:
                        # Se usa un Try -except, debido a que en ocasiones se obtenia que los momentos podian ser <<0>> y se generaba un error en la división.
                        momentos = cv2.moments(cont)                    # Calcula los momentos del contorno.
                        cx = int(momentos['m10'] / momentos['m00'])     # Existe una fórmula que define la posición en x del centroide del contorno.
                        cy = int(momentos['m01'] / momentos['m00'])     # Existe una fórmula que define la posición en y del centroide del contorno.
                        cv2.circle(self.manosconcentroide, (cx, cy), 5, GREEN, 4)  # Dibuja el centroide, con un color verde, radio 5 y grosor 4.

                        self.positionx_list.append(cx)  # Adiciona la posición x determinada anteriomente, al vector de posición en x.
                        self.positiony_list.append(cy)  # Adiciona la posición y determinada anteriomente, al vector de posición en y.
                    except ZeroDivisionError:
                        print ("Division por cero")  # Se imprime si se da el error de división por cero.

                    # AGREGAR AREA DE LOS CONTORNOS
                    self.area_list.append(area_)
                    # Comparar si el tamaño que se encuentre dentro de un rango dado.
                    if  area_<4000:
                        # La mano está cerrada, la nota debe reproducirse.
                        estado = True
                        self.estado_list.append(estado)
                    else:
                        # La mano está abierta, la nota no debe reproducirse.
                        estado = False
                        self.estado_list.append(estado)

                    ############################## MÍNIMO RECTÁNGULO DEL CONTORNO ###################################
                    #x, y, w, h = cv2.boundingRect(cont)
                    # draw a green rectangle to visualize the bounding rect
                    #cv2.rectangle(frame_RGB, (x, y), (x + w, y + h), BLUE, 2)
                

        notes = Proceso_nota.get_note_from_position(self.positionx_list, self.positiony_list, self.estado_list)


        for j in range(len(self.estado_list)):
            cv2.circle(self.manosconcentroide, (self.positionx_list[j], self.positiony_list[j]), 20, GREEN,4)

        return self.positionx_list, self.positiony_list, notes

    # Función para colocar un teclado virtual en pantalla.
    def add_image(self, canvas, image_path):
        '''
            Función para adicionar una imagen PNG a la imagen de color manteniendo la transparencia de esta.
            Parametros:
                canvas         ---> Array de video, RGB uint8
                image_path   ---> Ubicación del archivo PNG a colocar en la imagen canvas.
            Return:
                addImage  --- > format:uint8 RGB
        '''
        imagen = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)    # Se lee la imagen PNG con el canal alfa incluido.
        mask = np.array(imagen[:, :, 3], dtype=np.bool)            # Dado a que la imagen PNG es un array de 640x480x4, seleccionamos la última que corresponde al canal alpha de transparencia.
        imagen_RGB = np.array(imagen[:, :, :3], dtype=np.uint8)   # Seleccionamos los canales RGB deel imagen, guardandolo con el formato uint8.
        canvas_RGB = np.array(canvas, dtype=np.uint8)               # Nos cercioramos de que tenga el formato uint8

        R_canvas = canvas_RGB[:, :, 0]  # Selecciona canal R de la imagen de color del sensor.
        G_canvas = canvas_RGB[:, :, 1]  # Selecciona canal G de la imagen de color del sensor.
        B_canvas = canvas_RGB[:, :, 2]  # Selecciona canal B de la imagen de color del sensor.

        R_imagen = imagen_RGB[:, :, 0]  # Selecciona canal R de la imagen a añadir.
        G_imagen = imagen_RGB[:, :, 1]  # Selecciona canal G de la imagen a añadir.
        B_imagen = imagen_RGB[:, :, 2]  # Selecciona canal B de la imagen a añadir.

        R_out = R_canvas * np.logical_not(mask) + R_imagen * mask  # Une los canales R  de la imagen y el imagen a añadir, usando la máscara de transparencia (canal alpha).
        G_out = G_canvas * np.logical_not(mask) + G_imagen * mask  # Une los canales G  de la imagen y el imagena añadir, usando la máscara de transparencia (canal alpha).
        B_out = B_canvas * np.logical_not(mask) + B_imagen * mask  # Une los canales B  de la imagen y el imagena añadir, usando la máscara de transparencia (canal alpha).

        addImage = cv2.merge((R_out, G_out, B_out))  # Combina los canales obtenidos en una imagen.
        return addImage.astype(np.uint8)  # Se retorna la imagen con la suma del imagen.

