from umqttsimple import MQTTClient
from machine import Pin
import machine
import micropython
import time

 #MQTT
clientID = "esp32client" #连接ID
server = "39.101.179.153" #MQTT服务器地址
mqttport = 1883 #MQTT服务器端口号
userName = "admin" #MQTT登录用户名
passWord = "1qaz2wsx" #MQTT登录密码
keepAlive = 10 #心跳周期
subTopic = "sf001_ctrl" #订阅的主题
pubTopic = "sf001_ctrl_down" #发布的主题
 

 
