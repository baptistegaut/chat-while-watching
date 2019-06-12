from twisted.trial import unittest
from twisted.test import proto_helpers
from sibyl.protocol.sibyl_server_tcp_bin_protocol import SibylServerTcpBinProtocol
from sibyl.main.sibyl_tcp_server_factory import SibylTcpSeverProtocolFactory
from sibyl.main.sibyl_brain import SibylBrain
import os
import yaml
import time
import inspect


def mytime():
    return 1851.0


class ClientsAutomata():
    """
    For testing the server, we need an automata for the clients
    """

    def __init__(self, graph):
        self.graph = graph

    def get_starting_node(self):
        return 'Node A'

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
        edges = self.graph[node]
        if edges is None:
            return []
        conditions = [e.split('/')[0] for e in edges]  # 0:condition, 1:action
        return [c for c in conditions if c]

    def node_get_conditionnal_edges_for_client(self, node, client):
        client_conditions = []
        for c in self.node_get_conditionnal_edges(node):
            if client == int(c.split(':')[0].lstrip('#')):
                client_conditions.append(c.split(':')[1])
        return client_conditions

    def node_get_action_edges(self, node):
        edges = self.graph[node]
        if edges is None:
            return []
        actions = [e.split('/')[1] for e in edges]  # 0:condition, 1:action
        return [a for a in actions if a]

    def get_clients_ids(self, node):
        clients = set()
        for e, v in self.graph[node].items():
            action, condition = e.split('/')
            if not action == "":
                chaine = action
            elif not condition == "":
                chaine = condition
            else:
                continue
            client_id = int(chaine.split(':')[0].lstrip('#'))
            clients.add(client_id)
        return clients

    def get_next_from_action_edge(self, node, action):
        for e, v in self.graph[node].items():
            if e.split('/')[1].split(':')[1] == action:
                #print "Now node is ", v
                return v

    def next_from_conditionnal_edge(self, node, condition):
        for e, v in self.graph[node].items():
            if e.split('/')[0].split(':')[1] == condition:
                #print "Now node is ", v
                return v


def Error(s):
    print(s)
    exit(1)


class SibylServerTestCase(unittest.TestCase):

    print ("Module in test: " + inspect.getfile(SibylServerTcpBinProtocol))
    
    def init_clients(self, clients):
        for c in clients:
            self.protocols[c] = (self.factory.buildProtocol(('127.0.0.1', 0)),
                                 proto_helpers.StringTransport())
            self.protocols[c][0].makeConnection(self.protocols[c][1])
            #print "Initializing ... client:#", c

    def setUp(self):
        time.time=mytime
        self.factory = SibylTcpSeverProtocolFactory(SibylServerTcpBinProtocol,
                                                    SibylBrain(False))
        self.protocols = {}

    def test_sibyl_no_framing(self):

        self.st = open(os.path.join(os.getenv("STOCKRSMPATH"), "sibyl", "test", "servertestnoframing.yaml"))

        self.framing = False
        self._sibyl_test()

    def test_sibyl_framing(self):

        self.tests_counter = 0
        self.st = open(os.path.join(os.getenv("STOCKRSMPATH"), "sibyl", "test", "servertest.yaml"))

        self.framing = True
        self._sibyl_test()

    def _sibyl_test(self):

        mygraph = yaml.load(self.st)
        automata = ClientsAutomata(mygraph)
        current_node = automata.get_starting_node()
        clients = set()
        while True:
            if automata.node_has_no_edges(current_node):
                return
            if automata.node_has_illegal_edges(current_node):
                Error('graph has illegal edges')
            clients_from_node = automata.get_clients_ids(current_node)
            self.init_clients(clients_from_node - clients)
            clients = clients | clients_from_node

            if automata.node_has_conditionnal_edges(current_node):
                success = False
                for client in clients_from_node:
                    val = self.protocols[client][1].value()
                    trval = ""
                    for i in val:
                        trval = trval + "{0:#0{1}x}".format(i, 4)[2:]
                    val = trval
                    if not val == "":
                        success = True
                        client_conditions = automata.node_get_conditionnal_edges_for_client(current_node, client)
                        assert(client_conditions)
                        match = False
                        for c in client_conditions:
                            if c == val:
                                if self.framing:
                                    self.tests_counter += 1
                                self.assertEqual(c, val)
                                if self.framing and self.tests_counter == 1:
                                    print("\n\t *** First framing test passed: congratulations !")
                                elif self.framing and self.tests_counter == 2:
                                    print("\n\t *** Second framing test passed: congratulations !")
                                match = True
                                current_node = automata.next_from_conditionnal_edge(current_node, c)
                                self.protocols[client][1].clear()
                                break
                        if not match:
                            self.assertEqual(val, client_conditions[0])
                        else:
                            break
                if success == False:
                    Error('nothing returned')

            elif automata.node_has_action_edges(current_node):
                if len(automata.node_get_action_edges(current_node)) != 1:
                    Error('no more than 1 action edge')
                else:
                    e = automata.node_get_action_edges(current_node)[0]
                    e = e.split(':')[1]
                    client = clients_from_node.pop()
                    s = bytes()
                    for i in range(0, len(e), 2):
                        abyte = bytes([int(e[i: i + 2], 16)])
                        if self.framing and self.tests_counter == 0:
                            self.protocols[client][0].dataReceived(abyte)
                        else:
                            s = s + abyte
                    if (not self.framing) or (self.framing and self.tests_counter > 0):
                        self.protocols[client][0].dataReceived(s)
                    current_node = automata.get_next_from_action_edge(current_node, e)


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


# def bs_to_hs(s):
#     hs = []
#     for b in binstring_to_b_seq(s):
#         hs.append(chr(b))
#     hs_nox = ''
#     for s in hs:
#         hs_nox = hs_nox + s[0:]
#     return hs_nox


def binstring_to_b_seq(s):
    '''s is a bin string (010111001 ...) that will be
    converted to a sequence of bytes'''
    i = 0
    bseq = []
    while (i < len(s)):
        bseq.append(int(s[i:i + 8], 2))
        i += 8
    return bseq
