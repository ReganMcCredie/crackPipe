#!/usr/bin/python
import re


class Client():
    def __init__(self, clientMAC, accessPointMAC):
        self.clientMAC = clientMAC
        self.accessPointMAC = accessPointMAC


class Network():
    def __init__(self, name, BSSID, channel, signalStrength, clientMAC):
        self.name = name
        self.BSSID = BSSID
        self.channel = channel
        self.signalStrength = signalStrength
        self.clientMAC = clientMAC


def parseCSV(filename):
    networks = []
    with open(filename, 'r') as file:
        content = file.readlines()
        # Read file from bottom to top.
        content = list(reversed(content))
        # For each client, grab client MAC and associateed BSSID.
        clients, startLine = getClients(content)
        # Ommit top two lines of CSV file, known to be irrelevant.
        content = content[startLine:-2]
        for line in content:
            words =  line.split(',')
            # Grab data for Network object.
            networkName = words[13]
            BSSID = words[0]
            channelNumber = words[3]
            signalStrength = words[8]
            # Remove Whitespace.
            networkName = networkName[1:]
            channelNumber = re.sub('\s', '', channelNumber)
            signalStrength = re.sub('\s', '', signalStrength)
            # Dont include 'empty' networks.
            if (networkName == ''):
                continue
            # Find client for Deauth.
            for client in clients:
                # If associated client is found, add the network the networks list.
                # Logic is: cant deAuth attack networks without associated clients.
                if BSSID == client.accessPointMAC:
                    networks.append(Network(networkName, BSSID, channelNumber, signalStrength, client.clientMAC))
                    break
    # Sort networks by signal strength.
    networks.sort(key=lambda x: x.signalStrength, reverse=True)
    return networks


def getClients(content):
    clients = []
    for lineNumber, line in enumerate(content[1:]):
        if re.match(r'Station', line):
            return clients, lineNumber+3
        words =  line.split(',')
        clientMAC = words[0]
        accessPointMAC = words[5][1:]
        if re.search('not associated', accessPointMAC):
            continue
        clients.append(Client(clientMAC, accessPointMAC))