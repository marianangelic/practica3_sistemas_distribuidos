## importacion de librerias ##

# para manejo de las conexiones

import socket
# para manejo de los hilos
import threading
# para la codificacion y decodificacion de mensajes
import base64
import hashlib
# para el manejo del tiempo
import time
import sys

## declaracion de variables globales ##

# direccion ip del servidor
HOST = '10.2.126.2'
# puerto tcp
PORT_TCP = 19876  
# puerto udp
PORT_UDP = 15601 
BUFFER_UDP = 1024
BUFFER_TCP = 1024
# username
USER = ''
# socket tcp
s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
checksum = None


## hilo para el manejo de la conexion udp ##
def thread_udp(name):
    global s_tcp
    global checksum
    #se utilizara el socket tcp para realizar la validacion del checksum posteriormente
    #print ("abriendo el puerto de escucha udp...")
    # abrir escucha de udp con el tamaño del buffer
    s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_udp.bind(('10.2.126.19', PORT_UDP))
    print("en espera de mensaje...")
    msgFromServer = s_udp.recvfrom(BUFFER_UDP)
    s_udp.close() #se cierra la conexion udp ya que no es necesaria
    # se recibe el mensaje y se decodifica
    #print("mensaje recibido, decodificando...")
    base64_message = (msgFromServer[0])
    message_bytes = base64.b64decode(base64_message)
    message = message_bytes.decode('utf-8')
    print(message)
    # calculamos el checksum
    checksum = hashlib.md5(message_bytes)    
    

# conexion principal
if __name__ == "__main__":
    USER = input('ingrese el usuario:')
    HOST = input('ingrese direccion del servidor:')
    PORT_TCP = int(input('ingrese puerto tcp:'))
    PORT_UDP = int(input('ingrese puerto udp:'))
    # conectamos el puerto TCP
    s_tcp.connect((HOST, PORT_TCP))
    # validacion de usuario
    print ('validando usuario ' + USER +'...')
    command = 'helloiam '+ USER
    s_tcp.sendall(command.encode())
    data = (s_tcp.recv(BUFFER_TCP)).decode('utf-8')
    print(data)
    # solicitamos el tamano del mensaje
    s_tcp.sendall(b'msglen')
    #print('solicitando msglen...')
    data = s_tcp.recv(BUFFER_TCP)
    d = data.decode('utf-8')
    d = d.replace('ok ','')
    BUFFER_UDP = int(d) * 2
    #print('msglen: ', d)
    # abrir puerto udp para recibir el mensaje
    #print("creando hilo para udp")
    x = threading.Thread(target=thread_udp, args=(1,))
    #print("corriendo hilo...")
    x.start()
    # solicito el mensaje


    intento = 1

    #mientras tengas intentos disponibles
    while intento <= 3:
        if checksum is not None:
            break
        print('solicitando mensaje, intento ', intento)
        command = 'givememsg '+ str(PORT_UDP)
        s_tcp.sendall(command.encode())

        #se espera durante 20 segundos por una respuesta
        timer = 0
        while checksum is None and timer <= 20:
            time.sleep(1)
            timer+=1
        intento+=1

    #si los intentos fueron sobre pasados    
    if intento > 3:
        print ('conexion fallida')
        s_tcp.sendall(b'bye')
    

    # recibo la respuesta del servidor tcp de cuando solicitamos el envio de mensaje
    data = s_tcp.recv(BUFFER_TCP)

    
    # chequeamos el checksum con la conexion tcp
    print('checking msg...')
    command = 'chkmsg '+ checksum.hexdigest()
    s_tcp.sendall(command.encode())
    data = s_tcp.recv(BUFFER_TCP)
    print('Msg checked! ', data.decode('utf-8'))
    # cerramos la conexion tcp
    command = 'givememsg '+ str(PORT_UDP)
    s_tcp.sendall(command.encode())
    # Receive response
    data = s_tcp.recv(BUFFER_TCP)
    s_tcp.close()
    #print("socket finalizado")
    #print('el servidor ha enviado el mensaje: ', data.decode('utf-8'))
   
