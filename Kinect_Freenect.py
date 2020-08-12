#! -*- coding:utf8 -*-

import freenect
import numpy as np
import random
import cv2
import time
from threading import Thread
from collections import deque

class Kinect(Thread):
    grados = deque()
    depth = deque()
    video = deque()
    """ Clase base para extender una aplicacion freenect"""
    def __init__(self, *largs, **kwargs):
        super(Kinect, self).__init__(*largs, **kwargs)
        self.quit = False
        self.daemon = True          # Permite la ejecución del hilo sin afectar el hilo principal del programa.
        self.grados.appendleft(0)
        self.keep_running = True
        self.change_ang = False

    def run(self):
        """ Instrucción ejecutada por el Thread.
            Parametros: None
            Return: None
        """
        while not self.quit:
            # Ejecuta un ciclo de ejecución del Kinect.
            freenect.runloop(
                    depth=self.display_depth, # Control de imagen de profundidad.
                    video=self.display_rgb,   # Control de imagen de color.
                    body=self.main            # Control de motor y led Kinect.
                )

    def main(self, dev, ctx):
        """ Instrucción ejecutada por el Thread.
            Parametros:
                dev --> Puntero del dispositivo de cámara identificado como Kinect.
                ctx --> Puntero del Kinect.
            Return: None
        """
        if self.change_ang:
            # Si la colección tiene más de un elemento:
            if len(self.grados)>1:
                # Pide al Kinect moverse al ángulo ángulo y eliminarlo de la colección.
                freenect.set_tilt_degs(dev, self.grados.pop())
            else:
                # Pide al Kinect moverse a la única posición de la colección.
                freenect.set_tilt_degs(dev, self.grados[-1])
            # Establece que el ángulo ya fué cambiado.
            self.change_ang = False

    def display_depth(self, dev, data, timestamp):
        """ Control de los datos de profundidad.
            Parametros:
                dev       --> Puntero del dispositivo de cámara identificado como Kinect.
                data      --> Frame de profundidad , formato uint16.
                timestamp --> Información de tiempo de adquisición.
            Return: None
        """        
        # Se adquire el frame de profundidad.
        profundidad = data
        # Si el dato es nulo:
        if profundidad is None:
            # Esperar un segundo para adquirir de nuevo los datos.
            time.sleep(0.5)
            pass
        else:
            # Se agrega a la colección el frame obtenido.
            self.depth.appendleft(np.fliplr(profundidad))


    def display_rgb(self, dev, data, timestamp):
        """ Control de los datos de profundidad.
            Parametros:
                dev       --> Puntero del dispositivo de cámara identificado como Kinect.
                data      --> Frame de color RGB , formato uint8.
                timestamp --> Información de tiempo de adquisición.
            Return: None
        """
        try:
            # Se adquiere el frame de color.
            video = data
            # Si el dato es nulo o vacío:
            if data is None:
                # Esperar un segundo para adquirir de nuevo los datos.
                time.sleep(0.5)
                pass
            else:
                # Se agrega a la colección el nuevo frame de color.
                self.video.appendleft(np.fliplr(video[:, :, ::-1]))  # Cambia de BGR a RGB
        except AttributeError:
            print('dato no tomado')
    def getVideo(self):
        """ Obtención del último frame de Video guardado en la colección de Video.
            Parametros: None
            Return: 
                Último frame de video en la colección.
        """
        try:
            return self.video.pop()
        except:
            print ('No hay datos')

    def getDepth(self):
        """ Obtención del último frame de Profundidad guardado en la colección de Profundidad.
            Parametros: None
            Return: 
                Último frame de profundidad en la colección.
        """
        try:
            return self.depth.pop()
        except:
            print ('No hay datos')

    def setAngle(self, value):
        """ Establece el ángulo de inclinación que se desea mover el motor del Kinect
            Parametros: 
                value --> Valor de ángulo deseado.
            Return: 
                None
        """
        # Se establece que el ángulo ha cambiado.
        self.change_ang = True
        # Se agrega a la colección el nuevo ángulo.
        self.grados.appendleft(value)

    def terminate(self):
        """ Termina el Thread creado.
            Parametros: 
                None
            Return: 
                None
        """
        self.keep_running = False   # Se pone en False la condición de ejecutar el ciclo del Kinect.
        freenect.Kill               # Se desactiva el dispositivo Kinect inicializado.
        self.quit = True            # Se termina la ejecución del Thread.
