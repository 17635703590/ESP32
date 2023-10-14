import socket
import time
import urandom
 
from machine import Pin
p2 = Pin(2, Pin.OUT)
 
SERVER_IP = "192.168.1.102"
SERVER_PORT = 32666
BUFFER_SIZE = 1024
 
#定义接收服务器指令的回调函数，下面是打开ESP8266上led灯的指令
def receiveHandler(sck: socket.socket()):
    cmdInfo = sck.recv(BUFFER_SIZE).decode("utf8")
    if cmdInfo == "on":
        p2.off()
        print("Led Opened!")
    if cmdInfo == "off":
        p2.on()
        print("Led Closed!")
 
#套接字基本设置及连接操作
def doConnect(serverIp, serverPort):
    #创建套接字，socket.AF_INET表示服务器之间网络通信；socket.SOCK_STREAM表示流式socket,for TCP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address = (serverIp, serverPort)
    #下面是socket对象绑定了一个回调函数，这样不会因为套接字阻塞（如，未收到服务器端信息）而影响micropython主进程
    #当接收到指令后，则打断现行的操作，运行回调函数，之后自动回到之前的代码，下面的20不要更改
    s.setsockopt(socket.SOL_SOCKET, 20, receiveHandler)
    try:
        #说明，如果下面的连接失败，正常会有报错，这里用pass指令掉过报错
        s.connect(address)
        print("Server connected!")
    except:
        pass
    return s
 
def main(serverIp = SERVER_IP, serverPort = SERVER_PORT):
 
    sConnect = doConnect(serverIp, serverPort)
    while True:
        try:
            #下述指令表示生产一个8位数的整数，这个8位指的是2进制的8个位，最大为255
            #下面代码是每隔2秒往服务器端发送一个255以内的随机数
            randomNum = str(urandom.getrandbits(8))
            sConnect.send(randomNum+"\n")
            print("随机数: ", randomNum)
            time.sleep_ms(2000)
 
        #下面代码用于处理发送失败事件，正常产生失败原因有服务器掉线、发送数据错误等原因
        #但是下面仅用于显示报错原因和进行服务器断线重连
        except Exception as err:
            print("Excepetion Info: ", err)
            print("Re connect...")
            time.sleep_ms(3000)
            sConnect = doConnect(serverIp, serverPort)