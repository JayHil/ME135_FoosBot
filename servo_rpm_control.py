from machine import Pin,PWM, Timer
import time

p360f = PWM(Pin(14, mode=Pin.OUT))
p360f.freq(50)
angle = 0


# 0.5ms/20ms = 0.025 = 2.5% duty cycle
# 2.4ms/20ms = 0.12 = 12% duty cycle

# 0.025*1024=25.6
# 0.12*1024=122.88

target_RPM = 0

# Set up timer interrupt for encoder
encoder_ticks = 0
encoder_timer = Timer(1)
# def encoder_interrupt(timer):
#     global encoder_ticks
#     encoder_ticks += 1
# encoder_timer.init(period=10, mode=Timer.PERIODIC, callback=encoder_interrupt)

# Bound value between max and minimum
def bound(low, high, value):
    return max(low, min(high, value))

# Converts RPM input from -140 to 140 where negative is counter clockwise and vice versa
def rpm_to_duty(rpm):
    rpm = bound(-140, 140, rpm)
    if (rpm < 0):
        tControl = ((1.480 - 1.280)/(0--140))*(rpm--140)+1.280
        dutyCycle = (tControl/20) * 1024
    elif (rpm == 0):
        dutyCycle = 77
    elif (rpm > 0):
        tControl = ((1.720-1.520)/(140-0))*(rpm-0)+1.520
        dutyCycle = (tControl/20) * 1024
    print(dutyCycle)
    return int(dutyCycle)
        

while True:
    # Get target ticks per second from user input or other source
    target_RPM = int(input("Enter target RPM (-140-140): "))
    p360f.duty(rpm_to_duty(target_RPM))
    time.sleep(1)
    