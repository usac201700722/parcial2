import paho.mqtt.client as mqtt
import logging
import time
import os 
import socket
from brokerdata import * 


LOG_FILENAME = 'mqtt.log'
SALAS_FILENAME = 'salas'
USER_FILENAME = 'usuarios'
dato=b''

class configuracionesServidor(object):

    def __init__(self, filename='', qos=2):
        self.filename = filename
        self.qos = qos


    def subSalas(self):
        datos = []
        archivo = open(self.filename,'r') 
        for line in archivo:
            registro = line.split('S')
            registro[-1] = registro[-1].replace('\n', '')
            datos.append(registro) 
        archivo.close() #Cerrar el archivo al finalizar
        for i in datos:
            #print("salas/"+str(i[0])+"/S"+str(i[1]))
            #client.subscribe(("salas/"+str(i[0])+"/S"+str(i[1]), qos))
            logging.debug("salas/"+str(i[0])+"/S"+str(i[1]))
    
    def subUsuarios(self):
        datos = []
        archivo = open(self.filename,'r') #Abrir el archivo en modo de LECTURA
        for line in archivo: #Leer cada linea del archivo
            registro = line.split(',')
            registro[-1] = registro[-1].replace('\n', '')
            datos.append(registro) 
        archivo.close() #Cerrar el archivo al finalizar       
        for i in datos:
            client.subscribe(("usuarios/"+str(i[0]), self.qos))
            logging.debug("usuarios/"+str(i[0]))
    
    def subComandos(self, qos=2):
        client.subscribe("comandos/08/#",self.qos)

    def __str__(self):
        datosMQTT="Archivo de datos: "+str(self.filename)+" Qos: "+ str(self.qos)
        return datosMQTT

    def __repr__(self):
        return self.__str__

def conexionTCP(IP_ADDR,IP_ADDR_ALL,IP_PORT,BUFFER_SIZE):
    # Crea un socket TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    serverAddress = (IP_ADDR_ALL, IP_PORT) #Escucha en todas las interfaces
    print('Iniciando servidor en {}, puerto {}'.format(*serverAddress))
    sock.bind(serverAddress) #Levanta servidor con parametros especificados

    #Existe una nueva funcion en Python 3.8: socket.create_server()
    #Tiene poca documentación aún, por lo que utilizaremos socket.bind() + socket.listen()

    # Habilita la escucha del servidor en las interfaces configuradas
    sock.listen(10) #El argumento indica la cantidad de conexiones en cola

    while True:
        # Esperando conexion
        print('Esperando conexion remota')
        connection, clientAddress = sock.accept()
        try:
            print('Conexion establecida desde', clientAddress)

            # Se envia informacion en bloques de BUFFER_SIZE bytes
            # y se espera respuesta de vuelta
            while True:
                data = connection.recv(BUFFER_SIZE)
                print('Recibido: {!r}'.format(data))
                if data: #Si se reciben datos (o sea, no ha finalizado la transmision del cliente)
                    print('Enviando data de vuelta al cliente')
                    connection.sendall(data)
                else:
                    print('Transmision finalizada desde el cliente ', clientAddress)
                    break
        
        except KeyboardInterrupt:
            sock.close()


#Configuracion inicial de logging
logging.basicConfig(
    level = logging.DEBUG, 
    format = '[%(levelname)s] (%(threadName)-10s) %(message)s'
    )

#Callback que se ejecuta cuando nos conectamos al broker
def on_connect(client, userdata, rc):
    logging.info("Conectado al broker")	#No es necesario, pero pueees

#Callback que se ejecuta cuando llega un mensaje al topic suscrito
def on_message(client, userdata, msg):	#msg contiene el topic y la info que llego
    #Se muestra en pantalla informacion que ha llegado
    global dato 
    dato = msg.payload
    logging.info("Ha llegado el mensaje al topic: " + str(msg.topic)) #de donde vino el mss
    logging.info("El contenido del mensaje es: " + str(dato.decode('utf-8')))#que vino en el mss
    
def on_publish(client, userdata, mid): 
    publishText = "Publicacion satisfactoria"
    logging.debug(publishText)


client = mqtt.Client(clean_session=True) #Nueva instancia de cliente, iniciamos con una #sesion limpia
client.on_connect = on_connect #Se configura la funcion "Handler" cuando suceda la conexion
client.on_message = on_message #Se configura la funcion "Handler" que se activa al llegar un mensaje a un topic subscrito
client.on_publish = on_publish
client.username_pw_set(MQTT_USER, MQTT_PASS) #Credenciales requeridas por el broker, user y pass
client.connect(host=MQTT_HOST, port = MQTT_PORT) #Conectar al servidor remoto
#host es la ip, y el puerto el puerto xD si lo dejamos vacio lo conecta al 1883 (CREO)

#*********** Suscripciones del servidor ******************
qos = 1
user = configuracionesServidor(USER_FILENAME,qos)
user.subUsuarios()
salas = configuracionesServidor(SALAS_FILENAME,qos)
salas.subSalas()
comandos = configuracionesServidor(qos)
comandos.subComandos(qos)
#***********************************************************

#Iniciamos el thread (implementado en paho-mqtt) para estar atentos a mensajes en los topics subscritos
client.loop_start()	#COn esto hacemos que las sub funcionen
#El thread de MQTT queda en el fondo, mientras en el main loop hacemos otra cosa

try:
    while True:
        #logging.debug("El dato ingresado es: "+str(dato.decode('utf-8')))
        comandoIn=dato.decode('utf-8')
        
        if comandoIn=="archivo":
            print("**************************************")
            conexionTCP(IP_ADDR,IP_ADDR_ALL,IP_PORT,BUFFER_SIZE)
            

        time.sleep(10)	


except KeyboardInterrupt:
    logging.warning("Desconectando del broker...")

finally:
    client.loop_stop() #Se mata el hilo que verifica los topics en el fondo
    client.disconnect() #Se desconecta del broker
    logging.info("Desconectado del broker. Saliendo...")