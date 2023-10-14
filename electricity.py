from machine import UART,Pin
import utime
# 初始化
uart = UART(2, baudrate=9600, rx=16,tx=17,timeout=10)

count = 1

while True:
    print('\n\n===============CNT {}==============='.format(count))
    uart.write('>>GetVal')
    utime.sleep_ms(1000)

    if uart.any():
        bin_data = uart.readline()
        # 将字节数据转换为字符串 字节默认为UTF-8编码
        print('Echo String: {}'.format(bin_data.decode()))
    count += 1
    print('---------------------------------------')
