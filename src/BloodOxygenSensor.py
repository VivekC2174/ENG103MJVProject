from __future__ import print_function
from __future__ import division
import qwiic_max3010x
import time
import sys
import RPi.GPIO as GPIO
from twilio.rest import Client

GPIO.setmode(GPIO.BCM)

led = 26

GPIO.setup(led, GPIO.OUT)


def sendMessage(msg):
    # Find your Account SID and Auth Token at twilio.com/console
    # and set the environment variables. See http://twil.io/secure
    account_sid = 'AC3514b8529ae6590623639fdcf6443779'
    auth_token = '486d31b84480487cea5e52e6c92dd476'
    client = Client(account_sid, auth_token)

    message = client.messages.create(body=msg, from_='+12248084210', to='+61423644084')


def millis():
    return int(round(time.time() * 1000))


def Main():
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
        redValue = int(sensor.getRed())
        irValue = int(sensor.getIR())
        add = redValue + irValue
        sp02value = int(irValue / (redValue + irValue) * 100)

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
            GPIO.output(led, 0)
            print(
                'IR=', irValue, ' \t',
                'Red=', redValue, ' \t',
                'BPM=', beatsPerMinute, '\t',
                # 'DCE', getDCE() , '\t',\
                'Avg=', beatAvg, '\t',
                'Hz=', Hz,
                'SP02=', sp02value
            )
            if 60 > beatsPerMinute > 100:  # if heart rate is at a unsafe level
                GPIO.output(led, 1)  # turn on LED
                sendMessage("Heartbeat in unsafe range")
                time.sleep(3)
                GPIO.output(led, 0)  # turn off LED


if __name__ == '__main__':
    try:
        Main()
    except (KeyboardInterrupt, SystemExit) as exErr:
        print("\nEnding")
        sys.exit(0)
