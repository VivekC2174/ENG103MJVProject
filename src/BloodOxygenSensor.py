from __future__ import print_function
import qwiic_max3010x
import time
import sys
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

RED = 25
GREEN = 24
BLUE = 23

GPIO.setup(RED, GPIO.OUT)
GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(BLUE, GPIO.OUT)


def millis():
    return int(round(time.time() * 1000))


def LEDs(red, green, blue):
    GPIO.output(RED, red)
    GPIO.output(GREEN, green)
    GPIO.output(BLUE, blue)


def runExample():
    print("\nSparkFun MAX3010x Photodetector - Example 5\n")
    sensor = qwiic_max3010x.QwiicMax3010x()

    if sensor.begin() == False:
        print("The Qwiic MAX3010x device isn't connected to the system. Please check your connection", \
              file=sys.stderr)
        return
    else:
        print("The Qwiic MAX3010x is connected.")

    print("Place your index finger on the sensor with steady pressure.")

    if sensor.setup() == False:
        print("Device setup failure. Please check your connection", \
              file=sys.stderr)
        return
    else:
        print("Setup complete.")

    sensor.setPulseAmplitudeRed(0x0A)  # Turn Red LED to low to indicate sensor is running
    sensor.setPulseAmplitudeGreen(0)  # Turn off Green LED

    RATE_SIZE = 4  # Increase this for more averaging. 4 is good.
    rates = list(range(RATE_SIZE))  # list of heart rates
    rateSpot = 0
    lastBeat = 0  # Time at which the last beat occurred
    beatsPerMinute = 0.00
    beatAvg = 0
    samplesTaken = 0  # Counter for calculating the Hz or read rate
    startTime = millis()  # Used to calculate measurement rate

    while True:
        sp02value = sensor.getIR() / (sensor.getIR() + sensor.getRed())
        irValue = sensor.getIR()
        samplesTaken += 1
        if sensor.checkForBeat(irValue) == True:
            # We sensed a beat!
            print('BEAT')
            delta = (millis() - lastBeat)
            lastBeat = millis()

            beatsPerMinute = 60 / (delta / 1000.0)
            beatsPerMinute = round(beatsPerMinute, 1)

            if beatsPerMinute < 255 and beatsPerMinute > 20:
                rateSpot += 1
                rateSpot %= RATE_SIZE  # Wrap variable
                rates[rateSpot] = beatsPerMinute  # Store this reading in the array

                # Take average of readings
                beatAvg = 0
                for x in range(0, RATE_SIZE):
                    beatAvg += rates[x]
                beatAvg /= RATE_SIZE
                beatAvg = round(beatAvg)

        Hz = round(float(samplesTaken) / ((millis() - startTime) / 1000.0), 2)
        if (samplesTaken % 200) == 0:
            print(
                'IR=', irValue, ' \t',
                'BPM=', beatsPerMinute, '\t',
                # 'DCE', getDCE() , '\t',\
                'Avg=', beatAvg, '\t',
                'Hz=', Hz,
                'SP02=', sp02value
            )
            if 20 < beatsPerMinute < 70:
                LEDs(0, 0, 0)  # turn off LED
                LEDs(0, 1, 0)  # make Led Green

            elif 70 <= beatsPerMinute <= 80:
                LEDs(0, 0, 0)
                LEDs(1, 1, 0)

            elif beatsPerMinute > 80:
                LEDs(0, 0, 0)
                LEDs(1, 0, 0)
            else:
                LEDs(0, 0, 0)


if __name__ == '__main__':
    try:
        runExample()
    except (KeyboardInterrupt, SystemExit) as exErr:
        print("\nEnding Example 5")
        sys.exit(0)
