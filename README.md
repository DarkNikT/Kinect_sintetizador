# KINECT SINTETIZADOR

Proyecto de visión por computador en la asignatura de visión por computador. Se requiere de:
  - Sensor Kinect XBOX 360 V1
  - Computador Ubuntu
  - Python 2.7
  - OpenCV

# Instalación dependencias
Se acualiza el repositorio de Ubuntu
```sh
sudo apt-get update
sudo apt-get upgrade
```

Posteriormente, instalar las siguientes dependencias:
- Para ubuntu 10.10
    ``` sh
    sudo apt-get install cmake libglut3-dev pkg-config build-essential libxmu-dev libxi-dev libusb-1.0-0-dev
    ```
- For Ubuntu 13.04, use this instead (replaced libglut3 with freeglut3):
    ```
    sudo apt-get install cmake freeglut3-dev pkg-config build-essential libxmu-dev libxi-dev libusb-1.0-0-dev
    ```
### Libfreenect
 
Para instalar la librería libfreenect con la cual se puede interactuar con el sensor Kinect, se realizan los siguientes pasos encontrados en el repositorio de Github .
```
git clone https://github.com/OpenKinect/libfreenect
cd libfreenect
mkdir build
cd build
cmake -L .. 
make
cmake --build .        
sudo make install
sudo ldconfig /usr/local/lib64/
```
Después, para que el Kinect sea reconocido sin necesidad de superusuario.
```
sudo adduser $USER video 
sudo adduser $USER plugdev 
```
Modificación de reglas del controlador, ir a:
```
sudo nano /etc/udev/rules.d/51-kinect.rules 
```
Y copiar y pegar el siguiente texto:
```
# ATTR{product}=="Xbox NUI Motor"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02b0", MODE="0666"
# ATTR{product}=="Xbox NUI Audio"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02ad", MODE="0666"
# ATTR{product}=="Xbox NUI Camera"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02ae", MODE="0666"
# ATTR{product}=="Xbox NUI Motor"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02c2", MODE="0666"
# ATTR{product}=="Xbox NUI Motor"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02be", MODE="0666"
# ATTR{product}=="Xbox NUI Motor"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02bf", MODE="0666"
```
Posteriormente, dado que nos interesa trabajar con Python, se instala el wrapper de Python, estando en la carpeta de libfreenect:  
```
cd wrappers/python 
sudo python setup.py install
```


### Otras librerías

También se instala las librerías OpenCV, Numpy y fluidsynth. Esta última permite reproducir notas de un teclado musical. Para realizar la interfaz de la aplicación se usa Pygame.
```
Sudo apt install python-opencv
Sudo apt install python-numpy
Sudo apt install python-pygame
sudo apt-get install cython
sudo apt-get install python-dev
sudo apt-get install fluidsynth
sudo pip install mingus
```
## Descripción
La implementación realizada en Python usa OPP, mediante diferentes clases que desarrollan las etapas descritas anteriormente. En el documento anexo se menciona el diagrama de flujo del proyecto, este ciclo principal se encuentra en el archivo main.py.

Como clases principales se tienen:

 -  Kinect():
Para controlar la adquisición de la imagen de color y video de forma continua. Además, del control del ángulo de elevación. Encontrada en el archivo Kinect_Freenect.py
- Proceso_video():
Con el cual se realiza el procesamiento de los frames de profundidad para detectar la mano y demás. Encontrada en el archivo Class_Proceso.py
- Proceso_nota(): 
Con el cual se genera e identifica la nota de acuerdo a la posición. Encontrada en el archivo Class_Proceso.py
- ventana_Piano(): 
Con la cual se crea la interfaz mediante objetos y relaciones entre los objetos. Encontrada en el archivo class_app.py

## Uso

Ubiquese a una distancia de un poco más de 1 metro, ejecute el archivo *main.py* presione el botón **INICIAR**, debe aparecer la imagen si el Kinect se encuentra conectado. Con el botón **VER PASOS**.

  ![image](https://user-images.githubusercontent.com/34775257/90047332-5e63e980-dc97-11ea-86a1-85898f06be76.png)

Con los sliders de posición, distancia y umbral modifique el ángulo del Kinect y los parámetros de umbralización de la mano.

