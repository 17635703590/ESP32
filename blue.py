import machine
import time

# 初始化UART1
uart = machine.UART(1, baudrate=9600, tx=17, rx=16)  # 使用引脚17作为TX和引脚16作为RX，波特率为9600

# 发送数据
data_to_send = "Hello, ESP32!\n"
uart.write(data_to_send)

# 接收数据
received_data = b''  # 初始化一个字节串来存储接收的数据
timeout = time.ticks_ms() + 5000  # 设置一个5秒的超时时间

while time.ticks_ms() < timeout:
    if uart.any():  # 如果有可用数据
        received_byte = uart.read(1)  # 读取一个字节
        received_data += received_byte

# 打印接收到的数据
print("Received data:", received_data.decode('utf-8'))
