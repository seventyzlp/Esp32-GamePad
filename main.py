import time, network, ntptime

print("同步前本地时间：%s" %str(time.localtime()))
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('iPhone14 pro max', '115115115')
while not wlan.isconnected():
    pass

ntptime.NTP_DELTA = ntptime.NTP_DELTA - 8*60*60 # UTC+8 
ntptime.host = 'ntp.ntsc.ac.cn'
ntptime.settime()
print("同步后本地时间：%s" %str(time.localtime()))
