import paho.mqtt.client as paho
import logging
import time
import socket
import random
import os
import sys       #Requerido para salir (sys.exit())
import threading #Concurrencia con hilos
from brokerdata import * #Informacion de la conexion

'''
Ejemplo de cliente MQTT: gateway de red de sensores
'''
USER_FILENAME ='usuario'
SALAS_FILENAME = 'salas'

class configuracionCLiente(object):
    def __init__(self,filename='', qos=2):
        self.filename = filename
        self.qos = qos

    def subComandos(self):
        datos = []
        archivo = open(self.filename,'r') #Abrir el archivo en modo de LECTURA
        for line in archivo: #Leer cada linea del archivo
            registro = line.split('\n')
            datos.append(registro) 
        archivo.close() #Cerrar el archivo al finalizar
        for i in datos:
            client.subscribe(("comandos/"+str(i[0]), self.qos))
            logging.debug("comandos/"+str(i[0]))
    
    def subUsuarios(self):
        datos = []
        archivo = open(self.filename,'r') #Abrir el archivo en modo de LECTURA
        for line in archivo: #Leer cada linea del archivo
            registro = line.split('\n')
            datos.append(registro) 
        archivo.close() #Cerrar el archivo al finalizar
        for i in datos:
            client.subscribe(("usuarios/"+str(i[0]), self.qos))
            logging.debug("usuarios/"+str(i[0]))

    def subSalas(self):
        datos = []
        archivo = open(self.filename,'r') #Abrir el archivo en modo de LECTURA
        for line in archivo: #Leer cada linea del archivo
            registro = line.split('S')
            registro[-1] = registro[-1].replace('\n', '')
            datos.append(registro) 
        archivo.close() #Cerrar el archivo al finalizar
        for i in datos:
            client.subscribe(("salas/"+str(i[0])+"/S"+str(i[1]), self.qos))
            logging.debug("salas/"+str(i[0])+"/S"+str(i[1]))

    def __str__(self):
        datosMQTT="Archivo de datos: "+str(self.filename)+" qos: "+ str(self.qos)
        return datosMQTT

    def __repr__(self):
        return self.__str__

class hilos(object):
    def __init__(self,tiempo):
        self.tiempo=tiempo
        self.hiloGrabar=threading.Thread(name = 'loquesea',
                        target = hilos.grabarAudio,
                        args = (self,self.tiempo),
                        daemon = True
                        )
    def grabarAudio(self,tiempo=0):
        grabador = str("arecord -d "+str(tiempo)+" -f U8 -r 8000 ultimoAudio.wav")
        logging.info('Comenzando la grabación')
        os.system(grabador)
        logging.info('***Grabación finalizada***')

#Configuracion inicial de logging
logging.basicConfig(
    level = logging.DEBUG, 
    format = '[%(levelname)s] (%(processName)-10s) %(message)s'
    )



#Tiempo de espera entre lectura y envio de dato 
DEFAULT_DELAY = 2 

#Handler en caso suceda la conexion con el broker MQTT
def on_connect(client, userdata, flags, rc): 
    connectionText = "CONNACK recibido del broker con codigo: " + str(rc)
    logging.info(connectionText)

#Handler en caso se publique satisfactoriamente en el broker MQTT
def on_publish(client, userdata, mid): 
    publishText = "Publicacion satisfactoria"
    logging.debug(publishText)

#Callback que se ejecuta cuando llega un mensaje al topic suscrito
def on_message(client, userdata, msg):	#msg contiene el topic y la info que llego
    #Se muestra en pantalla informacion que ha llegado
    logging.info("Ha llegado el mensaje al topic: " + str(msg.topic)) #de donde vino el mss
    logging.info("El contenido del mensaje es: " + str(msg.payload))#que vino en el mss

def conexionTCP(server_ip,server_port, buffer_size):
    # Se crea socket TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Se conecta al puerto donde el servidor se encuentra a la escucha
    server_address = (server_ip, server_port)
    print('Conectando a {} en el puerto {}'.format(*server_address))
    sock.connect(server_address)

    try:
        # Se envia un texto codificado EN BINARIO
        message = b'Este es un mensaje fue enviado por TCP'
        print('\n\nEnviando el siguiente texto:  {!s}'.format(message))
        sock.sendall(message) #Se envia utilizando "socket.sendall" 

    finally:
        print('\n\nConexion finalizada con el servidor')
        sock.close()


logging.info("Cliente MQTT con paho-mqtt") #Mensaje en consola

'''
Config. inicial del cliente MQTT
'''
client = paho.Client(clean_session=True) #Nueva instancia de cliente
client.on_connect = on_connect #Se configura la funcion "Handler" cuando suceda la conexion
client.on_publish = on_publish #Se configura la funcion "Handler" que se activa al publicar algo
client.on_message = on_message
client.username_pw_set(MQTT_USER, MQTT_PASS) #Credenciales requeridas por el broker
client.connect(host=MQTT_HOST, port = MQTT_PORT) #Conectar al servidor remoto


#************* Suscripciones del servidor *********
comandos= configuracionCLiente(USER_FILENAME,2)
comandos.subComandos()
usuarios = configuracionCLiente(USER_FILENAME,2)
usuarios.subUsuarios()
salas = configuracionCLiente(SALAS_FILENAME,2)
salas.subSalas()
#***************************************************

def publishData(topicRoot, topicName, value, qos = 0, retain = False):
    topic = topicRoot + "/" + topicName
    client.publish(topic, value, qos, retain)
	#Publica de forma ordenada los valores del topic

print('''
Menú:
1- Enviar texto
    a. Enviar a usuario --> PRESIONE "1a"
    b. Enviar a sala    --> PRESIONE "1b"
2- Enviar mensaje de voz
    a. Enviar a usuario --> PRESIONE "2a"
        i. Duración (Segundos)
    b. Enviar a sala    --> PRESIONE "2b"
        i. Duración (Segundos)
''')

client.loop_start()
#Loop principal: leer los datos de los sensores y enviarlos al broker en los topics adecuados cada cierto tiempo
try:
    while True:       
        comando = input("Ingrese el comando: ")

        if comando == "1a":
            topic_send = input("Ingrese el numero de usuario: ")
            mensaje = input("Texto a enviar: ")
            #mensaje=mensaje.encode()
            client.publish("usuarios/"+str(topic_send),mensaje,1,False)
        elif comando == "1b":
            topic_send = input("Ingrese el nombre de la sala: ")
            mensaje = input("Texto a enviar: ")
            client.publish("usuarios/"+str(topic_send),mensaje,1,False)
        elif comando == "2a":
            topic_send = input("Ingrese el usuario al que desea enviar el audio: ")
            duracion = int(input("Ingrese la duracion del audio en segundos: "))
            grabar = hilos(duracion)
            grabar.hiloGrabar.start()
        elif comando == "2b":
            conexionTCP(SERVER_IP,SERVER_PORT,BUFFER_SIZE)
        else:
            logging.error("El comando ingresado es incorrecto, recuerde ver las instrucciones")
               
        logging.debug("Los datos han sido enviados al broker")            
        #Retardo hasta la proxima publicacion de info
        time.sleep(DEFAULT_DELAY)

except KeyboardInterrupt:
    logging.warning("Desconectando del broker MQTT...")

finally:
    client.loop_stop()
    client.disconnect()
    logging.info("Se ha desconectado del broker. Saliendo...")