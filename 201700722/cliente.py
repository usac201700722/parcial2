import paho.mqtt.client as paho
import logging
import time
import socket
import random
import os
import sys       #Requerido para salir (sys.exit())
import threading #Concurrencia con hilos
from brokerdata import * #Informacion de la conexion
from comandos import *

USER_FILENAME ='usuario'
SALAS_FILENAME = 'salas'
DEFAULT_DELAY = 2

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
            client.subscribe(("comandos/08/"+str(i[0]), self.qos))
            logging.debug("comandos/08/"+str(i[0]))
    
    def subUsuarios(self):
        datos = []
        archivo = open(self.filename,'r') #Abrir el archivo en modo de LECTURA
        for line in archivo: #Leer cada linea del archivo
            registro = line.split('\n')
            datos.append(registro) 
        archivo.close() #Cerrar el archivo al finalizar
        for i in datos:
            client.subscribe(("usuarios/08/"+str(i[0]), self.qos))
            logging.debug("usuarios/08/"+str(i[0]))

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
        self.hiloGrabar=threading.Thread(name = 'Nota de voz',
                        target = hilos.grabarAudio,
                        args = (self,self.tiempo),
                        daemon = True
                        )
    def grabarAudio(self,tiempo=0):
        grabador = str("arecord -d "+str(tiempo)+" -f U8 -r 8000 ultimoAudio.wav")
        logging.info('Comenzando la grabación')
        os.system(grabador)
        logging.info('***Grabación finalizada***')
 
class hiloTCP(object):
    def __init__(self, SERVER_IP):
        self.SERVER_IP=SERVER_IP
        self.hiloConexion=threading.Thread(name = 'Concexion por TCP',
                        target = hiloTCP.conexionTCP,
                        args = (self,self.SERVER_IP),
                        daemon = True
                        )

    def conexionTCP(self, SERVER_IP):
        self.SERVER_IP   = '167.71.243.238'
        SERVER_PORT = 9808
        BUFFER_SIZE = 64 * 1024
        time.sleep(5)
        # Se crea socket TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Se conecta al puerto donde el servidor se encuentra a la escucha
        server_address = (self.SERVER_IP, SERVER_PORT)
        print('Conectando a {} en el puerto {}'.format(*server_address))
        sock.connect(server_address)
        try:
            archivo = open('ultimoAudio.wav','rb')
            print("Enviando...")
            l=archivo.read(BUFFER_SIZE)
            while l:
                print("Sending...")
                sock.send(l)
                l=archivo.read(BUFFER_SIZE)
            archivo.close()
            print("Done sending")
            client.publish("comandos/08/201700722","nada",1,False)
            sock.close()
        except ConnectionRefusedError:
            logging.error("El servidor ha rechazado la conexion, intente hacerlo otra vez")


#Configuracion inicial de logging
logging.basicConfig(
    level = logging.DEBUG, 
    format = '[%(levelname)s] (%(processName)-10s) %(message)s'
    ) 

#Handler en caso suceda la conexion con el broker MQTT
def on_connect(client, userdata, flags, rc): 
    connectionText = "CONNACK recibido del broker con codigo: " + str(rc)
    logging.debug(connectionText)

#Handler en caso se publique satisfactoriamente en el broker MQTT
def on_publish(client, userdata, mid): 
    publishText = "Publicacion satisfactoria"
    logging.debug(publishText)

#Callback que se ejecuta cuando llega un mensaje al topic suscrito
def on_message(client, userdata, msg):	#msg contiene el topic y la info que llego
    #Se muestra en pantalla informacion que ha llegado
    logging.info("Ha llegado el mensaje al topic: " + str(msg.topic)) #de donde vino el mss
    logging.info("El contenido del mensaje es: " + str(msg.payload))#que vino en el mss


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


#************* Suscripciones del cliente *********
comandos= configuracionCLiente(USER_FILENAME,2)
comandos.subComandos()
usuarios = configuracionCLiente(USER_FILENAME,2)
usuarios.subUsuarios()
salas = configuracionCLiente(SALAS_FILENAME,2)
salas.subSalas()
#***************************************************

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
            topic_send = input("Ingrese el numero de usuario (Ej: '201700376', sin comillas): ")
            mensaje = input("Texto a enviar: ")
            client.publish("usuarios/08/"+str(topic_send),mensaje,1,False)
        elif comando == "1b":
            topic_send = input("Ingrese el nombre de la sala (Ej: 'S01', sin comillas y S Mayúscula): ")
            mensaje = input("Texto a enviar: ")
            client.publish("salas/08/"+str(topic_send),mensaje,1,False)
        elif comando == "2a":
            topic_send = input("Ingrese el usuario al que desea enviar el audio (Ej: '201700376', sin comillas): ")
            duracion = int(input("Ingrese la duracion del audio en segundos: (Max. 30 seg)"))
            #grabar = hilos(duracion)
            #grabar.hiloGrabar.start()
            if duracion<=30:
                grabador = str("arecord -d "+str(duracion)+" -f U8 -r 8000 ultimoAudio.wav")
                logging.info('Comenzando la grabación')
                os.system(grabador)
                logging.info('***Grabación finalizada***')
                size= os.stat('ultimoAudio.wav').st_size
                mensaje = comandosCliente(topic_send)
                mensaje.fileTransfer(size)

                client.publish("comandos/08/"+str(topic_send),"archivo",1,False)
                time.sleep(10)
                conexion= hiloTCP(SERVER_IP)
                conexion.hiloConexion.start()
            else:
                logging.error("¡La duracion debe ser menor a 30 seg!")
                break
            
        elif comando == "2b":
            topic_send = input("Ingrese el nombre de la sala (Ej: 'S01', sin comillas y S Mayúscula): ")
            client.publish("usuarios/"+str(topic_send),"archivo",1,False)
            time.sleep(DEFAULT_DELAY)
            conexion= hiloTCP(SERVER_IP)
            conexion.hiloConexion.start()
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