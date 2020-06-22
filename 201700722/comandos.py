#La clase comandosCLiente sirve para realizar las tramas de la negociacion
#entre cliente y servidor, a pesar que se llame comandosCLiente, no esta limitado
#solo a cliente, sino que el servidor tambien podra hacer uso de esta clase.
class comandosCliente(object):
    def __init__(self,Dest):
        self.Dest=Dest
        self.SEP= b'$'

    def fileTransfer(self, File_size=0):
        FTR=b'\x03'
        Destino = self.Dest
        Destino=Destino.encode()      
        tamArchivo=str(File_size)
        tamArchivo=tamArchivo.encode()
        trama= FTR+self.SEP+Destino+self.SEP+tamArchivo
        return trama
    def alive(self):
        ALIVE=b'\x04'
        Destino = self.Dest
        Destino=Destino.encode()
        trama= ALIVE+self.SEP+Destino
        return trama
    def fileReceive(self, File_size=0):
        FRR=b'\x02'
        Destino = self.Dest
        Destino=Destino.encode()
        tamArchivo=str(File_size)
        tamArchivo=tamArchivo.encode()
        trama = FRR+self.SEP+Destino+self.SEP+tamArchivo
        return trama
    def ack(self):
        ACK=b'\x05'
        Destino = self.Dest
        Destino=Destino.encode()
        trama= ACK+self.SEP+Destino
        return trama

    def OK(self):
        OKEY=b'\x06'
        Destino = self.Dest
        Destino=Destino.encode()
        trama= OKEY+self.SEP+Destino
        return trama

    def NO(self):
        NEL=b'\x07'
        Destino = self.Dest
        Destino=Destino.encode()
        trama= NEL+self.SEP+Destino
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
        self.comando= str(comando)
    def __str__(self):
        return str(self.separa())
    def __repr__(self): 
        return self.__str__()
    def __len__(self):
        return len(self.comando)

    def separa(self):
        lista = []
        separados=[]
        lista = self.comando.split("b'\\x")
        union = str(lista[1])
        separados = union.split("$")
        return separados
#el \x03 no lo toma en cuenta solo el 3 como al final el comando es ese, o si es 4 y asi
#sucesivamente entonces ya lo deja separado, luego toma el carnet o la sala y deja de
#de ultimo el tamaño del archivo, no importando la cantidad de digitos
# y hay ifs porque uno es si es el cliente osea el carnet o es una sala

