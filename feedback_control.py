import time
import machine

# Set up encoder pin and servo pin
encoder_pin = machine.Pin(32, machine.Pin.IN)
servo_pwm = machine.PWM(machine.Pin(14, machine.Pin.OUT))
servo_pwm.freq(50)

###################################################################################
# Define the encoder variables
###################################################################################
dcMin = 2.9 # Duty cycle for minimum servo RPM (2.9% DC = -140RPM)
dcMax = 97.1 # Duty cycle for max servo RPM (97.1% DC = 140RPM)
unitsFC = 360 # Number of units in a full circle rotation (360 to calculate angle)
dutyScale = 100 # Scale applied to duty cycle to get percent
turns = 0 # Track number of complete rotations
angle = 0.0 # Initialize angle variable
angleP = 0.0 # Initizlize previous angle variable

###################################################################################
# Define the PID control varaibles
###################################################################################
prev_error = 0 # Variable for storing previous error to calculate "derivative" term
integral = 0 # Storing integral term
Kp = 0.5
Ki = 0.001
Kd = 0.7

targetdistance = 0 # Reference distance
dPitch = 90 # Pitch diameter of rack and pinion (mm)
targetAngle = 360*targetdistance/(3.1415*dPitch) # Convert reference distance to angle

###################################################################################
# Function definitions
###################################################################################
# Bound value between max and minimum
def bound(low, high, value):
    return max(low, min(high, value))

# Convert RPM input to a duty cycle which can be written to the servo. This is done
# by mapping the RPM value to the mostly linear curve from the Parrallax Feedback 360
# Documentation
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

# Interrupt for measuring angle from encoder. This is done by measuring the high pulse
# and low pulse of the encoder output, and calculating the angle from this duty cycle using
# formulas from the documentation
def encoder_interrupt(timer):
    global angle, angleP, turns
    tHigh = machine.time_pulse_us(encoder_pin,1)
    tLow =  machine.time_pulse_us(encoder_pin,0)
    tCycle = tHigh + tLow;
    if(1000 < tCycle < 1200):
        dc = (100 * tHigh) / tCycle;
        angleRaw = (unitsFC - 1) - ((dc - dcMin) * unitsFC) / (dcMax - dcMin + 1)
        angleRaw = bound(0, unitsFC - 1, angleRaw)
        if (angleP > 270) & (angleRaw < 90):
            turns+=1
        elif (angleP < 90) & (angleRaw > 270):
            turns-=1
        if turns >= 0.0:
            angle = (turns * unitsFC) + angleRaw
        elif turns < 0.0:
             angle = ((turns + 1) * unitsFC) - (unitsFC - angleRaw)
        angleP = angleRaw
#        print("Raw Angle:",angleRaw,"| Turns:", turns, "| Angle:", angle)

# PID controller interupt which uses PID to calculate the desired RPM, which is then converted
# to a duty cycle, and written to the servo
def PID_interrupt(timer):
    global angle, targetAngle, integral, prev_error
    errorAngle = targetAngle - angle
    integral += errorAngle
    derivative = errorAngle - prev_error
    outputRPM = rpm_to_duty(Kp * errorAngle + Ki * integral + Kd * derivative)
    prev_error = errorAngle
#     print("Target angle:", targetAngle, "| Angle:", angle, "| Error Angle:", errorAngle, "| Output:", outputRPM)
    servo_pwm.duty(outputRPM)
    
# PID timer configuration
pid_timer = machine.Timer(0)
pid_timer.init(period=100, mode=machine.Timer.PERIODIC, callback=PID_interrupt)

    
# Configure the timer for angle measurments
encoderTimer = machine.Timer(1)
encoderTimer.init(period=int(1/910*10000), mode=machine.Timer.PERIODIC, callback=encoder_interrupt)

# Function for requesting new reference input from user
def get_new_distance():
    # Prompt user for a new distance and return the value
    distance = float(input("Enter new distance (mm): "))
    return distance

# Function which updates global variables: target distance and target angle
def update_setpoint(distance):
    global targetdistance, targetAngle
    targetAngle = 360*-distance/(3.1415*dPitch)
    print(targetAngle)

###################################################################################
# Main loop
###################################################################################
while True:
    new_distance = get_new_distance()
    if new_distance is not None:
        update_setpoint(new_distance)
