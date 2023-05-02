import time
from machine import Pin, Timer, PWM

# Set up pins for servo and encoder
servo_pin = Pin(4)
encoder_pin = Pin(5)

# Set up PWM for servo
servo_pwm = PWM(servo_pin, freq=50)

# Set up timer interrupt for encoder
encoder_ticks = 0
encoder_timer = Timer(1)
def encoder_interrupt(timer):
    global encoder_ticks
    encoder_ticks += 1
encoder_timer.init(period=10, mode=Timer.PERIODIC, callback=encoder_interrupt)

# Set up variables for PID control
target_ticks_per_second = 0
prev_error = 0
integral = 0
Kp = 1
Ki = 0.1
Kd = 0.01

# Set up timer interrupt for PID control
servo_ticks_per_second = 0
pid_timer = Timer(0)
def pid_interrupt(timer):
    global servo_ticks_per_second, target_ticks_per_second, prev_error, integral
    error = target_ticks_per_second - servo_ticks_per_second
    integral += error
    derivative = error - prev_error
    output = Kp * error + Ki * integral + Kd * derivative
    prev_error = error
    servo_ticks_per_second += output
    if servo_ticks_per_second < 0:
        servo_ticks_per_second = 0
    if servo_ticks_per_second > 64:
        servo_ticks_per_second = 64
    duty_cycle = int(servo_ticks_per_second / 64 * 1023)
    servo_pwm.duty(duty_cycle)
pid_timer.init(period=100, mode=Timer.PERIODIC, callback=pid_interrupt)

# Main loop
while True:
    # Get target ticks per second from user input or other source
    target_ticks_per_second = int(input("Enter target ticks per second (0-64): "))
    time.sleep(1)
