#!/usr/bin/python

# Display imports.
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect
import terminalio
import displayio
# Import local modules.
import processes
from init_device import *
# Misc imports.
from time import sleep


# Abstract parent class for States
class State:
    def __init__(self, controller):
        self.controller = controller
        self.display = None
        # The following method will set the value self.display to a new group
        self.makeNewDisplayGroup()

    def getDisplay(self):
        return self.display

    def setDisplay(self, newGroup):
        self.display = newGroup

    # Abstract Method
    def makeNewDisplayGroup(self):
        pass
    
    # Abstract Method
    def Controls(self):
        pass

    # Abstract Method
    def spawnProcess(self):
        pass

    def generateGenericBitmap(self):
        # Make BitMap
        bitmap = displayio.Bitmap(WIDTH, HEIGHT, 2) 
        # Make Palette
        palette = displayio.Palette(2)
        palette[0] = 0x000000
        palette[1] = 0xffffff
        return bitmap, palette

    def buildGroup(self, bitmap, palette, text_area=None, x=0, y=0):
        # Create a TileGrid
        #tileGrid = displayio.TileGrid(bitmap, pixel_shader=palette)
        # Create a Group and add the Tile Grid
        group = displayio.Group(x=x, y=y)
        #group.append(tileGrid)
        if text_area is not None :
            group.append(text_area)
        return group



class WelcomeScreen_State(State):
    def makeNewDisplayGroup(self):
        bitmap, palette = self.generateGenericBitmap()
        # Draw BitMap
        text = label.Label(terminalio.FONT, text="Welcome to\n cRakPipe", color=0xFFFFFF, x=35, y=25)
        # Set display to new group           
        newGroup = self.buildGroup(bitmap, palette, text_area=text)
        self.setDisplay(newGroup)

    def Controls(self):
        # Joy stick RIGHT
        if not button_R.value or not button_C.value:
            self.controller.changeState('SearchingNetworks')
        # DEBUG for testing with precaptured handshake
        if not button_U.value or not button_C.value:
            self.controller.changeState('SentAndWaiting')




class SearchingNetworks_State(State):
    def makeNewDisplayGroup(self):
        bitmap, palette = self.generateGenericBitmap()
        # Draw BitMap
        text = label.Label(terminalio.FONT, text="Searching Networks...", color=0xFFFFFF, x=0, y=HEIGHT // 2-1)
        # Set display to new group           
        newGroup = self.buildGroup(bitmap, palette, text_area=text)
        self.setDisplay(newGroup)

    def Controls(self):
        # Joy stick RIGHT
        #if not button_R.value: 
        #    self.controller.changeState('SelectNetwork')
        # Joy stick LEFT
        if not button_L.value: 
            self.controller.changeState('WelcomeScreen')
            
    def spawnProcess(self):
        networks = processes.getNetworks()
        # Add networks to SelectNetwork_State.
        self.controller.screenStates['SelectNetwork'].addNetworks(networks)
        self.controller.changeState('SelectNetwork')



class SelectNetwork_State(State):
    def __init__(self, controller):
        self.controller = controller
        self.networks = []
        self.displayedNetworks = []
        self.currentNetwork = None
        self.numberOfNetworks = 0
        self.makeNewDisplayGroup()

    def makeNewDisplayGroup(self):
        #self.clearDisplay = Rect(0, 0, 128, 64, fill=0xFFFFFF)
        bitmap, palette = self.generateGenericBitmap()
        #newGroup = self.buildGroup(bitmap, palette)
        newGroup = displayio.Group()
        # If no networks have been discovered, print error message to screen.
        if self.numberOfNetworks == 0:
            text = label.Label( terminalio.FONT, text="ERROR: No Networks" +\
                    "\n   Found", color=0xFFFFFF, x=8, y=HEIGHT // 2-1)
            newGroup = self.buildGroup(bitmap, palette, text_area=text)
            self.setDisplay(newGroup)
            return
        # Draw BitMap
        # Displays three networks at a time
        for position, network in enumerate(self.displayedNetworks):
            # Intialise display group.
            groupHeight = (HEIGHT // 3) -4
            y_coordinate = (groupHeight * position)
            networkGroup = displayio.Group(x=0, y=y_coordinate)
            # Set colours and add rectangle, allowing for colour inversion of selected network.
            if network is self.currentNetwork:
                background = 0xFFFFFF
                textCol = 0x000000
                selectedRect = Rect(0, 1, WIDTH, groupHeight-2, fill=background)
                networkGroup.append(selectedRect)
            else:
                textCol = 0xFFFFFF
            # Add network name text, only first 10 character of SSID/networkName.
            networkInfo  = network.name[:10] + '\t ' + network.signalStrength
            text_area = label.Label(terminalio.FONT, text=networkInfo, color=textCol, x=10, y=groupHeight//2)
            networkGroup.append(text_area)
            newGroup.append(networkGroup)
        '''
        # DEBUG
        print("networks")
        for network in self.networks:
            print(network.name, network)
        print("Displayed networks")
        for network in self.displayedNetworks:
            print(network.name, network)
        '''
        print("CURRENT NETWORK:", self.currentNetwork.name, self.currentNetwork.signalStrength)
        # Set the new display group.
        self.setDisplay(newGroup)

    def Controls(self):
        # Joy stick UP
        if not button_U.value:
            # At top of list, do nothing
            if self.currentNetwork is self.networks[0]:
                sleep(0.2)
                return
            # If at top of display, shift displayedNetworks
            if self.currentNetwork is self.displayedNetworks[0]:
                newStartIndex = self.networks.index(self.displayedNetworks[0])-1
                self.displayedNetworks = self.networks[newStartIndex:newStartIndex+3]
            # Shift current network.
            self.currentNetwork = self.networks[self.networks.index(self.currentNetwork)-1]
            self.makeNewDisplayGroup()
            self.controller.renderNewDisplay(self.getDisplay())
            sleep(0.2)
        # Joy stick DOWN
        if not button_D.value:
            # At bottom of list, do nothing
            if self.currentNetwork is self.networks[-1]:
                sleep(0.2)
                return
            # If at bottom of display, shift displayedNetworks
            if self.currentNetwork is self.displayedNetworks[-1]:
                newStartIndex = self.networks.index(self.displayedNetworks[0])+1
                self.displayedNetworks = self.networks[newStartIndex:newStartIndex+3]
            # Shift current network.
            self.currentNetwork = self.networks[self.networks.index(self.currentNetwork)+1]
            self.makeNewDisplayGroup()
            self.controller.renderNewDisplay(self.getDisplay())
            sleep(0.2)
        # Joy stick RIGHT
        if not button_R.value or not button_C.value: 
            self.controller.setTargetNetwork(self.currentNetwork)
            self.controller.changeState('CapturingHandshake')
        # Joy stick LEFT
        if not button_L.value: 
            self.controller.changeState('SearchingNetworks')

    def addNetworks(self, newNetworks):
        self.networks = newNetworks
        self.numberOfNetworks = len(newNetworks)
        # Set intial state to first network
        if self.numberOfNetworks != 0:
            self.displayedNetworks = self.networks[:3]
            self.currentNetwork = self.networks[0]
        self.makeNewDisplayGroup()



class CapturingHandshake_State(State):
    targetNetwork = None
   
    def makeNewDisplayGroup(self):
        newGroup = displayio.Group()
        text = label.Label(terminalio.FONT, text="Capturing WPA\n  Handshake", color=0xFFFFFF, x=16, y=HEIGHT // 2-1)
        # Need to fix change State before implementing
        #text = label.Label(terminalio.FONT, text="Capturing WPA\nHandshake on\n\
        #        %s"%(CapturingHandshake_State.targetNetwork.name), color=0xFFFFFF, x=28, y=5)
     

        newGroup.append(text)
        # Set the new display group.
        self.setDisplay(newGroup)
    
    def spawnProcess(self):

        #DEBUG
        print('capturing handshake on:', '$%s$'%(CapturingHandshake_State.targetNetwork.name))
        print('BSSID:', '$%s$'%(CapturingHandshake_State.targetNetwork.BSSID))
        print('channel:', '$%s$'%(CapturingHandshake_State.targetNetwork.channel))
        print('clientMAC:', '$%s$'%(CapturingHandshake_State.targetNetwork.clientMAC))
        # need exit to print
        #exit(0)

        apName = CapturingHandshake_State.targetNetwork.name
        apChannel = CapturingHandshake_State.targetNetwork.channel
        apMAC = CapturingHandshake_State.targetNetwork.BSSID
        clientMAC = CapturingHandshake_State.targetNetwork.clientMAC

        # Save output status of captureHandshake process.
        captureSuccess = processes.captureHandshake(apMAC, clientMAC, apChannel, apName)

        if captureSuccess:
            BSSID = CapturingHandshake_State.targetNetwork.BSSID
            ESSID = CapturingHandshake_State.targetNetwork.name
            processes.moveToFile(BSSID, 'targetBSSID.txt')
            processes.moveToFile(ESSID, 'targetESSID.txt')
            self.controller.changeState('SentAndWaiting')
        else:
            self.controller.changeState('CaptureFailed')

    def setTargetNetwork(self, targetNetwork):
        CapturingHandshake_State.targetNetwork = targetNetwork


class CaptureFailed_State(State):
    def Display(self):
        return group

    def makeNewDisplayGroup(self):
        newGroup = displayio.Group()
        text = label.Label(terminalio.FONT, text="  Capturing Failed\n<-New Net   Retry->", color=0xFFFFFF, x=8, y=25)
        newGroup.append(text)
        # Set the new display group.
        self.setDisplay(newGroup)
        pass
    
    def Controls(self):
        # Joy stick RIGHT
        if not button_R.value:
            self.controller.changeState('CapturingHandshake')
        # Joy stick LEFT
        if not button_L.value:
            self.controller.changeState('SelectNetwork')


class SentAndWaiting_State(State):
    # Abstract Method
    def makeNewDisplayGroup(self):
        newGroup = displayio.Group()
        text = label.Label(terminalio.FONT, text="Sent and Waiting", color=0xFFFFFF, x=8, y=25)
        newGroup.append(text)
        # Set the new display group.
        self.setDisplay(newGroup)
    
    # Abstract Method
    def spawnProcess(self):
        # Call send and receive processes, ensure scp is completed before
        # commencing for each.
        while(True):
            returnCode = processes.sendHandshake()
            sleep(7)
            if returnCode == 0:
                break
        while(True):
            returnCode = processes.receiveKey()
            sleep(7)
            if returnCode == 0:
                break
        result, key = processes.checkCrackResult()
        if (result == False):
            self.controller.changeState('Complete')
        else:
            # Save the key to the controller
            self.controller.setKey(key)
            self.controller.changeState('SuccessfulCrack')



class Complete_State(State):
    def Display(self):
        return group
    def Controls(self):
        pass
    # Abstract Method
    def makeNewDisplayGroup(self):
        newGroup = displayio.Group()
        text = label.Label(terminalio.FONT, text="Complete!", color=0xFFFFFF, x=28, y=25)
        newGroup.append(text)
        # Set the new display group.
        self.setDisplay(newGroup)
    
    # Abstract Method
    def Controls(self):
        pass

    # Abstract Method
    def spawnProcess(self):
        pass

class SuccessfulCrack_State(State):
    def Display(self):
        return group
    def Controls(self):
        pass
    # Abstract Method
    def makeNewDisplayGroup(self):
        key = self.controller.getKey()
        newGroup = displayio.Group()
        text = label.Label(terminalio.FONT, text=key, color=0xFFFFFF, x=28, y=25)
        newGroup.append(text)
        # Set the new display group.
        self.setDisplay(newGroup)
    
    # Abstract Method
    def Controls(self):
        pass

    # Abstract Method
    def spawnProcess(self):
        pass
