import paho.mqtt.client as paho #ARMCH libreria para configuracion de paho mqtt
import logging                  #ARMCH libreria para reemplazar el print
import time                     #ARMCH libreria para realizar pausas time.sleep
import os           #ARMCH esta libreria nos sirve para utilizar comandos de bash en python 
import sys          # ARMCH Requerido para salir (sys.exit())
import threading    #ARMCH Concurrencia con hilos
from brokerdata import * #ARMCH archcivo importado para credenciales y constantes 

'''
Comentario y clase hecho por: SALU
Config. inicial del cliente MQTT
Esta clase se encarga de realizar todas las configuraciones
para un cliente MQTT, cada uno de los métodos son handlres
o callbacks que se utilizan para la interaccion con los clientes
MQTT utilizando la libreria paho.mqtt.client, al darle ctr+click
a cada funcion nos abre la libreria y podamos leer la configuracion
de cada una de ellas.
'''
class MQTTconfig(paho.Client):
    def on_connect(self, client, userdata, flags, rc):
        #SALU Handler en caso suceda la conexion con el broker MQTT
        connectionText = "CONNACK recibido del broker con codigo: " + str(rc)
        logging.debug(connectionText)
    def on_publish(self, client, userdata, mid): 
        #SALU Handler en caso se publique satisfactoriamente en el broker MQTT
        publishText = "Publicacion satisfactoria"
        logging.debug(publishText)
    def on_message(self, client, userdata, msg):	
        #SALU Callback que se ejecuta cuando llega un mensaje al topic suscrito
        #SALU msg contiene el topic y la info que llego
        #SALU Se muestra en pantalla informacion que ha llegado
        print(lista1)
        topic= msg.topic
        if topic in lista1: #SALU si el topic tiene algun valor de lista1 guarda el audio
            archivo = open('audioEntrante.wav','wb')       
            archivo.write(msg.payload) 
            archivo.close()
            logging.debug('Se guardo la nota de voz satisfactoriamente')
            
            #SALU Activo el hilo que reproduce el audio
            hilo = hiloAudio(topic)
            hilo.hiloRecibidor.start()
        else:               #Si el topic no es de audio muestra el mensaje de forma amigable
            mensaje_chat=msg.payload
            logging.info("**************************************************************************")
            logging.info("Ha llegado el mensaje al topic: " + str(msg.topic)) #de donde vino el mss
            logging.info("El contenido del mensaje es: " + str(mensaje_chat.decode('utf-8')))#que vino en el mss
            logging.info("**************************************************************************")
            
    def on_subscribe(self, client, obj,mid, qos):
        #SALU Handler en caso se suscriba satisfactoriamente en el broker MQTT
        logging.debug("Suscripcion satisfactoria")

    def run(self):
        #SALU este metodo inicializa la conexion MQTT con las credenciales del broker
        self.username_pw_set(MQTT_USER, MQTT_PASS)
        self.connect(host=MQTT_HOST, port = MQTT_PORT)        
        rc = 0
        while rc==0:
            rc = self.loop_start()
        return rc

'''
Comentario y clase hecho por: HANC
La clase configuracionCLiente se encarga de realizar las suscripciones
recursivas del cliente MQTT, de esta manera las suscripciones se basan en los
archivos de texto plano "usuarios" y "salas".
'''
class configuracionCLiente(object):
    #HANC constructor de la clase configuracionCLiente
    def __init__(self,filename='', qos=2):
        self.filename = filename
        self.qos = qos
    #HANC metodo que suscribe al cliente para recibir audios de usuarios
    def subAudios(self):
        datos = []
        archivo = open(self.filename,'r') #HANC Abrir el archivo en modo de LECTURA
        for line in archivo: #HANC Leer cada linea del archivo
            registro = line.split('\n')
            datos.append(registro) 
        archivo.close() #HANC Cerrar el archivo al finalizar
        audios=[]
        for i in datos:
            client.subscribe(("audios/08/"+str(i[0]), self.qos))
            audios.append("audios/08/"+str(i[0]))
        return audios

    #HANC metodo que suscribe al cliente para recibir audios de salas
    def subAudiosSalas(self):
        datos = []
        archivo = open(self.filename,'r') #HANC Abrir el archivo en modo de LECTURA
        for line in archivo: #HANC Leer cada linea del archivo
            registro = line.split('S')
            registro[-1] = registro[-1].replace('\n', '')
            datos.append(registro) 
        archivo.close() #HANC Cerrar el archivo al finalizar
        audios=[]
        for i in datos:
            client.subscribe(("audios/"+str(i[0])+"/S"+str(i[1]), self.qos))
            audios.append("audios/"+str(i[0])+"/S"+str(i[1]))
        return audios
    
    #HANC metodo que suscribe al cliente a su mismo usuario
    def subUsuarios(self):
        datos = []
        archivo = open(self.filename,'r') #HANC Abrir el archivo en modo de LECTURA
        for line in archivo: #HANC Leer cada linea del archivo
            registro = line.split('\n')
            datos.append(registro) 
        archivo.close() #HANC Cerrar el archivo al finalizar
        users=[]
        for i in datos:
            client.subscribe(("usuarios/08/"+str(i[0]), self.qos))
            users.append("usuarios/08/"+str(i[0]))
        return users

    #HANC metodo que suscribe al cliente a su misma salas
    def subSalas(self):
        datos = []
        archivo = open(self.filename,'r') #HANC Abrir el archivo en modo de LECTURA
        for line in archivo: #HANC Leer cada linea del archivo
            registro = line.split('S')
            registro[-1] = registro[-1].replace('\n', '')
            datos.append(registro) 
        archivo.close() #HANC Cerrar el archivo al finalizar
        sal=[]
        for i in datos:
            client.subscribe(("salas/"+str(i[0])+"/S"+str(i[1]), self.qos))
            sal.append("salas/"+str(i[0])+"/S"+str(i[1]))
        return sal
    
    def __str__(self):
        datosMQTT="Archivo de datos: "+str(self.filename)+" qos: "+ str(self.qos)
        return datosMQTT

    def __repr__(self):
        return self.__str__

'''
Comentario y clase hecho por: ARMCH 
la clase comando usuarios sirve para controlar las acciones que realice el usuario el parametro de entrada 
de la clase indica la accion que se va a realizar de acuerdo al menu principal, de esta manera el codigo queda 
mas limpio y ordenado
'''

class comandosUsuario(object):
    #ARMCH este es el constructor de la clase comandos usuario
    def __init__(self, comando =""):
        self.comando=comando
    #ARMCH metodo que maneja cada una de las acciones que se van a realizar por mqtt
    def accion(self):
        if self.comando == "1a":    #ARMCH aqui envia mensajes a usuarios
            topic_send = input("Ingrese el numero de usuario (Ej: '201700376', sin comillas): ")
            mensaje = input("Texto a enviar: ")
            client.publish("usuarios/08/"+str(topic_send),mensaje,1,False)
        elif self.comando == "1b":  #ARMCH aqui envia mensajes a salas
            topic_send = input("Ingrese el nombre de la sala (Ej: 'S01', sin comillas y S Mayúscula): ")
            mensaje = input("Texto a enviar: ")
            client.publish("salas/08/"+str(topic_send),mensaje,1,False)
        elif self.comando == "2a":  #ARMCH aqui envia audio a usuarios
            topic_send = input("Ingrese el usuario al que desea enviar el audio (Ej: '201700376', sin comillas): ")
            duracion = int(input("Ingrese la duracion del audio en segundos: (Max. 30 seg)"))
            if duracion<=30:    #ARMCH si el audio es menor que 30 lo envia
                grabador = str("arecord -d "+str(duracion)+" -f U8 -r 8000 ultimoAudio.wav")
                logging.info('Comenzando la grabación')
                os.system(grabador)
                logging.info('***Grabación finalizada***')
                #**********Envio de audio por mqtt******************
                enviarAudio(topic_send)
            else:   #ARMCH de lo contrario da un mensaje de error
                logging.error("¡La duracion debe ser menor a 30 seg!")
       
        elif self.comando == "2b":  #ARMCH aqui envia audios a salas
            topic_send = input("Ingrese la sala a la que desea enviar el audio (Ej: 'S01', sin comillas y S Mayúscula): ")
            duracion = int(input("Ingrese la duracion del audio en segundos: (Max. 30 seg)"))
            if duracion<=30:    #ARMCH si el audio es menor que 30s lo envia
                grabador = str("arecord -d "+str(duracion)+" -f U8 -r 8000 ultimoAudio.wav")
                logging.info('Comenzando la grabación')
                os.system(grabador)
                logging.info('***Grabación finalizada***')
                #************** HILO **************************
                enviarAudio(topic_send)
            else:   #ARMCH si el audio es mayor da un mensaje de error
                logging.error("¡La duracion debe ser menor a 30 seg!")
                
        elif self.comando in ["exit","EXIT"]:   #ARMCH sale del programa
            sys.exit(0)

        else:
            logging.error("El comando ingresado es incorrecto, recuerde ver las instrucciones")
        #ARMCH hace una peque;a pausa antes de volver a pedir otro comando
        logging.debug("Los datos han sido enviados al broker")            
        time.sleep(DEFAULT_DELAY)

'''
 comentario y metodo hecho por: SALU
 La funcion reproducirAudio se encarga de reproducir el archivo de audio .wav
 que se almacena en la carpeta del cliente cuando llega un archivo al topic 
 audios/08/# (En el codigo NO se utilizo el wildcat #, ver clase configuracionCLiente())
'''   
#SALU La clase hiloAudio se encarga de reproducir el audio entrante en un hilo
#paralelo al programa principal.
class hiloAudio(object):
    def __init__(self,mensaje):
        self.mensaje=mensaje
        self.hiloRecibidor=threading.Thread(name = 'Guardar nota de voz',
                        target = hiloAudio.reproducirAudio,
                        args = (self,self.mensaje),
                        daemon = False
                        )
    def reproducirAudio(self, mensaje):
        logging.debug(mensaje)       
        logging.info("Reproduciendo nota de voz...")
        os.system('aplay audioEntrante.wav')

'''
comentario y método hecho por: SALU
La funcion enviarAudio sirve para enviar el audio por medio de MQTT utilizando la 
client.publish y enviando el archivo de audio como bytes
'''
def enviarAudio(topic_send):
    archivo = open('ultimoAudio.wav','rb')
    logging.debug("Preparando para enviar...")
    l=archivo.read(os.stat('ultimoAudio.wav').st_size)          
    logging.debug("Enviando...")
    client.publish("audios/08/"+str(topic_send),l,2,False)
    archivo.close()
    logging.debug("Envio Completado satisfactoriamente")

#SALU Configuracion inicial de logging
logging.basicConfig(
    level = logging.INFO, #SALU solo muestra los mensajes de nivel INFO para arriba
    format = '[%(levelname)s] (%(processName)-10s) %(message)s'
    ) 

logging.info("Bienvenidos a WhatsappBro") #SALI Mensaje en consola

#SALU Iniciamos la configuracion del cliente MQTT
client = MQTTconfig(clean_session=True)
rc = client.run()   #SALU Corre la congiduracion 
   
#************* Suscripciones del cliente *********
#ARMCH aqui mandamos a llamar a la clase configuraciones clientes para
#suscribir al usuario de forma recursiva
audios= configuracionCLiente(USER_FILENAME,2)
logging.debug(audios.subAudios())
lista1=audios.subAudios()
audiosSalas=configuracionCLiente(SALAS_FILENAME,2)
logging.debug(audiosSalas.subAudiosSalas())
lista1.extend(audiosSalas.subAudiosSalas())
usuarios = configuracionCLiente(USER_FILENAME,2)
logging.debug(usuarios.subUsuarios())
salas = configuracionCLiente(SALAS_FILENAME,2)
logging.debug(salas.subSalas())
#***************************************************

client.loop_start()  
#Loop principal: 
#SALU leer los comandos que ingrese el usuario
try:
    while True:
        #ARMCH menu principal
        print('''
        -------------------------------------------------
        |Menú:                                          |
        |1- Enviar texto                                |
        |    a. Enviar a usuario --> PRESIONE "1a"      |
        |    b. Enviar a sala    --> PRESIONE "1b"      |
        |2- Enviar mensaje de voz                       |
        |    a. Enviar a usuario --> PRESIONE "2a"      |
        |        i. Duración (Segundos)                 |
        |    b. Enviar a sala    --> PRESIONE "2b"      |
        |        i. Duración (Segundos)                 |
        |3. Salir del sistema --> PRESIONE "exit/EXIT"  |
        --------------------------------------------------
        ''') 
        dato_usuario = input("Ingrese el comando: ")    #ARMCH el usuario ingresa un comando
        com=comandosUsuario(dato_usuario)               #ARMCH instancia del objeto instancia usuario
        com.accion()                                    #ARMCH ejecuta las acciones mqtt

except KeyboardInterrupt:
    #SALU cuando se ejecuta esta interrupcion el programa lanza un mensaje de 
    #alerta e inmediatamente cierra el programa desconectando al cliente del broker
    logging.warning("Desconectando del broker MQTT...")

finally:
    client.loop_stop()          #SALU: Detiene la configuracion del cliente MQTT
    client.disconnect()         #SALU: Desconecta al cliente MQTT del broker
    logging.info("Se ha desconectado del broker. Saliendo...")  #SALU: Mensaje de salida del sistema