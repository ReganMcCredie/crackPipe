#!/usr/bin/python

# Display imports.
from PIL import Image, ImageDraw, ImageFont
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect
import adafruit_displayio_ssd1306
import terminalio
import displayio
import board

# Joystick and button imports.
from digitalio import DigitalInOut, Direction, Pull

# UI proccess imports.
import subprocess
from time import sleep
import re
import os
import glob


import networkParsing
import processes


# Joystick and button GPIO Initialisation.
button_A = DigitalInOut(board.D5)
button_A.direction = Direction.INPUT
button_A.pull = Pull.UP

button_B = DigitalInOut(board.D6)
button_B.direction = Direction.INPUT
button_B.pull = Pull.UP

button_L = DigitalInOut(board.D27)
button_L.direction = Direction.INPUT
button_L.pull = Pull.UP

button_R = DigitalInOut(board.D23)
button_R.direction = Direction.INPUT
button_R.pull = Pull.UP

button_U = DigitalInOut(board.D17)
button_U.direction = Direction.INPUT
button_U.pull = Pull.UP

button_D = DigitalInOut(board.D22)
button_D.direction = Direction.INPUT
button_D.pull = Pull.UP

button_C = DigitalInOut(board.D4)
button_C.direction = Direction.INPUT
button_C.pull = Pull.UP

# Screen Dimensions.
WIDTH = 128
HEIGHT = 64


# Display GPIO Intialisation.
displayio.release_displays()
i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C, reset=board.D9)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT, auto_refresh=False)



'''
# Run airmon-ng to scan for available networks and capture the output.
output = subprocess.run(['sudo', 'airmon-ng'], capture_output=True)

# Serious airmon stuff
subprocess.run(['sudo', 'airmon-ng', 'check', 'kill'])
subprocess.run(['sudo', 'airmon-ng', 'start', 'wlan0'])

# Split output by line, removing newlines.
output = re.split('\n\s*\n', output.stdout.decode())


availableNetworks = []
for line in output[1:-1]:
    # remove trailing newline
    line = re.sub('\n', '', line)
    availableNetworks.append(re.split('\t', line)[1])
print(availableNetworks)
'''
# Reset display.
#self.clearDisplay = Rect(0, 0, 128, 64, fill=0xFFFFFF)
#self.rootDisplayGroup.append(self.clearDisplay)
#text = "Test Text"

 

class Display():
    def __init__(self):
        global display
        self.rootDisplayGroup = displayio.Group()
        display.root_group = self.rootDisplayGroup
        self.clearDisplay = Rect(0, 0, 128, 64, fill=0x000000)


    def loadDisplay(self, newGroup):
        global display
        # Remove previous display group. 'Display group'
        # is displayio jargon for image to be displayed.
        while self.rootDisplayGroup.__len__() > 0:
            self.rootDisplayGroup.pop()
        # Clear the display.
        self.rootDisplayGroup.append(self.clearDisplay)
        display.refresh()
        self.rootDisplayGroup.pop()
        # Render 'newGroup' display group.
        self.rootDisplayGroup.append(newGroup)
        display.refresh()
        
        # DEGUG
        print("Should be displaying now")
        print("number of groups in root:", self.rootDisplayGroup.__len__())


# Main controller class.
class Controller:
    def __init__(self):
        # Add Display
        self.display = Display()
        # Add ScreenStates
        self.screenStates = {} 
        self.screenStates['WelcomeScreen'] = WelcomeScreen_State(self)
        self.screenStates['SearchingNetworks'] = SearchingNetworks_State(self)
        self.screenStates['SelectNetwork'] = SelectNetwork_State(self)
        self.screenStates['CapturingHandshake'] = CapturingHandshake_State(self)
        self.screenStates['SentAndWaiting'] = SentAndWaiting_State(self)
        self.screenStates['CaptureFailed'] = CaptureFailed_State(self)
        self.screenStates['Complete'] = Complete_State(self)
        # Set initial screenState to WelcomeScreen.
        self.currentState = self.screenStates['WelcomeScreen']
        self.renderNewDisplay(self.currentState.getDisplay())

    def renderNewDisplay(self, newDisplay):
            self.display.loadDisplay(newDisplay)

    def Controls(self):
        self.currentState.Controls()

    def changeState(self, newState):
        newDisplay = self.screenStates[newState].getDisplay()
        self.renderNewDisplay(newDisplay)
        self.currentState = self.screenStates[newState]

        # DEBUG
        print("current state: ", self.currentState)

	    # Start process in new state
        self.currentState.spawnProcess()
        # Small sleep to prevent Joystick bouncing
        sleep(0.15)

    def setTargetNetwork(self, targetNetwork):
        self.screenStates['CapturingHandshake'].setTargetNetwork(targetNetwork)

	

    


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
   
    # Abstract Method
    def makeNewDisplayGroup(self):
        newGroup = displayio.Group()
        text = label.Label(terminalio.FONT, text="Capturing WPA\n  Handshake", color=0xFFFFFF, x=28, y=5)
        # Need to fix change State before implementing
        #text = label.Label(terminalio.FONT, text="Capturing WPA\nHandshake on\n\
        #        %s"%(CapturingHandshake_State.targetNetwork.name), color=0xFFFFFF, x=28, y=5)
     

        newGroup.append(text)
        # Set the new display group.
        self.setDisplay(newGroup)
    
    # Abstract Method
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
        # Call send and receive proccesses, ensure scp is completed before
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

        self.controller.changeState('Complete')



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


controller = Controller()
while True:
    controller.Controls()
    #controller.showDisplay()
    pass
