#!/usr/bin/python

#  Copyright 2019-present Open Networking Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import argparse

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import Host
from mininet.topo import Topo
from stratum import StratumBmv2Switch

CPU_PORT = 255


class IPv4Host(Host):
    """Host that can be configured with an IPv4 gateway (default route).
    """

    def config(self, mac=None, ip=None, defaultRoute=None, lo='up', gw=None,
               **_params):
        super(IPv4Host, self).config(mac, ip, defaultRoute, lo, **_params)
        self.cmd('ip -4 addr flush dev %s' % self.defaultIntf())
        self.cmd('ip -6 addr flush dev %s' % self.defaultIntf())
        self.cmd('ip -4 link set up %s' % self.defaultIntf())
        self.cmd('ip -4 addr add %s dev %s' % (ip, self.defaultIntf()))
        if gw:
            self.cmd('ip -4 route add default via %s' % gw)
        # Disable offload
        for attr in ["rx", "tx", "sg"]:
            cmd = "/sbin/ethtool --offload %s %s off" % (
                self.defaultIntf(), attr)
            self.cmd(cmd)

        def updateIP():
            return ip.split('/')[0]

        self.defaultIntf().updateIP = updateIP


class TaggedIPv4Host(Host):
    """VLAN-tagged host that can be configured with an IPv4 gateway
    (default route).
    """
    vlanIntf = None

    def config(self, mac=None, ip=None, defaultRoute=None, lo='up', gw=None,
               vlan=None, **_params):
        super(TaggedIPv4Host, self).config(mac, ip, defaultRoute, lo, **_params)
        self.vlanIntf = "%s.%s" % (self.defaultIntf(), vlan)
        # Replace default interface with a tagged one
        self.cmd('ip -4 addr flush dev %s' % self.defaultIntf())
        self.cmd('ip -6 addr flush dev %s' % self.defaultIntf())
        self.cmd('ip -4 link add link %s name %s type vlan id %s' % (
            self.defaultIntf(), self.vlanIntf, vlan))
        self.cmd('ip -4 link set up %s' % self.vlanIntf)
        self.cmd('ip -4 addr add %s dev %s' % (ip, self.vlanIntf))
        if gw:
            self.cmd('ip -4 route add default via %s' % gw)

        self.defaultIntf().name = self.vlanIntf
        self.nameToIntf[self.vlanIntf] = self.defaultIntf()

        # Disable offload
        for attr in ["rx", "tx", "sg"]:
            cmd = "/sbin/ethtool --offload %s %s off" % (
                self.defaultIntf(), attr)
            self.cmd(cmd)

        def updateIP():
            return ip.split('/')[0]

        self.defaultIntf().updateIP = updateIP

    def terminate(self):
        self.cmd('ip -4 link remove link %s' % self.vlanIntf)
        super(TaggedIPv4Host, self).terminate()


class SimpleTopo(Topo):
    """Single switch connecting 4 hosts"""

    def __init__(self, *args, **kwargs):
        Topo.__init__(self, *args, **kwargs)

        # Leaves
        # gRPC port 50001
        switch1 = self.addSwitch('switch1', cls=StratumBmv2Switch, cpuport=CPU_PORT)

        # IPv4 hosts attached switch1
        h1a = self.addHost('h1a', cls=IPv4Host, mac="00:00:00:00:00:1A",
                           ip='172.16.1.1/24', gw='172.16.1.254')
        h1b = self.addHost('h1b', cls=IPv4Host, mac="00:00:00:00:00:1B",
                           ip='172.16.1.2/24', gw='172.16.1.254')
        h1c = self.addHost('h1c', cls=IPv4Host, mac="00:00:00:00:00:1C",
                           ip='172.16.1.3/24', gw='172.16.1.254')
        h1d = self.addHost('h1d', cls=IPv4Host, mac="00:00:00:00:00:20",
                           ip='172.16.1.4/24', gw='172.16.2.254')
        self.addLink(h1a, switch1)  # port 1
        self.addLink(h1b, switch1)  # port 2
        self.addLink(h1c, switch1)  # port 3
        self.addLink(h1d, switch1)  # port 4


def main():
    net = Mininet(topo=SimpleTopo(), controller=None)
    net.start()
    CLI(net)
    net.stop()
    print '#' * 80
    print 'ATTENTION: Mininet was stopped! Perhaps accidentally?'
    print 'No worries, it will restart automatically in a few seconds...'
    print 'To access again the Mininet CLI, use `make mn-cli`'
    print 'To detach from the CLI (without stopping), press Ctrl-D'
    print 'To permanently quit Mininet, use `make stop`'
    print '#' * 80


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Mininet topology script for a single switch with stratum_bmv2 and IPv4 hosts')
    args = parser.parse_args()
    setLogLevel('info')

    main()
