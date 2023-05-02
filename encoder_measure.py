import time
import machine

# Set up encoder pin and servo pin
encoder_pin = machine.Pin(32, machine.Pin.IN)
servo_pwm = machine.PWM(machine.Pin(14, machine.Pin.OUT))
servo_pwm.freq(50)

# Define the variables
dutyCycleMin = 2.9
dutyCycleMax = 97.1
unitsFullCircle = 360
Kp = 0.3;
targetAngle = 50
angle = 0

# Bound value between max and minimum
def bound(low, high, value):
    return max(low, min(high, value))

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
    return int(dutyCycle)


def encoder_interrupt(timer):
    global angle
    tHigh = machine.time_pulse_us(encoder_pin,1)
    tLow =  machine.time_pulse_us(encoder_pin,0)
    tCycle = tHigh + tLow;
    if(1000 < tCycle < 1200):
        dc = (100 * tHigh) / tCycle;
        angle = ((dc - dutyCycleMin)*360)/(dutyCycleMax - dutyCycleMin + 1)

def PID_interrupt(timer):
    global angle, targetAngle
    errorAngle = targetAngle - angle
    outputRPM = rpm_to_duty(Kp * errorAngle)
    print("Angle:", angle, "| Error Angle:", errorAngle, "| Output:", outputRPM)
    servo_pwm.duty(outputRPM)
pid_timer = machine.Timer(0)
pid_timer.init(period=100, mode=machine.Timer.PERIODIC, callback=PID_interrupt)

    
# Configure the timer
encoderTimer = machine.Timer(1)
encoderTimer.init(period=int(1/910*10000), mode=machine.Timer.PERIODIC, callback=encoder_interrupt)

# Main loop
while True:
    pass
