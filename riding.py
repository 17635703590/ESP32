#ESP32上运行相关代码
import network
import socket
import time
from machine import Pin # 导入Pin模块
from utime import sleep_ms #导入延时函数
from machine import Pin, ADC
from mqttclient import ConnectMqqtt

import _thread
import sys
import machine
from machine import UART,Pin
import utime




# 初始化
uart = UART(2, baudrate=9600, rx=16,tx=17,timeout=10)
count = 1
lock = _thread.allocate_lock()#线程锁
SSID="TP-LINK_DC0B"
PASSWORD="123qwe456asd"

port=1000
wlan=None
listenSocket=None


def connectWifi(ssid,passwd):
    global wlan
    wlan=network.WLAN(network.STA_IF)     
    wlan.active(True)              
    wlan.disconnect()               
    wlan.connect(ssid,passwd)         
    while(wlan.ifconfig()[0]=='0.0.0.0'):
        time.sleep(1)
    return True

def connectTCP():
    lock.acquire()
    try:
        connectWifi(SSID,PASSWORD)
        ip=wlan.ifconfig()[0]
        listenSocket = socket.socket()          
        listenSocket.bind((ip,port))           
        listenSocket.listen(1)                 
        listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        print("*"*90)
        print("TCP 服务器开启, IP: %s PORT: %s"%(ip, port))
        print("*"*90)
        while True:
            print("等待消息接收 ...")
           
            conn,addr = listenSocket.accept()    
            print("连接自客户端 ...",addr)
            

            while True:
                print('==============================')
                uart.write('>>GetVal')
                utime.sleep_ms(1000)

                if uart.any():
                    bin_data = uart.readline()
 
                    print('Echo String: {}'.format(bin_data.decode()))
                print('---------------------------------------')
               
                JC = conn.send('Echo String: {}'.format(bin_data.decode()))

    except Exception as err:
        print("Excepetion Info: ", err)
        lock.release()
        if(listenSocket):
            listenSocket.close()
        wlan.disconnect()
        wlan.active(False)
        connectTCP()



if __name__ == '__main__':
    #time.sleep_ms(3000)
   
    thread_1 = _thread.start_new_thread(connectTCP, ())

