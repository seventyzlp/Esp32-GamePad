# Esp32-GamePad

基于ESP32 - MicroPython 的开源游戏机 --开发手记

## 一、驱动点亮OLED屏幕

```py
from ssd1306 import SSD1306_I2C
from font import Font

display= SSD1306_I2C(128, 64, i2c)
f=Font(display)

def set_time():
    f.text(str(time.localtime()[0])+'y',0,0,10)
    f.text(str(time.localtime()[1])+'m',45,0,10)
    f.text(str(time.localtime()[2])+'d',70,0,10)
    f.text(str(time.localtime()[3])+'h',0,20,10)
    f.text(str(time.localtime()[4])+'m',45,20,10)
    f.text(str(time.localtime()[5])+'s',70,20,10)
    f.show()
```
笔者使用都显示屏是4针脚的SSD1306驱动的主控芯片，因此就在[Github](https://github.com/maysrp/ssd1306_font)中找到并使用了开源的驱动库。对于库函数的具体说明可以参考库内的说明文档，这里就简单说明使用到的库函数的用法。

首先，需要对显示模块进行定义，``SSD1306_I2C(128, 64, i2c)``即为定义显示屏长边为128个像素点，短边为64个像素点，使用i2c方式通信，按照显示模块的说明文档设置就好。如果设置不正确，会出现字符被拉长或是被挤压的情况，不会出现留白。

在设置完文字后，需要使用``f.show()``来使屏幕显示内容，然而，此时屏幕的显示**应该**重叠的，show()命令并不会刷新屏幕，所以可以使用``display.init_display()``来刷新显示器设置。当然，能否有更加方便的重载显示器内容的方式还存疑，需要进一步探究。

## 二、时间显示模块与NTP对时

```py
import ntptime, network, time

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
```

ntp的起始时间是2010年，所以需要增加一段偏移量，单位是秒```ntptime.NTP_DELTA = 3155644800```。

``ntp.host = 'ntp.ntsc.ac.cn'``是设置ntp对时服务器，一般选取国内的ntp服务器比较容易对时成功。不设置的话，会有默认的对时地址，但是对时成功率不高。

## 三、WI-FI连接与天气信息获取

```py
import urequests
import ujson
import network

wlan = network.WLAN(network.STA_IF)
# 设置Wi-Fi模块为STA模式，即为连接外部Wi-Fi
wlan.active(True)       
# 启用Wi-Fi

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

# 天气显示模块
def weather():
    f.text('T:'+str(j['result']['realtime']['temperature'])+'`',0,0,10)
    f.text('H:'+str(j['result']['realtime']['humidity'])+'%',70,0,10)
    f.text('P:'+str(j['result']['realtime']['pressure'])+'Pa',0,20,10)
    f.text('W:'+str(j['result']['realtime']['wind']['speed'])+'km/h',0,40,10)
    f.show()
```

```wlan = network.WLAN(network.STA_IF)```在STA模式之外，还有AP模式，因该还有并行模式。

可以用```wlan.isconnected()```函数来判断Wi-Fi是否连接，返回值为bool。在此之外，```wlan.ifconfig()```来获取Wi-Fi连接成功后的信息，获取到的值为数组。

在连接Wi-Fi之后，就可以使用外部API，例如天气信息API。想要调用API，需要使用```urequests.get()```函数，来获取返回的json文件。获取到的文件会被保存为*result.text*，用```ujson.load()```来读取json文件，并把内容保存到变量中。json文件的读取方式有点像字典索引，即为``变量[索引]``，在多层叠加的情况下可以一直套，例如``j['result']['realtime']['wind']['speed']``为获取风速。具体json文件内容的含义以及索引路径可以参考API的官方文档或者使用说明。

## 四、按钮的控制

按钮的本质是引脚电位的变化，因此，想要实现按钮的功能主要就在于对于引脚的定义。
```py
from machine import Pin

Button_next = Pin(21,Pin.IN,Pin.PULL_UP) # 设置21引脚为输入引脚
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
```
其中，``Pin(21,Pin.IN,Pin.PULL_UP)``是关键，这里定义了IO21引脚为输入引脚，并且输入引脚的接法为上拉点位的接法，21引脚为高电位。

要想获取引脚的点位情况，可以使用``value()``函数，高电位输出1，低点位输出0。也是使用value()函数输出值的变化，来判断按钮是否有人按下。