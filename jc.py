from machine import sleep, SoftI2C, Pin, Timer
from utime import ticks_diff, ticks_us
from max30102 import MAX30102, MAX30105_PULSE_AMP_MEDIUM
# ------------ 添加新代码 -----------
from hrcalc import calc_hr_and_spo2


BEATS = 0  # 存储心率
FINGER_FLAG = False  # 默认表示未检测到手指
# ------------ 添加新代码 -----------
SPO2 = 0  # 存储血氧
TEMPERATURE = 0  # 存储温度


def display_info(t):
    # 如果没有检测到手指，那么就不显示
    if FINGER_FLAG is False:
        return

    # ------------ 修改代码 -----------
    print('心率: ', BEATS, " 血氧：", SPO2, " 温度：", TEMPERATURE)


def main():
    # ------------ 修改代码 -----------
    global BEATS, FINGER_FLAG, SPO2, TEMPERATURE  # 如果需要对全局变量修改，则需要global声明
    
    # 创建I2C对象(检测MAX30102)
    i2c = SoftI2C(sda=Pin(17), scl=Pin(5	), freq=400000)  # Fast: 400kHz, slow: 100kHz

    # 创建传感器对象
    sensor = MAX30102(i2c=i2c)

    # 检测是否有传感器
    if sensor.i2c_address not in i2c.scan():
        print("没有找到传感器")
        return
    elif not (sensor.check_part_id()):
        # 检查传感器是否兼容
        print("检测到的I2C设备不是MAX30102或者MAX30105")
        return
    else:
        print("传感器已识别到")

    # 配置
    sensor.setup_sensor()
    sensor.set_sample_rate(400)
    sensor.set_fifo_average(8)
    sensor.set_active_leds_amplitude(MAX30105_PULSE_AMP_MEDIUM)

    t_start = ticks_us()  # Starting time of the acquisition

    MAX_HISTORY = 32
    history = []
    beats_history = []
    beat = False
    # ------------ 添加新代码 -----------
    red_list = []
    ir_list = []

    while True:
        sensor.check()
        if sensor.available():
            # FIFO 先进先出，从队列中取数据。都是整形int
            red_reading = sensor.pop_red_from_storage()
            ir_reading = sensor.pop_ir_from_storage()
            
            if red_reading < 1000:
                print('No finger')
                FINGER_FLAG = False  # 表示没有放手指
                continue
            else:
                FINGER_FLAG = True  # 表示手指已放

            # 计算心率
            history.append(red_reading)
            
            # 为了防止列表过大，这里取列表的后32个元素
            history = history[-MAX_HISTORY:]
            
            # 提取必要数据
            minima, maxima = min(history), max(history)
            threshold_on = (minima + maxima * 3) // 4   # 3/4
            threshold_off = (minima + maxima) // 2      # 1/2
            
            if not beat and red_reading > threshold_on:
                beat = True                    
                t_us = ticks_diff(ticks_us(), t_start)
                t_s = t_us/1000000
                f = 1/t_s
                bpm = f * 60
                if bpm < 500:
                    t_start = ticks_us()
                    beats_history.append(bpm)                    
                    beats_history = beats_history[-MAX_HISTORY:]   # 只保留最大30个元素数据
                    BEATS = round(sum(beats_history)/len(beats_history), 2)  # 四舍五入
            if beat and red_reading < threshold_off:
                beat = False
                
            # ------------ 添加新代码 -----------
            # 计算血氧
            red_list.append(red_reading)
            ir_list.append(ir_reading)
            # 最多 只保留最新的100个
            red_list = red_list[-100:]
            ir_list = ir_list[-100:]
            # 计算血氧值
            if len(red_list) == 100 and len(ir_list) == 100:
                hr, hrb, sp, spb = calc_hr_and_spo2(red_list, ir_list)
                if hrb is True and spb is True:
                    if sp != -999:
                        SPO2 = int(sp)

            # ------------ 添加新代码 -----------
            # 计算温度
            TEMPERATURE = sensor.read_temperature()


if __name__ == '__main__':
    # 1. 创建定时器
    timer = Timer(1)
    # 2. 设置定时器的回调函数，每1秒钟调用1次display_info函数（用来显示数据）
    timer.init(period=1000, mode=Timer.PERIODIC, callback=display_info)
    # 3. 调用主程序，用来检测数据
    main()
