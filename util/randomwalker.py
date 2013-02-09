#!/usr/bin/env python2

################## randomwalker.py ####################
# This is a test-AI for skyport, written in python    #
# & twisted. It randomly walks around on the board.   #
# This AI mainly demonstrates the use of the skyport  #
# python API.                                         #
# Note that the API is "framework-agnostic", so there #
# is no need to actually use twisted -- you can just  #
# use threads and blocking i/o if you want to. All    #
# you need to provide the skyport API with is a       #
# function it can use to send data to the socket,     #
# and you need to call receiver.parse_line() whenever #
# you receive data on the socket.                     #
#                                                     #
# Written by Jonathan Ringstad                        #
#######################################################

import sys
import json
import random

from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver

sys.path.append("../api/python")
import skyport

NAME = "randomwalker"

class SkyportConnection(LineReceiver):
    receiver = None
    transmitter = None
    delimiter = "\n" # need to set this
    def lineReceived(self, line):
        self.receiver.parseLine(line)
        
    def gotHandshake(self):
        print("AI got handshake!")
        
    def gotError(self, errormessage):
        print("AI got error: %s" % errormessage)
        
    def gotGamestate(self, turnNumber, mapObject, playerList):
        print("AI got gamestate!")
        if playerList[0]["name"] == NAME:
            direction = random.choice(["up", "down", "left-down", "left-up", "right-down", "right-up"])
            print("my turn! moving %s-wards." % direction)
            self.transmitter.sendMove(direction);
        
    def gotGamestart(self, turnNumber, mapObject, playerList):
        self.transmitter.sendLoadout("droid", "mortar")
        print("AI got gamestart!")
        
    def gotAction(self, actionType, restData):
        print("AI got action: %s" % actionType)
        
    def gotEndturn(self):
        print("AI got endturn!")
        
    def connectionMade(self):
        self.receiver = skyport.SkyportReceiver()
        # Set up callbacks for the receiver
        self.receiver.cb_handshake_successful = self.gotHandshake
        self.receiver.cb_error = self.gotError
        self.receiver.cb_gamestate = self.gotGamestate
        self.receiver.cb_gamestart = self.gotGamestart
        self.receiver.cb_action = self.gotAction
        self.receiver.cb_endturn = self.gotEndturn
        self.transmitter = skyport.SkyportTransmitter(self.sendLine)
        # the transmitter only needs to know what function to call
        # to actually send the data to the socket (self.sendLine)
        self.transmitter.sendHandshake(NAME)
        # send the initial handshake

class SkyportConnectionFactory(ClientFactory):
    protocol = SkyportConnection
    def clientConnectionFailed(self, connector, reason):
        print 'connection failed:', reason.getErrorMessage()
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print 'connection lost:', reason.getErrorMessage()
        reactor.stop()

def main():
    factory = SkyportConnectionFactory()
    reactor.connectTCP('localhost', 54321, factory)
    reactor.run()

if __name__ == '__main__':
    main()
