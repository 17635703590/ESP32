from machine import Pin, Timer
import time
hall_sensor_pin = Pin(23, Pin.IN, Pin.PULL_UP)  # 根据硬件连接修改引脚

pulse_count = 0  # 初始化脉冲计数
last_pulse_time = 0  # 初始化上一个脉冲时间
wheel_circumference = 2.07  # 以米为单位的轮胎直径（假设直径为2.07米）

riding_distance = 0  # 初始化骑行距离
riding_time = 0  # 初始化骑行时间
speed = 0
def count_pulse(timer):
    global pulse_count, last_pulse_time, riding_distance
    pulse_count += 1
    last_pulse_time = time.ticks_ms()

hall_sensor_pin.irq(trigger=Pin.IRQ_FALLING, handler=count_pulse)  # 配置中断处理函数

# 创建一个定时器，用于定期计算速度、骑行时间和骑行距离
def calculate_data(timer):
    global pulse_count, last_pulse_time, riding_distance, riding_time, speed
    current_time = time.ticks_ms()
    elapsed_time = time.ticks_diff(current_time, last_pulse_time)

    if pulse_count > 0:
        riding_time += elapsed_time / 1000  # 换算为秒
        riding_distance += (pulse_count / 2) * wheel_circumference  # 每个脉冲代表半个轮胎周长
        speed = (pulse_count / elapsed_time) * 1000  # 转换单位为秒
        pulse_count = 0  # 重置脉冲计数

        # 输出骑行时间和骑行距离（精确到十位）
        #print("速度 (m/s): {:.1f}".format(speed))
        #print("骑行时间 (s): {:.1f}".format(riding_time))
        #print("骑行距离 (m): {:.1f}".format(riding_distance))
        file = open ("data.txt", "w")
        file.write("速度 (m/s): {:.1f} \n".format(speed))
        file.write("骑行时间 (s): {:.1f} \n".format(riding_time))
        file.write("骑行距离 (m): {:.1f}".format(riding_distance))
        file.close()
        
def Start():
    data_timer = Timer(-1)
    data_timer.init(period=1000, mode=Timer.PERIODIC, callback=calculate_data)  # 每秒计算一次数据
    try:
        while True:
            pass
    except KeyboardInterrupt:
        data_timer.deinit()  # 停止数据计算定时器
#重置
def Reset():
    global pulse_count, riding_distance, riding_time
    pulse_count = 0
    riding_distance = 0
    riding_time = 0
    file = open ("data.txt", "w")
    file.write("速度 (m/s): {:.1f} \n".format(0))
    file.write("骑行时间 (s): {:.1f} \n".format(0))
    file.write("骑行距离 (m): {:.1f}".format(0))
    file.close()
    return '骑行数据已重置'

if __name__ == '__main__':
    Start()
