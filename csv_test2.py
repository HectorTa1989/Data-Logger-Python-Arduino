#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Hector Ta
#
# Created:     24/07/2019
# Copyright:   (c) hp 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import serial
import csv
import time
import numpy as np
import warnings
import serial
import serial.tools.list_ports
##ser = serial.Serial('COM4', 9600, timeout=.1)
##while True:
##	data = ser.readline()[:-2] #the last bit gets rid of the new-line chars
##	if data:
##		print data

##Approach 1
##In this case, we rely on seeing the letter "E" to know when to stop reading from the file.
# Open com port
ser = serial.Serial('COM4', 9600)

with open("datafile.csv", "w") as new_file:
    csv_writer = csv.writer(new_file)

    while True:
        # Strip whitespace on the left and right side
        # of the line
        line = ser.readline().decode()

        # If line starts with B, strip the B
        if line.startswith("B"):
            line = line[1:]

        # If the line ends with E, we reached the last line
        # We strip the E, and keep in mind that the serial
        # reader should be closed
        should_close = False
        if line.endswith("E"):
            line = line[:-1]
            should_close = True

        # Split the string "180,3600,1234" into a list ["180", "3600", "1234"]
        xyz_string_triplet = line.split(",")
        if len(xyz_string_triplet) != 3:
            print("Ignored invalid line: " + line)
            continue

        # Convert the numbers from string format to integer
        x = int(xyz_string_triplet[0])
        y = int(xyz_string_triplet[1])
        z = int(xyz_string_triplet[2])

        # Write XYZ to the CSV file
        csv_writer.writerow([x, y, z])

        # If we reached the last line, we close
        # the serial port and stop the loop
        if should_close:
            ser.close()
            break