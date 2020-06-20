SALAS_FILENAME = 'salas'
def fileRead(fileName = 'salas'):
    datos = []
    archivo = open(fileName,'r') #Abrir el archivo en modo de LECTURA
    for line in archivo: #Leer cada linea del archivo
        registro = line.split('S')
        registro[-1] = registro[-1].replace('\n', '')
        datos.append(registro) 
    archivo.close() #Cerrar el archivo al finalizar
    print(len(datos))
    for i in datos:
        print("salas/"+str(i[0])+"/S"+str(i[1]))

fileRead(SALAS_FILENAME)