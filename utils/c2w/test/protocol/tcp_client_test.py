from twisted.trial import unittest
from twisted.test import proto_helpers
from twisted.internet import task
from c2w.protocol.tcp_chat_client import c2wTcpChatClientProtocol
import yaml
import re
import sys
import os
from collections import namedtuple
import logging
from twisted.internet import reactor


#logC2w = logging.getLogger('c2w')
#logC2w.setLevel(logging.DEBUG)

class FakeClientProxy:

    def connectionRejectedONE(self, msg):
        pass

    def initCompleteONE(self, userList, movieList):
        pass
    
    def setUserListONE(self, userList):
        pass
    
    def joinRoomOKONE(self):
        pass
    
    def chatMessageReceivedONE(self, message, theid):
        pass

    def updateMovieAddressPort(self, movieTitle, movieIpAddress, moviePort):
        pass

# python is magic: args is a list of arguments (size of the list is unknown).
#     call the client proxy method by giving each parameter the value of
#     each argument from the list


def protocol_wrapper(protocol, func, args):
    getattr(protocol, func)(*args)


def get_automata_path():
    return os.path.join(os.getenv("STOCKRSMPATH"), "data", "c2w", "test")

class c2wTcpChatClientTestCase(unittest.TestCase):

    def setUp(self):

        self.automata_dir = os.path.dirname(__file__)
        self.protocol = c2wTcpChatClientProtocol(FakeClientProxy(),
                                                 "0.0.0.0", 0)
        self.transport = proto_helpers.StringTransport()
        self.split = False
        self.two_by_two = False

        self.protocol.makeConnection(self.transport)

    def test_automata(self):

#         self.server_fsm = yaml.load(open(os.path.join(self.automata_dir, 
#                                                       self.automata)))
        self.server_fsm = yaml.load(open(self.automata))
        automata_state = namedtuple('automata_state', 'action edges')

        state = self.server_fsm['Init']
        label = 'Init'
        state = automata_state._make(state)  # now we can write t.action and t.edges
        while True:
            assert(type(state.action) is str)
            if state.action.startswith("CALL"):
                to_call = state.action.split()[1:]
                protocol_wrapper(self.protocol, to_call[0], to_call[1:])
            if state.action.startswith("F"):
                forward_time = float(re.search(r"(F )([0-9]*\.?[0-9]*)",
                                               state.action).
                                     group(2))
                self.clock.advance(forward_time)

            assert(type(state.edges) is dict)

            success = False
            for edge, next_state in list(state.edges.items()):
                condition, action = edge.split('/')
                if condition:
                    try:
                        v = self.transport.value()
                        #assert(type(v[0]) is str)
                        # check port and address. Should match 127... 9999
                        hex_v = "".join("{0:#0{1}x}".format(i, 4)[2:] for i in v)
                        if hex_v == condition:
                            print("\n ---> Test passed")
                            self.assertEqual(hex_v, condition)
                            self.transport.clear()
                            success = True
                        else:
                            failed_condition = condition
                            failed_hex_v = hex_v
                    except IndexError:
                        # we were expected something from the server ...
                        pending = reactor.getDelayedCalls()
                        for p in pending:
                            if p.active():
                                p.cancel()
                        self.fail("Well, this is embarrassing. I (the test)\
                        was expecting data from your protocol and nothing is\
                        available")
                if ((action and not condition) or (action and success)):
                    s = bytes()
                    for i in range(0, len(action), 2):
                        s = s + bytes([int(action[i: i + 2], 16)])
                    if self.split:
                        if self.two_by_two:
                            for i in range(0, len(s), 2):
                                #print ("sending ", s[i:i+2])
                                self.protocol.dataReceived(s[i:i+2])
                        else:
                            for s_b in s:
                                #print ("sending one byte: %u " % s_b)
                                self.protocol.dataReceived(bytes([s_b]))
                    else:
                        self.protocol.dataReceived(s)
                    state = automata_state._make(self.server_fsm[next_state])
                    label = next_state
                    break
                if not action and success:
                    state = automata_state._make(self.server_fsm[next_state])
                    label = next_state
                    break
            else:
                if label == "Final":
                    print("Rock'n Roll !")
                    pending = reactor.getDelayedCalls()
                    for p in pending:
                        if p.active():
                            p.cancel()
                    return
                self.assertEqual(failed_hex_v, failed_condition)


with open(os.path.join(get_automata_path(), "tcp_client_tests_list.txt")) as tests_list:
    tests = list(l.rstrip('\n') for l in tests_list.readlines())
        
for t in tests:
    
    def test_generic(self, t=t):
        self.automata = os.path.join(get_automata_path(), t + ".yaml")
        self.split = False
        self.two_by_two = False
        if 'framing' in t and ('1by1' in t or '2by2' in t):
            self.split = True
            self.two_by_two = '2by2' in t
        self.test_automata()
    setattr(c2wTcpChatClientTestCase, 'test_' + t, test_generic)
