import time
import machine

# Set up encoder pin and servo pin
encoder_pin = machine.Pin(32, machine.Pin.IN)

# Define the variables
dcMin = 2.9
dcMax = 97.1
unitsFC = 360
dutyScale = 100
turns = 0
angle = 0.0
angleP = 0.0
firstRun = True

# Bound value between max and minimum
def bound(low, high, value):
    return max(low, min(high, value))

def encoder_interrupt(timer):
    global angle, angleP, turns
    tHigh = machine.time_pulse_us(encoder_pin,1)
    tLow =  machine.time_pulse_us(encoder_pin,0)
    tCycle = tHigh + tLow;
    if(950 < tCycle < 1250):
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
        print("Raw Angle:",angleRaw,"| Turns:", turns, "| Angle:", angle)

# Configure the timer
encoderTimer = machine.Timer(1)
encoderTimer.init(period=int(1/910*100000), mode=machine.Timer.PERIODIC, callback=encoder_interrupt)

# Main loop
while True:
    pass

