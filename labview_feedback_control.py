import time
import machine

opponent_active = 0

###################################################################################
# Define pins and servos
###################################################################################
# Goalie pins
goalieEncoderPin = machine.Pin(32, machine.Pin.IN)
goaliePWM = machine.PWM(machine.Pin(14, machine.Pin.OUT))
goaliePWM.freq(50)

# Defender pins
defenderEncoderPin = machine.Pin(33, machine.Pin.IN)
defenderPWM = machine.PWM(machine.Pin(15, machine.Pin.OUT))
defenderPWM.freq(50)

###################################################################################
# Define the encoder variables
###################################################################################
# Common
dcMin = 2.9 # Duty cycle for minimum servo RPM (2.9% DC = -140RPM)
dcMax = 97.1 # Duty cycle for max servo RPM (97.1% DC = 140RPM)
unitsFC = 360 # Number of units in a full circle rotation (360 to calculate angle)
dutyScale = 100 # Scale applied to duty cycle to get percent
alpha = 0.9 # Alpha value for low pass filter

# Goalie
goalieTurns = 0 # Track number of complete rotations
goalieAngle = 0.0 # Initialize angle variable
goalieAnglePrev = 0.0 # Initialize previous angle variable
goalieAngleRawPrev = 0.0 # Initizlize previous raw angle variable

# Defender
defenderTurns = 0 # Track number of complete rotations
defenderAngle = 0.0 # Initialize angle variable
defenderAnglePrev = 0.0 # Initialize previous angle variable
defenderAngleRawPrev = 0.0 # Initizlize previous raw angle variable

###################################################################################
# Define the PID control varaibles
###################################################################################
# Common
Kp = 8
Ki = 0.1
Kd = 8
dPitch = 90 # Pitch diameter of rack and pinion (mm)

# Goalie
goaliePrevError = 0 # Variable for storing previous error to calculate "derivative" term
goalieIntegral = 0 # Storing integral term
goalieTargetDistance = 0 # Reference distance
goalieTargetAngle = 360*goalieTargetDistance/(3.1415*dPitch) # Convert reference distance to angle

# defender
defenderPrevError = 0 # Variable for storing previous error to calculate "derivative" term
defenderIntegral = 0 # Storing integral term
defenderTargetDistance = 0 # Reference distance
defenderTargetAngle = 360*defenderTargetDistance/(3.1415*dPitch) # Convert reference distance to angle

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
# Interrupt for measuring angle from encoder. This is done by measuring the high pulse
# and low pulse of the encoder output, and calculating the angle from this duty cycle using
# formulas from the documentation
def goalie_encoder_interrupt(timer):
    global goalieAngle, goalieAngleRawPrev, goalieTurns, defenderAngle, defenderAngleRawPrev, defenderTurns
    tHigh = machine.time_pulse_us(goalieEncoderPin,1)
    tLow =  machine.time_pulse_us(goalieEncoderPin,0)
    tCycle = tHigh + tLow;
    if(1000 < tCycle < 1200):
        dc = (100 * tHigh) / tCycle;
        angleRaw = (unitsFC - 1) - ((dc - dcMin) * unitsFC) / (dcMax - dcMin + 1)
        angleRaw = bound(0, unitsFC - 1, angleRaw)
        if (goalieAngleRawPrev > 270) & (angleRaw < 90):
            goalieTurns+=1
        elif (goalieAngleRawPrev < 90) & (angleRaw > 270):
            goalieTurns-=1
        if goalieTurns >= 0.0:
            angleUnfilt = (goalieTurns * unitsFC) + angleRaw
        elif goalieTurns < 0.0:
             angleUnfilt = ((goalieTurns + 1) * unitsFC) - (unitsFC - angleRaw)
        goalieAngle = low_pass_filter(goalieAnglePrev, angleUnfilt)
        goalieAngleRawPrev = angleRaw
#         print("Raw Angle:",angleRaw,"| Turns:", goalieTurns, "| Angle:", goalieAngle)
    tHigh = machine.time_pulse_us(defenderEncoderPin,1)
    tLow =  machine.time_pulse_us(defenderEncoderPin,0)
    tCycle = tHigh + tLow;
    if(1000 < tCycle < 1200):
        dc = (100 * tHigh) / tCycle;
        angleRaw = (unitsFC - 1) - ((dc - dcMin) * unitsFC) / (dcMax - dcMin + 1)
        angleRaw = bound(0, unitsFC - 1, angleRaw)
        if (defenderAngleRawPrev > 270) & (angleRaw < 90):
            defenderTurns+=1
        elif (defenderAngleRawPrev < 90) & (angleRaw > 270):
            defenderTurns-=1
        if defenderTurns >= 0.0:
            angleUnfilt = (defenderTurns * unitsFC) + angleRaw
        elif defenderTurns < 0.0:
             angleUnfilt = ((defenderTurns + 1) * unitsFC) - (unitsFC - angleRaw)
        defenderAngle = low_pass_filter(defenderAnglePrev, angleUnfilt)
        defenderAngleRawPrev = angleRaw

# PID controller interupt which uses PID to calculate the desired RPM, which is then converted
# to a duty cycle, and written to the servo
def goalie_PID_interrupt(timer):
    global goalieAngle, goalieTargetAngle, goalieIntegral, goaliePrevError, defenderAngle, defenderTargetAngle, defenderIntegral, defenderPrevError
    errorAngle = goalieTargetAngle - goalieAngle
    goalieIntegral += errorAngle
    derivative = errorAngle - goaliePrevError
    outputRPM = rpm_to_duty(Kp * errorAngle + Ki * goalieIntegral + Kd * derivative)
    goaliePrevError = errorAngle
#     print("Target angle:", goalieTargetAngle, "| Angle:", goalieAngle, "| Error Angle:", errorAngle, "| Output:", outputRPM)
    goaliePWM.duty(outputRPM)
    errorAngle = defenderTargetAngle - defenderAngle
    defenderIntegral += errorAngle
    derivative = errorAngle - defenderPrevError
    outputRPM = rpm_to_duty(Kp * errorAngle + Ki * defenderIntegral + Kd * derivative)
    defenderPrevError = errorAngle
#     print("Target angle:", defenderTargetAngle, "| Angle:", defenderAngle, "| Error Angle:", errorAngle, "| Output:", outputRPM)
    defenderPWM.duty(outputRPM)
    
# PID timer configuration
goalie_pid_timer = machine.Timer(0)
goalie_pid_timer.init(period=100, mode=machine.Timer.PERIODIC, callback=goalie_PID_interrupt)

# defender_pid_timer = machine.Timer(1)
# defender_pid_timer.init(period=100, mode=machine.Timer.PERIODIC, callback=defender_PID_interrupt)
    
# Configure the timer for angle measurments
goalie_encoder_timer = machine.Timer(2)
goalie_encoder_timer.init(period=int(1/910*20000), mode=machine.Timer.PERIODIC, callback=goalie_encoder_interrupt)

# defender_encoder_timer = machine.Timer(3)
# defender_encoder_timer.init(period=int(1/910*1000), mode=machine.Timer.PERIODIC, callback=defender_encoder_interrupt)

# Function which updates global variables: target distance and target angle
def update_goalie_setpoint(distance):
    global goalieTargetDistance, goalieTargetAngle
    goalieTargetAngle = 360*-distance/(3.1415*dPitch)
    #print(goalieTargetAngle)

# Function which updates global variables: target distance and target angle
def update_defender_setpoint(distance):
    global defenderTargetDistance, defenderTargetAngle
    defenderTargetAngle = 360*-distance/(3.1415*dPitch)

def low_pass_filter(valuePrev, valueNew):
    return alpha * valuePrev + (1 - alpha) * valueNew

print('\r\nESP32 Ready to accept Commands\r\n')

###################################################################################
# labview communication
###################################################################################
try:
    while(1):
        command=input('')
        indicatorChar=command[0]
        if indicatorChar == 'T':
            if opponent_active == 1:
                print("TOpponent Disabled \r\n")
            else:
                print("TOpponent Enabled \r\n")
            opponent_active ^= 1
        elif indicatorChar == 'R':
            newSetpoint=float(command[1:len(command)])
            update_goalie_setpoint(newSetpoint)
        elif indicatorChar == 'Q':
            newSetpoint=float(command[1:len(command)])
            update_defender_setpoint(newSetpoint)
        elif indicatorChar == '1' and opponent_active == 0:
            print('1Setpoint = 100\r\n')
        elif indicatorChar == '2' and opponent_active == 0:
            print('2Opponent Disabled\r\n')
        elif indicatorChar == '3' and opponent_active == 0:
            print('3Opponent Disabled\r\n')
        elif indicatorChar == 'I':
            print('IESP32\r\n')            
except:
    goalie_encoder_timer.deinit()
    goalie_pid_timer.deinit()
    pass
