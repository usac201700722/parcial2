#La clase comandosCLiente sirve para realizar las tramas de la negociacion
#entre cliente y servidor, a pesar que se llame comandosCLiente, no esta limitado
#solo a cliente, sino que el servidor tambien podra hacer uso de esta clase.
class comandosCliente(object):
    def __init__(self,Dest):
        self.Dest=Dest

    def fileTransfer(self, File_size=0):
        FTR=b'\x03'
        Destino = self.Dest
        Destino=Destino.encode()      
        tamArchivo=str(File_size)
        tamArchivo=tamArchivo.encode()
        trama= FTR+Destino+tamArchivo
        return trama
    def alive(self):
        ALIVE=b'\x04'
        Destino = self.Dest
        Destino=Destino.encode()
        trama= ALIVE+Destino
        return trama
    def fileReceive(self, File_size=0):
        FRR=b'\x02'
        Destino = self.Dest
        Destino=Destino.encode()
        tamArchivo=str(File_size)
        tamArchivo=tamArchivo.encode()
        trama = FRR+Destino+tamArchivo
        return trama
    def ack(self):
        ACK=b'\x05'
        Destino = self.Dest
        Destino=Destino.encode()
        trama= ACK+Destino
        return trama

    def OK(self):
        OKEY=b'\x06'
        Destino = self.Dest
        Destino=Destino.encode()
        trama= OKEY+Destino
        return trama

    def NO(self):
        NEL=b'\x07'
        Destino = self.Dest
        Destino=Destino.encode()
        trama= NEL+Destino
        return trama

    def __str__(self):
        return "Destino: "+str(self.Dest)+" Tamaño de archivo: "#+str(self.File_size)
    def __repr__(self):
        return self.__str__

#La clase comandosServidor sirve para obtener la trama recibida del cliente y 
#separar cada dato como "comando", "ID O SALA" y/o "Tamaño del archivo",
#aunque la clase se llame comandosServidor no esta limitada solo al servidor
#Para este caso el cliente tambien hara uso de ella.
class comandosServidor(object):
    def __init__(self, comando):
        self.comando = comando

    def __len__(self):
        return len(self.comando)

    def separa(self):
        lista = []
        codi=''
        destinatario =''
        tamaño=''
        if(len(self) > 16):
            for i in range(len(self)):
                if i>3 and i<6:
                    codi = codi + self.comando[i]
                elif i>5 and i < 15:
                    destinatario = destinatario + self.comando[i]
                elif i >14 and i < len(self)-1:
                    tamaño = tamaño + self.comando[i]
            lista.append(codi)
            lista.append(destinatario)
            lista.append(tamaño)
            return lista
        else:
            for i in range(len(self)):
                if i>3 and i<6:
                    codi = codi + self.comando[i]
                elif i>5 and i < 11:
                    destinatario = destinatario + self.comando[i]
                elif i >10 and i < len(self)-1:
                    tamaño = tamaño + self.comando[i]
            lista.append(codi)
            lista.append(destinatario)
            lista.append(tamaño)
            return lista
    #def
    #sdef 
    def __str__(self):
        return str(self.separa())
    def __repr__(self): 
        return self.__str__()
#el \x03 no lo toma en cuenta solo el 3 como al final el comando es ese, o si es 4 y asi
#sucesivamente entonces ya lo deja separado, luego toma el carnet o la sala y deja de
#de ultimo el tamaño del archivo, no importando la cantidad de digitos
# y hay ifs porque uno es si es el cliente osea el carnet o es una sala

'''
user=input("Ingrese el destino: ")
fsize=int(input("Ingrese el tamaño del archivo: "))
print("*************************")
objeto= comandosCliente(user)
objeto.fileTransfer(fsize)
descomponer = comandosServidor(str(objeto.fileTransfer(fsize)))
print(descomponer.separa()[0])
print(descomponer.separa()[1])
print(descomponer.separa()[2])
print("*************************")
objeto.alive()
descomponer = comandosServidor(str(objeto.alive()))
print(descomponer.separa()[0])
print(descomponer.separa()[1])
print(descomponer.separa()[2])
print("*************************")
'''
