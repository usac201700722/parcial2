import paho.mqtt.client as mqtt
import logging
import time
import os 
from brokerData import * 


LOG_FILENAME = 'mqtt.log'
SALAS_FILENAME = 'salas'
USER_FILENAME = 'usuarios'

class configuracionesServidor(object):
    def __init__(self, MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASS):
        self.MQTT_HOST = MQTT_HOST
        self.MQTT_PORT = MQTT_PORT
        self.MQTT_USER = MQTT_USER
        self.MQTT_PASS = MQTT_PASS

    def configuracionLoggin(self):
        #Configuracion inicial de logging
        logging.basicConfig(
        level = logging.INFO, 
        format = '[%(levelname)s] (%(threadName)-10s) %(message)s'
        )
    def subSalas(self, filename='salas', qos=2):
        datos = []
        archivo = open(fileName,'r') #Abrir el archivo en modo de LECTURA
        for line in archivo: #Leer cada linea del archivo
            registro = line.split('S')
            registro[-1] = registro[-1].replace('\n', '')
            datos.append(registro) 
        archivo.close() #Cerrar el archivo al finalizar
        for i in datos:
            client.subscribe(("salas/"+str(i[0])+"/S"+str(i[1]), qos))
            #print("salas/"+str(i[0])+"/S"+str(i[1]))





configuracionesServidor.configuracionLoggin()

#Callback que se ejecuta cuando nos conectamos al broker
def on_connect(client, userdata, rc):
    logging.info("Conectado al broker")	#No es necesario, pero pueees


#Callback que se ejecuta cuando llega un mensaje al topic suscrito
def on_message(client, userdata, msg):	#msg contiene el topic y la info que llego
    #Se muestra en pantalla informacion que ha llegado
    logging.info("Ha llegado el mensaje al topic: " + str(msg.topic)) #de donde vino el mss
    logging.info("El contenido del mensaje es: " + str(msg.payload))#que vino en el mss
    
    #Y se almacena en el log 
    logCommand = 'echo "(' + str(msg.topic) + ') -> ' + str(msg.payload) + '" >> ' + LOG_FILENAME
    os.system(logCommand)
	#Al usar este comando solo funciona en linux, por los comandos que estoy usando.
	#Aqui escribo en un archivo de texto el mensaje que entra del topic


client = mqtt.Client(clean_session=True) #Nueva instancia de cliente, iniciamos con una #sesion limpia
client.on_connect = on_connect #Se configura la funcion "Handler" cuando suceda la conexion
client.on_message = on_message #Se configura la funcion "Handler" que se activa al llegar un mensaje a un topic subscrito
#CUando llega un mensaje se ejecutan estas funciones de arriba y aqui es donde se guardan
#los mensajes del topic, es como una interrupcion
client.username_pw_set(MQTT_USER, MQTT_PASS) #Credenciales requeridas por el broker, user y pass
client.connect(host=MQTT_HOST, port = MQTT_PORT) #Conectar al servidor remoto
#host es la ip, y el puerto el puerto xD si lo dejamos vacio lo conecta al 1883 (CREO)



#Nos conectaremos a distintos topics:
qos = 2

#Subscripcion simple con tupla (topic,qos)
client.subscribe(("sensores/6/hum", qos))	#Aqui nos estamos suscribiendo a 1 topic

#Subscripcion multiple con lista de tuplas
client.subscribe([("sensores/8/#", qos), ("sensores/+/atm", qos), ("sensores/0/temp", qos)])
#Enviamos una lista de tuplas para sub a varios topics a la vez

#Iniciamos el thread (implementado en paho-mqtt) para estar atentos a mensajes en los topics subscritos
client.loop_start()	#COn esto hacemos que las sub funcionen
			#Crea un ciclo infinito que crea un hilo daemon viendo si hay 
			#nuevos mensajes
#client.loop_forever()#Esta hace lo mismo,pero en el hilo principal, es una funcion
#bloqueante

#El thread de MQTT queda en el fondo, mientras en el main loop hacemos otra cosa

try:
    while True:
        logging.info("olakease")	#muestra un mensaje olakease
        time.sleep(10)	


except KeyboardInterrupt:
    logging.warning("Desconectando del broker...")

finally:
    client.loop_stop() #Se mata el hilo que verifica los topics en el fondo
    client.disconnect() #Se desconecta del broker
    logging.info("Desconectado del broker. Saliendo...")