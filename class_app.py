#!/usr/bin/env python
# coding: utf-8

# IMPORTANDO LIBRERIAS
#####################################################################################################################

import numpy as np
import pygame
import gtk
import cv2

# CLASE UTILIZADA PARA CREAR UN BOTON
class Button:
    """
        Clase de botón para Pygame
    """
    def __init__(self, window, tipo, posx, posy, ancho, alto):
        setattr(self, 'body', None)                     # Cuerpo del bóton.
        setattr(self, 'text', "")                       # Texto del bóton.
        setattr(self, 'window', window)                 # Screen en la cual se dibuja la pantalla.
        setattr(self, 'tipo', tipo)
        setattr(self, 'state', False)
        setattr(self, 'colorBtn', (0, 0, 0))
        setattr(self, 'colorText', (255, 255, 255))
        setattr(self, 'Font', None)

        self.body = pygame.Rect(posx, posy, ancho, alto)    # Se crea el objeto rectángulo de Pygame.

    def setText(self, textOfButton):
        """
        Método para definir el texto del bóton.
        :param textOfButton:    String
        :return: None
        """
        self.text = textOfButton
    
    def clicked(self):
        """
        Método para cambiar el estado del bóton, toggle.
        :return: None
        """
        self.state=not(self.state)

    def checkClicked(self,posClick):
        """
        Método para saber si el click se encuentra en el área del botón.
        :param posClick:  Arreglo con la posición x, y del Click dado en pantalla.
        :return: Boolean
        """
        # Si la posición se encuentra dentro del botón.
        if self.body.collidepoint(posClick):
            self.clicked()  # Se ejecuta la función asociada al botón.
            return True     # Retornar True si se cumple la condición.

    def draw(self):
        """
        Función para renderizar el botón en la ventana de Pygame.
        :return: None
        """
        # Renderizar el texto del botón.
        TextSurf = self.Font.render(self.text, 0, self.colorText)
        # Obtener el rectángulo del texto renderizado.
        TextRect = TextSurf.get_rect()
        # Centrar el texto al cuerpo del botón.
        TextRect.center = self.body.center
        # Rellenar el botón de con el color dado.
        self.window.fill(self.colorBtn, self.body)
        # Colocar el texto en la posición del
        self.window.blit(TextSurf, TextRect)
# CLASE PARA CREAR UN SLIDER E INTERACTUAR CON EL
class Slider:

    def __init__(self, window, tipo, posx, posy, ancho, alto, rangeSlider):
        """
        # Inicializando la el constructor de slider.
        :param window:  # Ventana sobre la que se dibuja el slider.
        :param tipo:    # Si el valor de 0 del slider está centrado o en el borde.
        :param posx:    # Posición x del slider.
        :param posy:    # Posición y del slider.
        :param ancho:   # Ancho del slider.
        :param alto:    # Alto del slider.
        :param rangeSlider:     # Arreglo [min, max]
        """
        # ATRIBUTOS
        setattr(self, 'body', None)                 # Rectángulo del slider.
        setattr(self, 'value', 0)                   # Valor del slider.
        setattr(self, 'window', window)             # Ventana a la que se renderiza el slider.
        setattr(self, 'event_rel', None)
        setattr(self, 'tipo', tipo)                 # Si el slider es Vertical u Horizontal.
        setattr(self, 'state', False)               # Si el slider está presionado.
        setattr(self, 'range', rangeSlider)         # Rango del slider.
        setattr(self, 'colorBar', (0, 0, 75))
        setattr(self, 'colorBtn', (240, 100, 25))
        setattr(self, 'pasos', rangeSlider[1]-rangeSlider[0])

        # CREACION DEL SLIDER
        self.body = pygame.Rect(posx, posy, ancho, alto)            # Cuerpo del slider.
        self.btn_slider=pygame.Rect(posx, posy, alto*0.5, alto)     # Botón del slider.
        # Si el botón del slider está centrado:
        if tipo == "Center":
            self.btn_slider.center = self.body.center
        # Si el botón
        if tipo == "Desp":
            self.btn_slider.midleft = self.body.midleft
            self.value = min(self.range)

    def clicked(self):
        #Función que debe realizar
        #print("btn_pres")
        self.state=not(self.state)
        #obtener el valor del mismo
        

    def checkClicked(self,posClick):
        if self.btn_slider.collidepoint(posClick):
            self.clicked()
            return True
    def draw(self):
        # método usado para renderiazar el slider en la pantalla
        if self.state:
            posxn=pygame.mouse.get_rel()[0]

            self.btn_slider.move_ip(posxn,self.body.centery)
            self.btn_slider.clamp_ip(self.body)
            m_y=float(max(self.range)-min(self.range))
            m_x=float(self.body.width-self.btn_slider.width)
            pendiente=m_y/m_x

            if self.tipo=="Center":    
                #print((max(self.range)-min(self.range)))
                despx=(self.btn_slider.centerx-self.body.centerx)
                self.value=int(despx*pendiente-(self.body.width*0.5-self.btn_slider.width*0.5)*pendiente+max(self.range))
                #print("dx  {}, pendientex {}, pendientey {},  valor {}".format(despx,m_x,m_y,self.value))
            if self.tipo=="Desp":
                despx=(self.btn_slider.centerx-self.body.midleft[0]-self.btn_slider.width/2)
                self.value=int(despx*pendiente+min(self.range))
                #print("dx  {}, pendientex {}, pendientey {},  valor {}".format(despx,m_x,m_y,self.value))
        
        self.window.fill(self.colorBar, self.body)
        self.window.fill(self.colorBtn, self.btn_slider)

class ventana_Piano():
    def _init_(self):
        setattr(self, 'notes', [])
        self.NOTES_DICTIONARY = {
            '0': "     ",

            '27': " Si 2", '28': " Do 3", '29': "Do# 3", '30': " Re 3",
            # Diccionario que contiene el nombre de la tecla en
            '31': "Re# 3", '32': " Mi 3", '33': " Fa 3", '34': "Fa# 3",
            # cifrado americano, relacionandola con el número de esta.
            '35': "Sol 3", '36': "Sol#3", '37': " La 3", '38': "La# 3",

            '39': " Si 3", '40': " Do 4", '41': "Do# 4", '42': " Re 4",
            # Diccionario que contiene el nombre de la tecla en
            '43': "Re# 4", '44': " Mi 4", '45': " Fa 4", '46': "Fa# 4",
            # cifrado americano, relacionandola con el número de esta.
            '47': "Sol 4", '48': "Sol#4", '49': " La 4", '50': "La# 4",

            '51': " Si 4", '52': " Do 5", '53': "Do# 5", '54': " Re 5",
            # Diccionario que contiene el nombre de la tecla en
            '55': "Re# 5", '56': " Mi 5", '57': " Fa 5", '58': "Fa# 5",
            # cifrado americano, relacionandola con el número de esta.
            '59': "Sol 5", '60': "Sol#5", '61': " La 5", '62': "La# 5",
            '63': " Si 5", '64': " Do 6",
        }

        # Iniciar Pygame, necesario para usar los métodos de esta librería.
        pygame.init()
        # Se define el reloj de la ventana
        self.fpsClock = pygame.time.Clock()
        self.FPS = 20                        # Dado que el kinect funciona a 30 fps

        # Se crean las fuentes que se van a usar en la ventana.
        self.font = pygame.font.SysFont('arial', 32)         # Arial tamaño 32
        self.font2 = pygame.font.SysFont('arial', 20)        # Arial tamaño 10
        self.font3 = pygame.font.SysFont('budmo', 40)        #  tamaño 40

        #ATRIBUTOS VENTANA
        self.SCREEN_WIDTH = gtk.gdk.screen_width()      # Se toma el ancho de la pantalla del PC.
        self.SCREEN_HEIGHT = gtk.gdk.screen_height()-32 # Se toma el alto de la pantalla y se reduce en 32 para que ajuste mejor.
        self.NAME_WINDOW = "TECLADO VIRTUAL"            # Nombre de la ventana.
        
        #Se actualiza la ventana con el tamaño deseado y se crea el objeto screen.
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE)
        
        pygame.display.set_caption(self.NAME_WINDOW)    # Define el título de la ventana
        self.screen_rect = self.screen.get_rect()       # Se obtiene el rectángulo que cubre la ventana.
        
        # DEFINICION DE COLORES USADOS EN LA VENTANA
        self.COLOR_BLACK = [0,     0,   0]
        self.COLOR_WHITE = [255, 255, 255]
        self.COLOR_GREEN = [14,  102,  85]
        self.COLOR_BLUE = [41,  128, 185]
        self.COLOR_BLUE_DARK = [31,  118, 175]
        self.COLOR_RED = [255,   0,   0]
        self.COLOR_GRAY = [179, 182, 183]

        
        # CREACIÓN DEL ENTORNO DE TRABAJO
        # Se asigna un recuadro de un tamaño menor a la pantalla para ajustar los elementos.
        self.MARGIN_WIDTH = int(self.SCREEN_WIDTH*0.95)
        self.MARGIN_HEIGTH = int(self.SCREEN_HEIGHT*0.9)
        # Se crea un rectángulo de trabajo centrado en la pantalla.
        self.margin_rect = pygame.Rect((0, 0), (self.MARGIN_WIDTH, self.MARGIN_HEIGTH))
        self.margin_rect.center = self.screen_rect.center   # Centrar el recuadro creado.

        # CREANDO DIVISIONES
        self.ancho_div1 = int(self.margin_rect.width*0.8)
        self.alto_div1 = self.margin_rect.height
        self.div1 = pygame.Rect(self.margin_rect.topleft, (self.ancho_div1, self.alto_div1))


        # divisiones de los botones, se cuentan 8 divisiones
        self.altura_divs = int(self.alto_div1/8)
        self.ancho_divs = self.margin_rect.width-self.ancho_div1

        self.div2=pygame.Rect(self.div1.topright, (self.ancho_divs, self.altura_divs))
        self.div3=pygame.Rect(self.div2.bottomleft, (self.ancho_divs, self.altura_divs))
        self.div4=pygame.Rect(self.div3.bottomleft, (self.ancho_divs, self.altura_divs))
        self.div5=pygame.Rect(self.div4.bottomleft, (self.ancho_divs, self.altura_divs))
        self.div6=pygame.Rect(self.div5.bottomleft, (self.ancho_divs, self.altura_divs))
        self.div7=pygame.Rect(self.div6.bottomleft, (self.ancho_divs, self.altura_divs))
        self.div8=pygame.Rect(self.div7.bottomleft, (self.ancho_divs, self.altura_divs))
        self.div9=pygame.Rect(self.div8.bottomleft, (self.ancho_divs, self.altura_divs))

        # Rectángulo de imagen
        # se usa la relación de 3/4 para el alto
        self.rect_image = pygame.Rect(self.div1.topleft, (int(self.div1.width*0.8), int(int(self.div1.width*0.8)*0.75)))
        self.rect_image.center = self.div1.center
        # Rectángulo de imagen si se está mostrando los pasos
        self.resolution_kinect = (640, 480)
        self.rect_image2 = pygame.Rect(self.div1.topleft, self.resolution_kinect)
        self.rect_image2.midleft = self.div1.midleft

        # rectángulos para mostrar los pasos.
        self.ancho_divs2 = self.div1.width-self.resolution_kinect[0]
        self.alto_divs2 = int(self.alto_div1/4)  # Se muestran 3 pasos.

        self.div10 = pygame.Rect(self.rect_image2.topright, (self.ancho_divs2, self.alto_divs2))
        self.div10.topright = self.div1.topright
        self.div11 = pygame.Rect(self.div10.bottomleft, (self.ancho_divs2, self.alto_divs2))
        self.div12 = pygame.Rect(self.div11.bottomleft, (self.ancho_divs2, self.alto_divs2))
        self.div13 = pygame.Rect(self.div12.bottomleft, (self.ancho_divs2, self.alto_divs2))

        # tamaño de los rect de pasos
        self.recPasos = pygame.Rect(self.div10.topleft, (self.alto_divs2*4/3, self.alto_divs2))

        self.image_kinect = []              # Variable para guardar la imagen del kinect
        self.rect_image_kinect=pygame.Rect((0, 0), (640, 480))
        self.rect_image_kinect.center = self.div1.center

        self.factorMano = [float(self.rect_image.width) / float(self.rect_image2.width), float(self.rect_image.height) / float(self.rect_image2.height)]
        
        setattr(self, 'image_kinect', [])
        setattr(self, 'image_size', [self.rect_image.width, self.rect_image.height])
        setattr(self, 'pasos_procesa', [])

        # BOTONES
        self.boton_inicia = Button(self.screen, "TOGGLE", self.div2.centerx-120/2, self.div2.centery-50/2, 120, 50)
        self.boton_inicia.text = "INICIAR"
        self.boton_inicia.colorBtn = self.COLOR_GREEN
        self.boton_inicia.Font = self.font

        self.boton_pasos = Button(self.screen, "TOGGLE", self.div3.midleft[0], self.div3.centery-50/2, self.div3.width, 50)
        self.boton_pasos.text = "VER PASOS"
        self.boton_pasos.colorBtn = self.COLOR_BLUE
        self.boton_pasos.Font = self.font


        # SLIDERS
        self.SLIDER_WIDTH = self.ancho_divs
        self.SLIDER_HEIGHT = 50
        self.SLIDER_BTN_WIDTH = 50
        
        # slider ángulo
        setattr(self, 'tilt_kinect', 0)
        setattr(self, 'is_touched_slider_ang', False)
        X, Y = self.div5.midleft[0], self.div5.centery-self.SLIDER_HEIGHT/2
        self.slider_ang = Slider(self.screen, "Center", X, Y, self.SLIDER_WIDTH, self.SLIDER_HEIGHT, [-25, 25])
        
        # slider distancia
        setattr(self, 'is_touched_slider_dist', False)
        setattr(self, 'depth', 70)
        X, Y = self.div7.midleft[0], self.div7.centery-self.SLIDER_HEIGHT/2
        self.slider_depth = Slider(self.screen, "Desp", X, Y, self.SLIDER_WIDTH, self.SLIDER_HEIGHT, [70, 150])

        # slider umbral
        setattr(self, 'is_touched_slider_umb', False)
        X, Y = self.div9.midleft[0], self.div9.centery-self.SLIDER_HEIGHT/2
        self.slider_umbral = Slider(self.screen, "Desp", X, Y, self.SLIDER_WIDTH, self.SLIDER_HEIGHT, [10, 30])
        setattr(self, 'umbral', 10)

        self.is_running = True
        self.is_take_video = False
        self.is_touched_slider_depth = False
        self.is_touched_slider_umbral = False
        self.state_window = False
        
        setattr(self, 'is_running', True)
        setattr(self, 'is_take_video', False)
        setattr(self, 'is_show_pasos', False)

        # TEXTO
        self.text_inicializar = self.font2.render("PRESIONE INICIAR", 0, self.COLOR_RED)
        self.text_instrucciones = self.font.render("UBIQUESE A LA DISTANCIA INDICADA", 0, self.COLOR_BLACK)



        setattr(self, 'mano_posx', [])
        setattr(self, 'mano_posy', [])
        setattr(self, 'mano_state', [])

        self.desplazaMano = [0, 0]

        self.image_mano_der = pygame.transform.scale(pygame.image.load("abierta_der.png"), [90, 120])
        self.image_mano_izq = pygame.transform.scale(pygame.image.load("abierta_izq.png"), [90, 120])
        self.image_puno_der = pygame.transform.scale(pygame.image.load("cerrado_der.png"), [70, 90])
        self.image_puno_izq = pygame.transform.scale(pygame.image.load("cerrado_izq.png"), [70, 90])

        self.recAbierto = self.image_mano_der.get_rect()
        self.recCerrado = self.image_puno_der.get_rect()


    # Función para gestionar los eventos de botones y sliders
    def get_eventos(self):
        evento_actual = []
        events = pygame.event.get() #Se observan los eventos de mouse.
        for event in events:
            # Si el mouse es presionado:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Se obtiene la posición del click en la pantalla.
                mouse_pos = event.pos
                # Si se presiona el botón de iniciar:
                if self.boton_inicia.checkClicked(mouse_pos):
                    print("Iniciando toma datos")
                    # Toggle de la variable de tomar video.
                    self.is_take_video = not self.is_take_video
                    if not self.is_take_video:
                        self.is_show_pasos = False
                # Si se presiona el botón de mostrar pasos:
                if self.boton_pasos.checkClicked(mouse_pos):
                    if self.is_take_video:
                        print("Mostrando pasos")
                        self.is_show_pasos = not self.is_show_pasos
                        evento_actual.append("MOSTRAR_PASOS")
                # Si se presiona el botón del slider de ángulo:
                if self.slider_ang.checkClicked(mouse_pos) and event == pygame.MOUSEMOTION:
                    self.is_touched_slider_ang = True
                    self.slider_ang.event_rel = event.get_rel()
                    evento_actual.append("ACTUALIZA_ANGULO")
                # Si se presiona el botón del slider de profundidad:
                if self.slider_depth.checkClicked(mouse_pos) and event == pygame.MOUSEMOTION:
                    self.is_touched_slider_dis = True
                    evento_actual.append("ACTUALIZA_PROFUNDIDAD")
                    self.slider_depth.event_rel=event.get_rel()
                # Si se presiona el botón del slider de umbral:
                if self.slider_umbral.checkClicked(mouse_pos) and event == pygame.MOUSEMOTION:
                    self.is_touched_slider_umbral = True
                    evento_actual.append("ACTUALIZA_UMBRAL")
                    self.slider_umbral.event_rel = event.get_rel()
            # Despues del clic:
            if event.type == pygame.MOUSEBUTTONUP:
                self.is_touched_slider_ang = False
                self.slider_ang.state = self.is_touched_slider_ang
                self.is_touched_slider_depth = False
                self.slider_depth.state = self.is_touched_slider_depth
                self.is_touched_slider_umbral = False
                self.slider_umbral.state = self.is_touched_slider_umbral

            # Si el evento es salir:
            if event.type == pygame.QUIT:
                self.is_running = False
                setattr(self, 'is_running', False)
        return evento_actual

    # Función que recibe un array y lo convierte a surface, y poder mostrarse en la ventana.
    def cvimage_a_pygame(self, imageData, resize, newSize):

        if len(imageData.shape) == 3:
            imageOut = imageData[:, :, ::-1]                                                   # La selección [:,:,::-1] indica que se toman todos los pixeles, pero se invierte el color RGB a BGR.
            image_ = pygame.image.frombuffer(imageOut.tostring(), imageOut.shape[1::-1], "RGB")  # Devuelve el objeto imagen compatible con pygame.
        elif len(imageData.shape) == 2:
                image_ = imageData.astype(np.uint8)
                imageOut = cv2.cvtColor(image_, cv2.COLOR_GRAY2BGR)
                image_ = pygame.image.frombuffer(imageOut.tostring(), imageOut.shape[1::-1], "RGB")     # Devuelve el objeto imagen compatible con pygame.
        if resize:
            image_ = self.resize_surface(image_, newSize)
        return image_

    # Función para escalar una superficie renderizada en Pygame.
    def resize_surface(self, surface, newSize):
        return pygame.transform.scale(surface, newSize)

    # Función que actualiza la ventana.
    def update_window(self):
        # Ajustando elementos
        self.screen_rect = self.screen.get_rect()
        self.margin_rect.center = self.screen_rect.center
        # Renderizar el fondo de color blanco.
        self.screen.fill(self.COLOR_WHITE)
        # Texto inicial.
        rect_text = self.text_instrucciones.get_rect()
        rect_text.topleft = self.screen_rect.topleft
        self.screen.blit(self.text_instrucciones, rect_text)

        text_notes=""                                               #Texto vacío
        for i in range(len(self.notes)):                                             #Recorre el vector de notas obtenido.
            text_notes+="    "+self.NOTES_DICTIONARY[str(self.notes[i])]             #Coloca el nombre de la enesima nota.
        notes_surf = self.font3.render(text_notes, 0, self.COLOR_BLACK)
        notes_rect = notes_surf.get_rect()


        # Si se esta mostrando el video del Kinect:
        if self.is_take_video:

            ## se reinician las posiciones de las manos

            #self.desplazaMano = []

            # Si se estan mostrando los pasos:
            if self.is_show_pasos:

                # La imagen se coloca en el rectángulo de imagen más pequeño.
                self.screen.blit(self.image_kinect, self.rect_image2)
                notes_rect.midbottom = self.rect_image2.midbottom
                self.screen.fill(self.COLOR_WHITE, notes_rect)
                self.screen.blit(notes_surf, notes_rect)  # Se coloca el nombre de la nota que está siendo tocada en pantalla, posición (20,570).

            else:

                # La imagen se coloca en el rectángulo más grande.
                self.screen.blit(self.image_kinect, self.rect_image)
                notes_rect.midbottom = self.rect_image.midbottom
                self.screen.fill(self.COLOR_WHITE, notes_rect)
                self.screen.blit(notes_surf, notes_rect)  # Se coloca el nombre de la nota que está siendo tocada en pantalla, posición (20,570).




            #self.screen.blit(self.image_kinect,self.rect_image)
            self.boton_inicia.text = "PARAR"                                                               #Establece el mensaje del boton de iniciar.
            self.boton_inicia.colorBtn = self.COLOR_GREEN                                                                 #Establece el color del botón de iniciar.

            for i in range(len(self.mano_state)):  # Recorre el vector de notas obtenido.

                if self.mano_state[i]:
                    if self.is_show_pasos:

                        self.desplazaMano = self.rect_image2.topleft
                        self.recCerrado.center = [self.mano_posx[i] + self.desplazaMano[0], self.mano_posy[i] + self.desplazaMano[1]]

                    else:
                        self.desplazaMano = self.rect_image.topleft
                        self.recCerrado.center = [int(self.factorMano[0]*self.mano_posx[i] + self.desplazaMano[0]),
                                              int(self.factorMano[1]*self.mano_posy[i] + self.desplazaMano[1])]

                    self.screen.blit(self.image_puno_der, self.recCerrado)


                elif not self.mano_state[i]:
                    if self.is_show_pasos:
                        self.desplazaMano = self.rect_image2.topleft
                        self.recAbierto.center = [self.mano_posx[i] + self.desplazaMano[0], self.mano_posy[i] + self.desplazaMano[1]]
                    else:
                        self.desplazaMano = self.rect_image.topleft
                        self.recAbierto.center = [int(self.factorMano[0]*self.mano_posx[i] + self.desplazaMano[0]),
                                                  int(self.factorMano[1]*self.mano_posy[i] + self.desplazaMano[1])]
                    self.screen.blit(self.image_mano_der, self.recAbierto)

        else:
            # Muestra estado
            self.boton_inicia.text = "INICIAR"                                                               #Establece el mensaje del boton de iniciar.
            self.boton_inicia.colorBtn = self.COLOR_RED                                                                 #Establece el color del botón de iniciar.
            

            rect_text = self.text_inicializar.get_rect()
            rect_text.center = self.div1.center
            self.screen.blit(self.text_inicializar, rect_text)

        if self.is_show_pasos:
            self.boton_pasos.colorBtn = self.COLOR_BLUE_DARK
            self.muestraPasos()
        else:
            self.boton_pasos.colorBtn = self.COLOR_BLUE

        self.boton_inicia.draw()
        self.boton_pasos.draw()
        self.slider_ang.draw()
        self.slider_depth.draw()
        self.slider_umbral.draw()

        # Se muestra el valor del slider de ángulo en la pantalla
        self.tilt_kinect = self.slider_ang.value
        text_value = self.font.render("Posicion: {0}".format(self.tilt_kinect), 0, self.COLOR_BLACK)
        rect_text = text_value.get_rect()
        rect_text.center = self.div4.center
        self.screen.blit(text_value, rect_text) #Se coloca en pantalla el mensaje del botón de iniciar.

        self.depth = self.slider_depth.value*10
        text_value = self.font.render("distancia: {0}".format(self.slider_depth.value), 0, self.COLOR_BLACK)
        rect_text = text_value.get_rect()
        rect_text.center = self.div6.center
        self.screen.blit(text_value, rect_text) #Se coloca en pantalla el mensaje del botón de iniciar.

        self.umbral = self.slider_umbral.value*2
        text_value = self.font.render("Umbral: {0}".format(self.slider_umbral.value), 0, self.COLOR_BLACK)
        rect_text = text_value.get_rect()
        rect_text.center = self.div8.center
        self.screen.blit(text_value, rect_text) #Se coloca en pantalla el mensaje del botón de iniciar.


        self.fpsClock.tick(self.FPS)
        pygame.display.flip()

    def exit(self):
        pygame.quit()

    def muestraPasos(self):
        dir_pos = {'p0': self.div10, 'p1': self.div11, 'p2': self.div12, 'p3': self.div13}
        # Se recorre el array de imagenes
        for i, p in enumerate(self.pasos_procesa):
            # Cual es el rectángulo actual.
            rect_ = dir_pos["p{}".format(i)]
            # Se centra al rectángulo actual.
            self.recPasos.center = rect_.center
            paso_ = self.cvimage_a_pygame(p, True, [self.recPasos.width, self.recPasos.height])
            self.screen.blit(paso_, self.recPasos)

    def change_threshold(value):
        THRESHOLD_VALUE = value

    def change_depth(value):
        DEPTH_VALUE = value
