from machine import I2C, Pin,RTC,WDT,reset
from ssd1306 import SSD1306_I2C
from font import Font
import time
import ntptime
import network # 时钟
import os
import urequests
import ujson

i2c = I2C(scl=Pin(0), sda=Pin(1))
display= SSD1306_I2C(128, 64, i2c)
f=Font(display)
# 为开发板创建网络，模式为STA模式
wlan = network.WLAN(network.STA_IF) # create station interface
# 激活STA
wlan.active(True)       # activate the interface
# ESP32开发板扫描网络     

Button_next = Pin(21,Pin.IN,Pin.PULL_UP) # 设置21引脚为输入引脚

def sync_ntp():
    ntptime.NTP_DELTA = 3155644800   # 可选 UTC+8偏移时间（秒），不设置就是UTC0
    ntptime.host = 'ntp.ntsc.ac.cn'  # 可选，ntp服务器，默认是"pool.ntp.org"ntp1.aliyun.com
    try:
        display.init_display() #理论上这个是重置界面刷新
        ntptime.settime()   # 修改设备时间,到这就已经设置好了
        f.text("sync time",0,0,10)
        f.text("success",0,20,10)
        f.show()
    except:
        f.text("sync time",0,0,10)
        f.text("fail",0,20,10)
        f.show()

def set_time():
    f.text(str(time.localtime()[0])+'y',0,0,10)
    f.text(str(time.localtime()[1])+'m',45,0,10)
    f.text(str(time.localtime()[2])+'d',70,0,10)
    f.text(str(time.localtime()[3])+'h',0,20,10)
    f.text(str(time.localtime()[4])+'m',45,20,10)
    f.text(str(time.localtime()[5])+'s',70,20,10)
    f.show()

if not wlan.isconnected():
    display.init_display()
    f.text("connecting network..",0,0,10)
    print('connecting to network...')
    wlan.connect('iPhone14 pro max','115115115') #输入WIFI账号密码
    while not wlan.isconnected():
        if time.time()-start_time > 15 :
            f.text("WIFI timeout!",0,0,10)
            print('WIFI Connected Timeout!')
            break
if wlan.isconnected():
    print('connected!')
    print('network information:', wlan.ifconfig())  


result = urequests.get('https://api.caiyunapp.com/v2.5/faiP7e6spPqeTSgn/116.2377,39.5427/realtime.json') # 彩云天气API
j = ujson.loads(result.text)

# f.text('Beijng',25,5)   # 天气显示模块
def weather():
    f.text('T:'+str(j['result']['realtime']['temperature'])+'`',0,0,10)
    f.text('H:'+str(j['result']['realtime']['humidity'])+'%',70,0,10)
    f.text('P:'+str(j['result']['realtime']['pressure'])+'Pa',0,20,10)
    f.text('W:'+str(j['result']['realtime']['wind']['speed'])+'km/h',0,40,10)
    f.show()

sync_ntp()
#set_time()
time.sleep(1)
display.init_display()
flag = True

while(1):
    key1 = Button_next.value()
    time.sleep_ms(1)
    key2 = Button_next.value()
    if key1 != key2:
         if flag:
             flag = False
             display.init_display()
         else:
             flag = True
             display.init_display()

    #print(flag)
    
    if flag: # 输入高电位
        set_time()
    #time.sleep(1)
    if not flag:
        weather()
    



         