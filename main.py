#!/usr/bin/env python
# coding: utf-8

########################################################################################################################
######################################### LIBRERIAS ####################################################################
import freenect
import cv2
import numpy as np
import time
from class_app import ventana_Piano
from mingus.midi import fluidsynth
from Class_Proceso import Proceso_nota
from Class_Proceso import Proceso_video
from Kinect_Freenect import Kinect

from mingus.midi import fluidsynth
from mingus.containers import Note, NoteContainer, Piano
fluidsynth.init('/usr/share/sounds/sf2/FluidR3_GM.sf2', "alsa")


procesovideo=Proceso_video()

# Constantes proyecto
PATH_TECLADO_VIRTUAL = "teclado.png"        # Path imagen del teclado que se muestra en la pantalla.
PATH_TECLADO_COLORES = "coloresTeclado.png" # Path imagen del teclado con el que segmenta las notas correspondientes.
BASE_KEY_KEYBOARD = 39                      # Número de tecla base a partir de la que se mapea las notas del teclado.

manos = False
fr = 0
if __name__ == "__main__":
    # EJECUCIÓN PRINCIṔAL
    notes = []                      # Inicializa un vector vacio de notas.
    is_update_notes_array = False   # Array de notas no actualizado
    base_keyboard = 0               #
    base_keyboard = Proceso_nota.update_notes_array(base_keyboard, BASE_KEY_KEYBOARD, PATH_TECLADO_COLORES, is_update_notes_array)
    is_update_notes_array = True


    #DECLARACION DE CLASES
    ventana = ventana_Piano()   #Declaración clase que controla la interfaz de pygame y eventos de mouse
    ventana._init_()            #Inicialización

    k = Kinect()
    k.start()
    time.sleep(2)

    # Variable para guardar el ángulo de inclinación anterior.
    ang_prev = ventana.tilt_kinect


    # Si se presiona el botón de iniciar:
    ############################################################################################################################
    # CICLO PRINCIPAL
    while ventana.is_running:

        # DETECTAR EVENTOS DE LA PANTALLA
        eventos_ = ventana.get_eventos()


        if ventana.is_take_video:
            #Verificar si hay un cambio en el ángulo del Kinect
            if ventana.tilt_kinect != ang_prev:
                k.setAngle(ventana.tilt_kinect)
                ang_prev = ventana.tilt_kinect
            #Adquirir el valor para realizar la umbralización.
            procesovideo.THRESHOLD_VALUE = ventana.umbral
            procesovideo.DEPTH_VALUE = ventana.depth
            
            # ADQUISICIÓN DE IMAGENES
            video = k.getVideo()
            depthFrame = k.getDepth()

            if not(video is None) and not(depthFrame is None):
                videoFrame = procesovideo.add_image(video, PATH_TECLADO_VIRTUAL)

                # PROCESAMIENTO
                posx, posy, notes = procesovideo.procesa_video(depthFrame, videoFrame)

                # NOTAS
                NotasPres = notes

                fluidsynth.play_NoteContainer(NotasPres)
                ventana.notes = NotasPres
                ventana.mano_state = procesovideo.estado_list
                ventana.mano_posx = posx
                ventana.mano_posy = posy

                # RENDERIZACIÓN DE RESULTADOS
                if ventana.is_show_pasos:
                    # La imagen procesada se guarda en la pantalla sin escalar, por lo que el
                    # segundo atributo es False y el tamaño es []
                    ventana.image_kinect = ventana.cvimage_a_pygame(videoFrame, False, [])
                    # se ingresan en forma de arreglo los pasos a mostrar en la interfaz.
                    Pasos_proceso = [depthFrame,
                                     procesovideo.medianDepth.astype(np.uint8),
                                     procesovideo.manosconcentroide.astype(np.uint8),
                                     procesovideo.manosconcontornos.astype(np.uint8)]
                    ventana.pasos_procesa = Pasos_proceso
                else:
                    # Se ingresa la imagen escalada al tamaño designado en pantalla, para mostrar la imagen procesada
                    ventana.image_kinect = ventana.cvimage_a_pygame(videoFrame, True, ventana.image_size)
        
        # ACTUALIZACIÓN DE PANTALLA
        ventana.update_window()

    ventana.exit()  # Salir de la ventana
    k.terminate()   # Terminar la adquisición de imagenes.