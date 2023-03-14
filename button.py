from machine import Pin

KEY=Pin(21,Pin.IN,Pin.PULL_DOWN) # 设置为输入引脚，并且设置默认引脚点位为0

print(KEY.value())