#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Hector Ta
#
# Created:     24/07/2019
# Copyright:   Hector Ta 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import serial
import random
import time
import os
import msvcrt
from datetime import datetime
# Define names that may change
print ("Setting file names")
DATAOUT1='-final.txt' # This is the final CSV output after completion
DATAOUT2='-raw.txt' # This is where the CSV data is saved incrementally in case of
interruption
DEBUGOUT='-debug.txt' # Where debug outputs go
# Define constants
print("Defining constants")
# Define initial values
print("Defining initial values"
DATAPREFIX='test29'
# These arrays define sensor types and calibration variables
sensortypes=[1,2,2,1,1] # Identifies default sensor types
calibration=[0,0,0,0,0] # offset of final value
# These matricies are where data is kept until post processing
rawdataset=[] # This is where data is stored prior to processing (voltage
                #readings). Format = rawvalueset.format
dataset=[] # This is where data is stored after it is put through a calibration
curve. Format = currentvalueset.format
additionaldata=[] # This is where supplemental calculations are stored. Format =
#[counter, min sensor 1, max sensor 1, average sensor 1 (total), average sensor 1
#(moving), min sensor 2, max sensor 2, average sensor 2 (total), average sensor
#2(moving)

# These arrays are where data is kept while each sensor reports. Once done they are
#sent to the datasets at one time. There should be three more spaces than the number
#of sensors
# Format = [counter, timestamp, elapsed (seconds), sensor 1 (voltage), sensor 2
#(voltage)
rawvalueset=[0,0,0,0,0,0,0,0]
currentvalueset=[0,0,0,0,0,0,0,0]

counterlast=1 # Used for incremental saves to the temporary file (in case the
program fails)
counter=1
currentval=0
iterations=1
newcomma=-1
databit=0
i=1
i2=1
valuelimit=-1
timelimit=-1
datalength=1
stopstamp=0
totalelapsed = 0
samplecount=0
itergrid=[-1]
datagrid=[]
readset=[]
PORT='com4' # This is the port for the arduino
userinput=''
print "Defining sensor calibration curves"
# Set trendline for a type 1 sensor (10K ohm thermistor)
print "Type 1 Sensor is a 10K ohm thermistor"
s1cx6=0.00000000000003802599
s1cx5=-0.00000000013163288500
s1cx4=0.00000018401496784309
s1cx3=-0.00013221078369464300
s1cx2=0.05126731168167180000
s1cx1=-9.97795580719172000000
s1cx0=792.64578517129100000000
# Set trendline for type 2 sensor (Light Sensor)
print "Type 2 Sensor is a room light sensor"
# Training Data x=0,300,700,900,1024
# Training Data y=0,50,85,98,100
s2cx2=-0.00008362919778933350
s2cx1=0.18226818739982600000
s2cx0=0.79679493424566800000
# Set trendline for a type 3 sensor (Lilypad thermistor)
print "Type 3 Sensor is a Lilypad thermistor (unknown)"
s3cx6=0.00000000000000000000
s3cx5=0.00000000000000000000
s3cx4=0.00000000000000000000
s3cx3=0.00000000000000000000
s3cx2=0.00000000000000000000
s3cx1=0.87890625000000000000
s3cx0=58.00000000000000000000
# Definitions
print "Creating definitions"
def is_number(s):
 try:
 int(s)
 return True
 except ValueError:
 return False
def writedata(filename,dataarray,startpt,endpt,textname):
 print " Writing to ",filename," for ",textname
 debugmsg("Exporting Raw Data",datetime.now())


 with open(filename, "a") as f:
 i3=startpt-1
 while i3<=endpt-1:
 i4=0
 while i4<=len(dataarray[i3])-1:
 f.write("%s\t" % dataarray[i3][i4])
 i4+=1
 f.write("\n")
 i3+=1
 print " Closing"
 debugmsg(" Export complete",datetime.now())
# This is where debug messages are sent
def debugmsg(message,stamp):
 with open(DEBUGOUT, "a") as db:
 db.write("\n %s" % message)
 db.write("\t %s" % stamp)
# Type 1 sensor conversion
def converttemp(ts):
 return
(s1cx6*ts*ts*ts*ts*ts*ts)+(s1cx5*ts*ts*ts*ts*ts)+(s1cx4*ts*ts*ts*ts)+(s1cx3*ts*ts*ts
)+(s1cx2*ts*ts)+(s1cx1*ts)+(s1cx0)
# Type 2 sensor conversion
def convertlight(ts):
 return (s2cx2*ts*ts)+(s2cx1*ts)+(s2cx0)
# Type 3 sensor conversion
def converttemp2(ts):
 return
(s3cx6*ts*ts*ts*ts*ts*ts)+(s3cx5*ts*ts*ts*ts*ts)+(s3cx4*ts*ts*ts*ts)+(s3cx3*ts*ts*ts
)+(s3cx2*ts*ts)+(s3cx1*ts)+(s1cx0)
def readarduino(newdata):
 # Reads the data the arduino sent over serial
 # and is assuming it is in this format: 30.2,532.012,5 (CSV in other words)
 # it then searches for the commas and tries to break the data into an array
 iterations = newdata.count(',') # counts the number of commas to know how many datablocks are needed
 i=1 # Reset counter variable (it is reused elsewhere)
 itergrid=[-1] # Reset comma location array since this process is repeated
for each data sample
 datagrid=[] # Reset the data array since this proccess is repeated for each data sample
 while i <= iterations: # Repeat the following for each comma found
 newcomma=newdata.find(',',itergrid[i-1]+1) # Identify the next comma using the array of located commas
 itergrid.append(newcomma) # Add this comma to the array of located commas
 databit=newdata[itergrid[i-1]+1:itergrid[i]] # The databit is the text
                            #between two commas ("... ,20, ..." = "20")
 if is_number(databit)==True: # Look at databit and determine if it could be a number using another definition
 databit=int(databit) # If databit could be a number, convert it into
                        #a number
 datagrid.append(databit) # Add the current data bit to the dataset
 i+=1 # Move on to the next comma
 databit=newdata[itergrid[i-1]+1:] # Make a databit for the text between the last comma and the end of line
 if is_number(databit)==True: # Repeat check to see if databit could be a number
 databit=int(databit) # If databit could be a number, convert it into a
                        #number

 datagrid.append(databit) # Add the current data bit to the dataset
 return datagrid # That should be the full array, so send it back to be saved
def kbfunc():
 x = msvcrt.kbhit()
 if x:
 ret = ord(msvcrt.getch())
 else:
 ret = 0
 return ret
# User setup variables
print "Getting user setup variables"
PORT = raw_input("Please enter COM port number (i.e. COM3 = COM3 / Linux =
/dev/ttyUSB0):")
DATAPREFIX = raw_input("Please enter data file prefix (without extension):")
DATAOUT1=DATAPREFIX+DATAOUT1
DATAOUT2=DATAPREFIX+DATAOUT2
DEBUGOUT=DATAPREFIX+DEBUGOUT
while timelimit<1:
 userinput=raw_input("Please enter number of minutes to record:")
 if is_number(userinput)==True:
 timelimit=int(userinput)
# Start the clock
print "Starting clock"
startstamp = datetime.now()
debugmsg("Program Started",startstamp)
# Start communication with Arduino
print "Starting serial port communications"
ser = serial.Serial(PORT, 9600)
debugmsg("Serial Port Started",datetime.now())

print "Starting recording - Press 'Z' to end early"
debugmsg("Recording started",datetime.now())
while 1:
 # Get new data
currentread=ser.readline()
debugmsg(currentread,datetime.now())
# Convert data to array
readset=readarduino(currentread)
datalength=len(readset)
# Act on data - Convert to an array of the raw values
i2=1
timestamp=datetime.now()
while i2 <=datalength:
 currentval=readset[i2-1]
 rawvalueset[i2+2]=-1 # This clears the current value so that any
                        #record errors are obvious
 if is_number(currentval)==True:
 currentval=int(currentval)
 rawvalueset[i2+2]=currentval
 i2+=1
 elapsedstamp=timestamp-startstamp
 elapsed =
elapsedstamp.days*86400.000000+elapsedstamp.seconds+elapsedstamp.microseconds/100000
.000000
 rawvalueset[0]=counter
 rawvalueset[1]=timestamp.strftime("%Y-%m-%d %H:%M:%S")
 rawvalueset[2]=round(elapsed,2)
 rawdataset.append(rawvalueset[:])
 # Act on data - Convert the raw values to sensor data

 i2=1
 currentvalueset[0]=rawvalueset[0]
 currentvalueset[1]=rawvalueset[1]
 currentvalueset[2]=rawvalueset[2]
 while i2 <=datalength:
 currentvalueset[i2+2]=-1 # This clears the current value so that any errors are obvious
 if sensortypes[i2-1]==1:

currentvalueset[i2+2]=round(converttemp(rawvalueset[i2+2])+calibration[i2-1],2)
 if sensortypes[i2-1]==2:

currentvalueset[i2+2]=round(convertlight(rawvalueset[i2+2])+calibration[i2-1],2)
 if sensortypes[i2-1]==3:

currentvalueset[i2+2]=round(converttemp2(rawvalueset[i2+2])+calibration[i2-1],2)
 i2+=1
 dataset.append(currentvalueset[:])
 print "%s " % currentvalueset
 if elapsed>=60.00*timelimit:
 break
 if counter-counterlast>3:
 writedata(DATAOUT2,rawdataset,counterlast,counter,"rawdataset")
 counterlast=counter+1
 X=kbfunc() # This allows the user to push Z to end the recording early
 if X==122:
 break
 counter+=1

print "Ending recording"
stopstamp=timestamp-startstamp
debugmsg("Recording ended",timestamp)
totalelapsed =
stopstamp.days*86400.000000+stopstamp.seconds+stopstamp.microseconds/100000.000000
samplecount=counter
debugmsg("Total samples ",timestamp)
debugmsg(samplecount,timestamp)
# Print out final data
print "Writing final data file"
debugmsg("Writing final data set",datetime.now())
writedata(DATAOUT1,dataset,1,counter,"dataset")
debugmsg("Final data set complete",datetime.now())
print "Ending Program\n"
debugmsg("Normal end of program",datetime.now())
