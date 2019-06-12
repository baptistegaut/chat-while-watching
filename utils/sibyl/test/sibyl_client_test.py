import sys
from twisted.trial import unittest
from twisted.test import proto_helpers
from sibyl.protocol.sibyl_client_tcp_bin_protocol import SibylClientTcpBinProtocol
from sibyl.main.sibyl_tcp_client_factory import SibylTcpClientProtocolFactory
try:
    import yaml
except:
    print('yaml is unavailable')
    sys.exit(0)
import time
import shlex
import os
import inspect
import binascii

def mytime():
    return 1851.0


class Automata():
    def __init__(self, graph):
        self.graph = dict((k, tuple(v)) for (k, v) in graph.items())

    def get_starting_node(self):
        return 'Node A'

    def node_contains_client_action(self, node):
        return True if self.graph[node][0] is not None else False

    def node_get_client_action(self, node):
        return self.graph[node][0]

    def node_has_no_edges(self, node):
        return True if (not self.node_has_action_edges(node)
                        and not self.node_has_conditionnal_edges(node)
                        ) else False

    def node_has_illegal_edges(self, node):
        return True if (self.node_has_action_edges(node)
                        and self.node_has_conditionnal_edges(node)
                        ) else False

    def node_has_conditionnal_edges(self, node):
        return True if self.node_get_conditionnal_edges(node) else False

    def node_has_action_edges(self, node):
        return True if self.node_get_action_edges(node) else False

    def node_get_conditionnal_edges(self, node):
        edges = self.graph[node][1]  # 0 is client_action, 1 is edges
        if edges is None:
            return []
        conditions = [e.split('/')[0] for e in edges]  # 0:condition, 1:action
        return [c for c in conditions if c]

    def node_get_action_edges(self, node):
        edges = self.graph[node][1]  # 0 is client_action, 1 is edges
        if edges is None:
            return []
        actions = [e.split('/')[1] for e in edges]  # 0:condition, 1:action
        return [a for a in actions if a]

    def get_next_from_action_edge(self, node, action):
        for e, v in self.graph[node][1].items():
            if e.split('/')[1] == action:
                return v

    def next_from_conditionnal_edge(self, node, condition):
        for e, v in self.graph[node][1].items():
            if e.split('/')[0] == condition:
                return v


def Error(s):
    print(s)
    exit(1)


class FakeProxy():
    def connectionSuccess(self):
        pass

    def registerProtcolInstance(self, instance):
        pass

    def responseReceived(self, responseText):
        pass


class FakeController():
    pass


class SibylClientTestCase(unittest.TestCase):

    print ("Module in test: " + inspect.getfile(SibylClientTcpBinProtocol))

    def setUp(self):
        self.tr = proto_helpers.StringTransport()

        #time.time = mytime
        factory = SibylTcpClientProtocolFactory(SibylClientTcpBinProtocol,
                                                FakeProxy(),
                                                FakeController())
        self.protocol = factory.buildProtocol(('127.0.0.1', 0))
        #self.protocol = SibylClientTcpBinProtocol(FakeProxy())
        self.protocol.makeConnection(self.tr)

    def execute_client_action(self, action):
        # works only for calling a method with one argument
        # to be fixed !
        #getattr(self.protocol, action.split()[0])(action.split()[1])
        getattr(self.protocol, shlex.split(action)[0])(shlex.split(action)[1])

    def test_sibyl_no_framing(self):
        
        st = open(os.path.join(os.getenv("STOCKRSMPATH"), "sibyl", "test", "clienttest.yaml"))

        mygraph = yaml.load(st)

        server = Automata(mygraph)
        current_node = server.get_starting_node()
        while True:
            if server.node_contains_client_action(current_node):
                self.execute_client_action(server.
                                           node_get_client_action(current_node))
            if server.node_has_no_edges(current_node):
                return
            if server.node_has_illegal_edges(current_node):
                Error('graph has illegal edges')
            if server.node_has_conditionnal_edges(current_node):
                value = self.tr.value()
                trval = ""
                for i in value:
                    trval = trval + "{0:#0{1}x}".format(i, 4)[2:]
                value = trval
                
                matches = [item for item in
                           server.node_get_conditionnal_edges(current_node)
                           if self.sibylEquals(item, value)]
                if matches:
                    self.assertEqual(value, int_to_4hex(self.protocol_time) + matches[0][8:])
                    current_node = server.next_from_conditionnal_edge(current_node,
                                                                  matches[0])
                    self.tr.clear()
                else:
                    if self.time_ok:
                        self.assertEqual(value, int_to_4hex(self.protocol_time) +
                                                server.node_get_conditionnal_edges(current_node)[0][8:])
                    else:
                        self.assertEqual(value, int_to_4hex(self.test_time) + 
                                         server.node_get_conditionnal_edges(current_node)[0][8:])
                    
            if server.node_has_action_edges(current_node):
                if len(server.node_get_action_edges(current_node)) != 1:
                    Error('no more than 1 action edge')
                else:
                    e = server.node_get_action_edges(current_node)[0]
                    s = bytes()
                    for i in range(0, len(e), 2):
                        abyte = bytes([int(e[i: i + 2], 16)])                          
                        s = s + abyte
                    self.protocol.dataReceived(s)
                    #self.protocol.dataReceived(e)
                    current_node = server.get_next_from_action_edge(current_node, e)


    def sibylEquals(self, s1, s2):
        self.test_time = int(time.time())
        self.protocol_time = int.from_bytes(bytes.fromhex(s2[0:8]), 'big')
        self.time_ok = abs(self.protocol_time - self.test_time) < 5
        self.following_ok = s1[8:] == s2[8:]
        return self.following_ok and self.time_ok

def int_to_4hex(i):
    return ''.join(["%02X" % x for x in i.to_bytes(4, "big")]).strip().lower()

def b1(n):
    return "01"[n % 2]


def b2(n):
    return b1(n >> 1) + b1(n)


def b3(n):
    return b2(n >> 2) + b2(n)


def b4(n):
    return b3(n >> 4) + b3(n)

thebytes = [b4(n) for n in range(256)]


def binstring(s):
    return ''.join(thebytes[ord(c)] for c in s)
