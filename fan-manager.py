#!/usr/bin/python3

import glob
import time
import configparser
import argparse
import os
from Logger import Logger

from os.path import exists

manualFanControl = False
daily_list = []                     # length =  86400 / pollinterval
recent_list = []                    # length =  recent_list_time / pollinterval

## Temp : fanspeed % in hexadecimal 
tempMap = {}

def FanControlSwitch(enable):
    global manualFanControl
    if(enable):
        if(manualFanControl == False):
            cmd = "ipmitool raw 0x30 0x30 0x01 0x00"
            manualFanControl = True
            os.system(cmd)
    else:
        cmd = "ipmitool raw 0x30 0x30 0x01 0x01"
        os.system(cmd)
        manualFanControl = False

def get_cpu_temp(tempType):
    cpu_temps = []
    for x in glob.glob("/sys/class/thermal/thermal_zone[0-9]/temp"): 
        tempFile = open(x)
        cpu_temps.append(int(tempFile.read().strip('\n')))
        tempFile.close()

    if (tempType == "Max"):
        tTemp = 0
        for i in cpu_temps:
            if (i > tTemp):
                tTemp = i   
        temp = int((int(tTemp)/1000))     
    elif ( tempType == "Avg" ):
        tTemp = 0
        for i in cpu_temps:
            tTemp += i
        temp = int((int(tTemp)/1000)/len(cpu_temps))

    if (len(daily_list) >= (86400/pollInterval)):
        daily_list.pop()
    daily_list.insert(0, temp)

    if (len(recent_list) >= (recent_list_time/pollInterval)):
        recent_list.pop()
    recent_list.insert(0, temp)


    return temp

def setFanSpeed(speed):
    global currentSpeed
    FanControlSwitch(True)
    cmd = f"ipmitool raw 0x30 0x30 0x02 0xff {hex(speed)}"
    os.system(cmd)
    currentSpeed = speed

def loadTempMap(filePath = './default.tm'):
    global tempMap
    if exists(filePath):
        with open(filePath, 'r') as f:
            line = f.readline()
            while line:
                tempMap.update({line.split(',')[0]: line.split(',')[1].strip('\n')})
                line = f.readline()

def handle_cleanup():
    ## Attempt to revert fans to system control - this is not always called depending on how the program exits
    FanControlSwitch(False)
    if (log != None):
        log.Dispose()

def TempMap_Handler(temp):
    if ( tempMap[str(temp)] != currentSpeed ):
        log.write(f" Temp :{temp} - Setting Fan Speed {int(tempMap[str(temp)],16)}%")
        setFanSpeed(temp, tempMap[str(temp)])
    else:
        log.write(f" Temp :{temp} - Fan Speed {int(tempMap[str(temp)],16)}% not changed")

def TargetTempWithBuffer_Handler(temp):
    global log
    newSpeed = -1
    if (shiftby == "distance"):
        shift = abs(config.getint("TargetTempWithBuffer","TargetTemp") - temp)
    else:
        shift = 1
    ## Temp Higher than target + buffer - Raise fan speed
    if (temp > (config.getint("TargetTempWithBuffer","TargetTemp")+config.getint("TargetTempWithBuffer","Buffer"))):
        if (currentSpeed < 100 ):
            newSpeed = currentSpeed + shift
    ## Temp Lower than target - buffer - Lower fan speed
    elif (temp < (config.getint("TargetTempWithBuffer","TargetTemp")-config.getint("TargetTempWithBuffer","Buffer"))):
        if (currentSpeed > config.getint("System","MinFanSpeed") ):
            newSpeed = currentSpeed - shift

    ## if newspeed not set it must be in range so do nothing 
    ## Set fan speed to new speed value (also updates currentspeed)
    if (newSpeed == -1):
        #do nothing
        log.write(f" Temp: {temp}\tFan Speed: {currentSpeed}",endWith="")
    else:
        setFanSpeed(newSpeed)
        log.write(f" Temp: {temp}\tFan Speed: {currentSpeed}",endWith="")



def main():
    
    ## Load Args
    parser = argparse.ArgumentParser(description='Fan Manager for Dell Servers.')
    parser.add_argument('--ControlType', '-T', default="TargetTempWithBuffer",
                        choices=['TargetTempWithBuffer', 'TempMap'], help='Control Type')
    parser.add_argument('--ConfigFile', '-C', default='/etc/fan-manager/conf.d/default.conf',
                        help='Path to Configuration File')
    parser.add_argument('--TemperatureCalculation', '-A', default='Max',
                        choices=['Max', 'Avg'], help='Value to use for Temprature calculation')

    args = parser.parse_args()

    try:
        ## Load Config
        global config
        global log
        global currentSpeed
        global pollInterval
        global recent_list_time
        global shiftby
        global statslog

        if (not exists(args.ConfigFile)):
            print(f"Can not access {args.ConfigFile} or it does not exist")
            return
        config = configparser.ConfigParser()
        config.read_file(open(args.ConfigFile))
        
        log = Logger(filePath=config["Logging"]["LogDirectory"], fileName=config["Logging"]["LogName"], maxFileSize=config["Logging"]["MaxLogSize"], logsToKeep=config["Logging"]["LogFilesToKeep"])
        log.write(" Starting Fan Manager\n")

        if (config.getboolean("Logging","CollectStats")):
            statslog = Logger(filePath=config["Logging"]["StatsDirectory"], fileName=config["Logging"]["StatsName"], maxFileSize=config["Logging"]["StatsMaxLogSize"], logsToKeep=config["Logging"]["StatsLogFilesToKeep"])

        pollInterval = config.getint("System","PollInterval")
        currentSpeed = config.getint("System","StartupSpeed")
        recent_list_time = config.getint("System","RecentTime")
        shiftby = config["TargetTempWithBuffer"]["ShiftBy"]
        ## Set Fan control to manual
        FanControlSwitch(True)
        exit = False
        while (not exit):
            time.sleep(pollInterval)
            temp = get_cpu_temp(config["System"]["TemperatureCalculation"])
            if(temp > config.getint("System","HighTempCutOff")):
                log.write(" Temp too high! Disabling Manual Fan Control\n")
                FanControlSwitch(False)
            else:
                match config["System"]["ControlType"]:
                    case "TargetTempWithBuffer":
                        TargetTempWithBuffer_Handler(temp)
                    case "TempMap":
                        TempMap_Handler(temp)

            average_24 = round(sum(daily_list) / len(daily_list),2)
            average_recent = round(sum(recent_list) / len(recent_list),2)
            log.write(f"\t24hr Avg: {average_24}\t{int(recent_list_time/60)}min Avg: {average_recent}", startWith="")
            if (config.getboolean("Logging","CollectStats")):
                statslog.write(f",{currentSpeed},{temp}")
                    
    finally:
        handle_cleanup()



if __name__ == "__main__":
    main()
