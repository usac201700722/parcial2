import binascii
FTR = b'\x03'
dest = input("Ingrese el user o sala: ")
fSize = int(input("Ingrese un entero: "))    #Este numero puede ser chiquito o grande 
                    #porque depende del tamaño del archivo
dest=dest.encode()
fSize=str(fSize)
fSize=fSize.encode()
mensaje = FTR+ dest+fSize
print(mensaje)  #Date cuenta que mensaje es de tipo byte
