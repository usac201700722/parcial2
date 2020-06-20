import paho.mqtt.client as paho
import logging
import time
import random
from brokerdata import * #Informacion de la conexion

'''
Ejemplo de cliente MQTT: gateway de red de sensores
'''
USER_FILENAME ='usuario'
SALAS_FILENAME = 'salas'

class configuracionCLiente(object):
    def __init__(self,MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASS):
        self.MQTT_HOST = MQTT_HOST
        self.MQTT_PORT = MQTT_PORT
        self.MQTT_USER = MQTT_USER
        self.MQTT_PASS = MQTT_PASS
    def subComandos(self,filename='usuario',qos=2):
        datos = []
        archivo = open(filename,'r') #Abrir el archivo en modo de LECTURA
        for line in archivo: #Leer cada linea del archivo
            registro = line
            datos.append(registro) 
        archivo.close() #Cerrar el archivo al finalizar
        for i in datos:
            client.subscribe(("comandos/"+str(i), qos))
            logging.debug("comandos/"+str(i))
    
    def subUsuarios(self,filename='usuario',qos=2):
        datos = []
        archivo = open(filename,'r') #Abrir el archivo en modo de LECTURA
        for line in archivo: #Leer cada linea del archivo
            registro = line
            datos.append(registro) 
        archivo.close() #Cerrar el archivo al finalizar
        for i in datos:
            client.subscribe(("usuarios/"+str(i), qos))
            logging.debug("usuarios/"+str(i))

    def subSalas(self, filename='salas', qos=2):
        datos = []
        archivo = open(filename,'r') #Abrir el archivo en modo de LECTURA
        for line in archivo: #Leer cada linea del archivo
            registro = line.split('S')
            registro[-1] = registro[-1].replace('\n', '')
            datos.append(registro) 
        archivo.close() #Cerrar el archivo al finalizar
        for i in datos:
            client.subscribe(("salas/"+str(i[0])+"/S"+str(i[1]), qos))
            logging.debug("salas/"+str(i[0])+"/S"+str(i[1]))

    def __str__(self):
        datosMQTT="HOST: "+str(self.MQTT_HOST)+"PUERTO: "+ str(self.MQTT_PORT)
        return datosMQTT

    def __repr__(self):
        return self.__str__

#Configuracion inicial de logging
logging.basicConfig(
    level = logging.INFO, 
    format = '[%(levelname)s] (%(processName)-10s) %(message)s'
    )

#Nombres de Topics de ejemplo
SENSORES    = 'sensores'
PRESION_A   = 'atm'
HUMEDAD     = 'hum'
TEMPERATURA = 'temp'

#Cantidad de sensores de ejemplo que se simulan
CNT_SENSORES = 10

#Tiempo de espera entre lectura y envio de dato de sensores a broker (en segundos)
DEFAULT_DELAY = 60 #1 minuto


#Clase que simula la adquisición de los datos de los sensores de los nodos remotos de la red
class RemoteSensors(object):
    def __init__(self, sensorCount):
        self.sensorCount = sensorCount
    
    def getHumedad(self, sensorIndex): #Simulamos la data generada por un conjunto de sensores DHT-22
        return random.randrange(40, 100, 2)

    def getTemperatura(self, sensorIndex): #Simulamos la data generada por un conjunto de sensores DS18S20
        return random.randrange(15, 40, 1)

    def getPresionA(self, sensorIndex): #Simulamos la data generada por un conjunto de sensores BMP280
        return random.randrange(700, 1014, 1) 

    def getSensorTypes(self):
        return 3 #Devuelve la cantidad de tipos de sensores que hay instalados en la red de sensores

    def getSensorCount(self): #Devuelve la cantidad de sensores (por cada tipo) en la red
        return self.sensorCount




#Handler en caso suceda la conexion con el broker MQTT
def on_connect(client, userdata, flags, rc): 
    connectionText = "CONNACK recibido del broker con codigo: " + str(rc)
    logging.info(connectionText)

#Handler en caso se publique satisfactoriamente en el broker MQTT
def on_publish(client, userdata, mid): 
    publishText = "Publicacion satisfactoria"
    logging.debug(publishText)


logging.info("Cliente MQTT con paho-mqtt") #Mensaje en consola


'''
Config. inicial del cliente MQTT
'''
client = paho.Client(clean_session=True) #Nueva instancia de cliente
client.on_connect = on_connect #Se configura la funcion "Handler" cuando suceda la conexion
client.on_publish = on_publish #Se configura la funcion "Handler" que se activa al publicar algo
client.username_pw_set(MQTT_USER, MQTT_PASS) #Credenciales requeridas por el broker
client.connect(host=MQTT_HOST, port = MQTT_PORT) #Conectar al servidor remoto

#Mensaje de prueba MQTT en el topic "test"
client.publish("test", "Mensaje inicial", qos = 0, retain = False)


def publishData(topicRoot, topicName, value, qos = 0, retain = False):
    topic = topicRoot + "/" + topicName
    client.publish(topic, value, qos, retain)
	#Publica de forma ordenada los valores del topic


#Instancia de la clase que simula la lectura de datos de sensores remotos
sensores = RemoteSensors(CNT_SENSORES) 

#Loop principal: leer los datos de los sensores y enviarlos al broker en los topics adecuados cada cierto tiempo
try:
    while True:


        #Para temperatura
        for i in range(sensores.getSensorCount()):
            publishData(SENSORES, (str(i) + "/" + TEMPERATURA), sensores.getTemperatura(i))
            
        
        #Para humedad
        for i in range(sensores.getSensorCount()):
            publishData(SENSORES, (str(i) + "/" + HUMEDAD), sensores.getHumedad(i))

        #Para presion
        for i in range(sensores.getSensorCount()):
            publishData(SENSORES, (str(i) + "/" + PRESION_A), sensores.getPresionA(i))


        logging.info("Los datos han sido enviados al broker")            

        #Retardo hasta la proxima publicacion de info
        time.sleep(DEFAULT_DELAY)

except KeyboardInterrupt:
    logging.warning("Desconectando del broker MQTT...")

finally:
    client.disconnect()
    logging.info("Se ha desconectado del broker. Saliendo...")