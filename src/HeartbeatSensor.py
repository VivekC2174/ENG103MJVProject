import Adafruit_MCP3008
import time
from datetime import datetime
print(datetime.now(), "James Pitor, Vivek Chand, Mariah Clarke")

# Software SPI configuration:

CLK = 11

MISO = 9

MOSI = 10

CS = 8

mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)


# Print nice channel column headers.

# Main program loop.
secs = 0

while(secs < 0.6):

    # Read all the ADC channel values in a list.

    values = [0]*8

    for i in range(8):

        # The read_adc function will get the value of the specified channel (0-7)

        values[i] = mcp.read_adc(i)

        # Print the ADC values.

        #print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*values))

        # Pause for half a second.
        #print(values)
        secs += 0.1
        #print(secs)
        print("Time = " + str(secs) + "sensor data is " + str(values[0]) + " " + "*" *(int (values[0] / 10)))
        #print(values[0])
        time.sleep(0.1)