import paho.mqtt.client as paho
import logging
import time
import socket
import os
import sys       #Requerido para salir (sys.exit())
import threading #Concurrencia con hilos
from brokerdata import * #Informacion de la conexion

USER_FILENAME ='usuario'
SALAS_FILENAME = 'salas'
DEFAULT_DELAY = 2
reproducir = False

'''
Config. inicial del cliente MQTT
'''
class MQTTconfig(paho.Client):
    def on_connect(self, client, userdata, flags, rc):
        #Handler en caso suceda la conexion con el broker MQTT
        connectionText = "CONNACK recibido del broker con codigo: " + str(rc)
        logging.debug(connectionText)
    def on_publish(self, client, userdata, mid): 
        #Handler en caso se publique satisfactoriamente en el broker MQTT
        publishText = "Publicacion satisfactoria"
        logging.debug(publishText)
    def on_message(self, client, userdata, msg):	
        #Callback que se ejecuta cuando llega un mensaje al topic suscrito
        #msg contiene el topic y la info que llego
        #Se muestra en pantalla informacion que ha llegado
        print(lista1)
        topic= msg.topic
        if topic in lista1:
            archivo = open('audioEntrante.wav','wb')       
            archivo.write(msg.payload) 
            archivo.close()
            logging.debug('Se guardo la nota de voz satisfactoriamente')
            hilorecibidor.start()
        else:
            mensaje_chat=msg.payload
            logging.info("**************************************************************************")
            logging.info("Ha llegado el mensaje al topic: " + str(msg.topic)) #de donde vino el mss
            logging.info("El contenido del mensaje es: " + str(mensaje_chat.decode('utf-8')))#que vino en el mss
            logging.info("**************************************************************************")
            
    def on_subscribe(self, client, obj,mid, qos):
        #Handler en caso se suscriba satisfactoriamente en el broker MQTT
        logging.debug("Suscripcion satisfactoria")

    def run(self):
        self.username_pw_set(MQTT_USER, MQTT_PASS)
        self.connect(host=MQTT_HOST, port = MQTT_PORT)        
        rc = 0
        while rc==0:
            rc = self.loop_start()
        return rc

class configuracionCLiente(object):
    def __init__(self,filename='', qos=2):
        self.filename = filename
        self.qos = qos

    def subAudios(self):
        datos = []
        archivo = open(self.filename,'r') #Abrir el archivo en modo de LECTURA
        for line in archivo: #Leer cada linea del archivo
            registro = line.split('\n')
            datos.append(registro) 
        archivo.close() #Cerrar el archivo al finalizar
        audios=[]
        for i in datos:
            client.subscribe(("audios/08/"+str(i[0]), self.qos))
            audios.append("audios/08/"+str(i[0]))
        return audios

    def subAudiosSalas(self):
        datos = []
        archivo = open(self.filename,'r') #Abrir el archivo en modo de LECTURA
        for line in archivo: #Leer cada linea del archivo
            registro = line.split('S')
            registro[-1] = registro[-1].replace('\n', '')
            datos.append(registro) 
        archivo.close() #Cerrar el archivo al finalizar
        audios=[]
        for i in datos:
            client.subscribe(("audios/"+str(i[0])+"/S"+str(i[1]), self.qos))
            audios.append("audios/"+str(i[0])+"/S"+str(i[1]))
        return audios
    
    def subUsuarios(self):
        datos = []
        archivo = open(self.filename,'r') #Abrir el archivo en modo de LECTURA
        for line in archivo: #Leer cada linea del archivo
            registro = line.split('\n')
            datos.append(registro) 
        archivo.close() #Cerrar el archivo al finalizar
        users=[]
        for i in datos:
            client.subscribe(("usuarios/08/"+str(i[0]), self.qos))
            users.append("usuarios/08/"+str(i[0]))
        return users

    def subSalas(self):
        datos = []
        archivo = open(self.filename,'r') #Abrir el archivo en modo de LECTURA
        for line in archivo: #Leer cada linea del archivo
            registro = line.split('S')
            registro[-1] = registro[-1].replace('\n', '')
            datos.append(registro) 
        archivo.close() #Cerrar el archivo al finalizar
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

class comandosUsuario(object):
    def __init__(self, comando =""):
        self.comando=comando

    def accion(self):
        if self.comando == "1a":
            topic_send = input("Ingrese el numero de usuario (Ej: '201700376', sin comillas): ")
            mensaje = input("Texto a enviar: ")
            client.publish("usuarios/08/"+str(topic_send),mensaje,1,False)
        elif self.comando == "1b":
            topic_send = input("Ingrese el nombre de la sala (Ej: 'S01', sin comillas y S Mayúscula): ")
            mensaje = input("Texto a enviar: ")
            client.publish("salas/08/"+str(topic_send),mensaje,1,False)
        elif self.comando == "2a":
            topic_send = input("Ingrese el usuario al que desea enviar el audio (Ej: '201700376', sin comillas): ")
            duracion = int(input("Ingrese la duracion del audio en segundos: (Max. 30 seg)"))
            if duracion<=30:
                grabador = str("arecord -d "+str(duracion)+" -f U8 -r 8000 ultimoAudio.wav")
                logging.info('Comenzando la grabación')
                os.system(grabador)
                logging.info('***Grabación finalizada***')
                #**********Esto lo puedo meter en un hilo******************
                enviarAudio(topic_send)
            else:
                logging.error("¡La duracion debe ser menor a 30 seg!")
                #break
       
        elif self.comando == "2b":
            topic_send = input("Ingrese la sala a la que desea enviar el audio (Ej: 'S01', sin comillas y S Mayúscula): ")
            duracion = int(input("Ingrese la duracion del audio en segundos: (Max. 30 seg)"))
            if duracion<=30:
                grabador = str("arecord -d "+str(duracion)+" -f U8 -r 8000 ultimoAudio.wav")
                logging.info('Comenzando la grabación')
                os.system(grabador)
                logging.info('***Grabación finalizada***')
                #************** HILO **************************
                enviarAudio(topic_send)
            else:
                logging.error("¡La duracion debe ser menor a 30 seg!")
                #break
        elif self.comando in ["exit","EXIT"]:
            sys.exit(0)

        else:
            logging.error("El comando ingresado es incorrecto, recuerde ver las instrucciones")

        logging.debug("Los datos han sido enviados al broker")            
        time.sleep(DEFAULT_DELAY)
    
def reproducirAudio():       
    logging.info("Reproduciendo nota de voz...")
    os.system('aplay audioEntrante.wav')

def enviarAudio(topic_send):
    archivo = open('ultimoAudio.wav','rb')
    logging.debug("Preparando para enviar...")
    l=archivo.read(os.stat('ultimoAudio.wav').st_size)          
    logging.debug("Enviando...")
    client.publish("audios/08/"+str(topic_send),l,2,False)
    archivo.close()
    logging.debug("Envio Completado satisfactoriamente")


#Configuracion inicial de logging
logging.basicConfig(
    level = logging.DEBUG, 
    format = '[%(levelname)s] (%(processName)-10s) %(message)s'
    ) 


hilorecibidor=threading.Thread(name = 'Reproducir nota de voz',
        target = reproducirAudio,
        args = (),
        daemon = False
        )


logging.info("Cliente MQTT con paho-mqtt") #Mensaje en consola


client = MQTTconfig(clean_session=True)
rc = client.run()

    
#************* Suscripciones del cliente *********
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
#Loop principal: leer los datos de los sensores y enviarlos al broker en los topics adecuados cada cierto tiempo
try:
    while True:
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
        dato_usuario = input("Ingrese el comando: ")
        com=comandosUsuario(dato_usuario)
        com.accion()

        


except KeyboardInterrupt:
    logging.warning("Desconectando del broker MQTT...")

finally:
    client.loop_stop()
    client.disconnect()
    logging.info("Se ha desconectado del broker. Saliendo...")