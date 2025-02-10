#!/usr/bin/python

# Import local module.
from init_device import *
from states import *
# Display imports.
import displayio
# UI proccess imports.
from time import sleep

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
        self.key = "EMPTY"
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
        self.screenStates['SuccessfulCrack'] = SuccessfulCrack_State(self)
        self.screenStates['Complete'] = Complete_State(self)
        # Set initial screenState to WelcomeScreen.
        self.currentState = self.screenStates['WelcomeScreen']
        self.renderNewDisplay(self.currentState.getDisplay())
        

    def renderNewDisplay(self, newDisplay):
            self.display.loadDisplay(newDisplay)

    def Controls(self):
        self.currentState.Controls()

    def changeState(self, newState):
        self.currentState = self.screenStates[newState]
        self.currentState.makeNewDisplayGroup()
        newDisplay = self.currentState.getDisplay()
        self.renderNewDisplay(newDisplay)

        # DEBUG
        print("current state: ", self.currentState)

	    # Start process in new state
        self.currentState.spawnProcess()
        # Small sleep to prevent Joystick bouncing
        sleep(0.15)

    def setTargetNetwork(self, targetNetwork):
        self.screenStates['CapturingHandshake'].setTargetNetwork(targetNetwork)

    def setKey(self, newKey):
        self.key = newKey

    def getKey(self):
        return self.key


# Perpetual loop, enabling UI.
controller = Controller()
while True:
    controller.Controls()
    #controller.showDisplay()
    pass
