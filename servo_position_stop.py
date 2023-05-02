from machine import Pin,PWM
import time

p360f = PWM(Pin(14, mode=Pin.OUT))
p360f.freq(50)

# 0.5ms/20ms = 0.025 = 2.5% duty cycle
# 2.4ms/20ms = 0.12 = 12% duty cycle

# 0.025*1024=25.6
# 0.12*1024=122.88

while True:
    p360f.duty(int(0.077*1024))
    