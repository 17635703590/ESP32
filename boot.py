# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
import network
import socket
import time
from machine import Pin # 导入Pin模块
from utime import sleep_ms #导入延时函数
from machine import Pin, ADC
from mqttclient import ConnectMqqtt
import he
import _thread
import machine
lock = _thread.allocate_lock()#线程锁

SSID="J1CGK7"
PASSWORD="12345678"
#ip =  '192.168.3.3'
port=10000
wlan=None
listenSocket=None

# 全局变量用于存储当前连接的客户端
client_conn = None
client_addr = None

#继电器
p22 = Pin(22, Pin.IN)
def led(control_cmd):
    LED = Pin(22,Pin.OUT)
    if control_cmd == "open":
        LED.value(1)  # 点亮LED
    elif control_cmd == "close":
        LED.value(0)  # 熄灭LED
    elif control_cmd == "flicker":
        for i in range(3):
            LED.value(0)  # 点亮LED
            sleep_ms(300)
            LED.value(1)  # 熄灭LED
            sleep_ms(400)
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
    global client_conn, client_addr
    lock.acquire()
    try:
        connectWifi(SSID,PASSWORD)
        ip=wlan.ifconfig()[0]
        listenSocket = socket.socket()     #创建套接字        
        listenSocket.bind((ip,port))            #绑定地址和端口号
        listenSocket.listen(1)                   #监听套接字, 最多允许一个连接
        listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)     #设置套接字
        print("*"*90)
        print("TCP 服务器开启, IP: %s PORT: %s"%(ip, port))
        print("*"*90)
        while True:
            print("等待消息接收 ...")
            conn,addr = listenSocket.accept()    #接收连接请求，返回收发数据的套接字对象和客户端地址
            #客户端
            client_conn = conn
            client_addr = addr
            print("连接自客户端 ...",client_addr)
            mqtt_client = ConnectMqqtt()
            JC = client_conn.send('MQTT_CLIENT........')
            while True:
                data = client_conn.recv(1024)
                if(len(data) == 0): #判断客户端是否断开连接
                    print("断开连接 ......")
                    client_conn.close()
                    break
                message_content  = data.decode()

                if(message_content == "open"):
                    led(message_content)
                    print("\033[0;36;32m接收消息内容: [%s]\033[0m"%message_content)
                    ret = client_conn.send('open')
                if(message_content == "close"):
                    led(message_content)
                    print("\033[0;36;32m接收消息内容: [%s]\033[0m"%message_content)
                    ret = client_conn.send('close')
                if(message_content == "flicker"):
                    led(message_content)
                    print("\033[0;36;32m接收消息内容: [%s]\033[0m"%message_content)
                    ret = client_conn.send('flicker')
                if(message_content == "0"):
                    he.Reset()
                    ret = client_conn.send('ResetData')
                if(message_content == "2"):
                    mqtt_client.publish("sf001_ctrl", "sf001_ctrl_down", retain=True)
                    ret = client_conn.send('brake-down')
                if(message_content == "3"):
                    mqtt_client.publish("sf001_ctrl", "sf001_ctrl_up", retain=True)
                    ret = client_conn.send('brake-up')
                if(message_content == "4"):
                    SpeedStart()
    except Exception as err:
        print("Excepetion Info: ", err)
        lock.release()
        if(listenSocket):
            listenSocket.close()
        wlan.disconnect()
        wlan.active(False)
        connectTCP()
        
        
def SpeedStart():
    global client_conn, client_addr
    f = open("data.txt", "r")
    line = f.read()                             #去掉每行头尾空白  
    print (line)
    client_conn.send(line)
    f.close()
    
    
    
    
def HrStart():
    he.Start()
if __name__ == '__main__':
    #time.sleep_ms(3000)
    #多线程    
    thread_1 = _thread.start_new_thread(connectTCP, ())
    #启动传感器
    thread_2 = _thread.start_new_thread(HrStart, ())