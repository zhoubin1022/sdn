from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call


class MyTopo(Topo):
	def __init__(self):
		Topo.__init__(self)

		# loop for add hosts
		hosts = []
		for i in range(4):
			h = self.addHost('h' + str(i + 1))
			hosts.append(h)

		# loop for add switchs
		switchs = []
		for i in range(4):
			s = self.addSwitch('s' + str(i + 1))
			switchs.append(s)

		# loops for add links
		self.addLink(hosts[0], switchs[0])

		for i in range(1, 4):
			self.addLink(switchs[0], switchs[i])

		for i in range(1, 3):
			self.addLink(switchs[i], switchs[3])

		for i in range(1, 4):
			self.addLink(switchs[3], hosts[i])


topos = {'mytopo': (lambda: MyTopo())}