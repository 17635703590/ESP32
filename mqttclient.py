from umqttsimple import MQTTClient


#MQTT
clientID = "esp32server" #连接ID
server = "39.101.179.153" #MQTT服务器地址
mqttport = 1883 #MQTT服务器端口号
userName = "admin" #MQTT登录用户名
passWord = "1qaz2wsx" #MQTT登录密码
keepAlive = 30 #心跳周期
subTopic = "sf001_ctrl" #订阅的主题

#订阅主题回调函数 收到消息时在此处理
def subCallBack(subTopic, msg):
    print(subTopic,msg)
    
def ConnectMqqtt():
    """连接MQTT"""
    client = MQTTClient(clientID,server,mqttport,userName,passWord,keepAlive)
    client.set_callback(subCallBack)
    client.connect()
    client.subscribe(subTopic)
    print("MQTT订阅成功，订阅topic为：",subTopic)
    
    return client
def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()
  
  
try:
    print('CONNECT...')
except OSError as e:
    print('error',e)
    restart_and_reconnect()


  
  
  
  
  
  
  
  