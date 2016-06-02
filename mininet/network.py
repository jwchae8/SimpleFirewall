#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.util import quietRun
from mininet.moduledeps import pathCheck

from sys import exit
import os.path
from subprocess import Popen, STDOUT, PIPE

IPBASE = '10.3.0.0/16'
ROOTIP = '10.3.0.100/16'
IPCONFIG = './IP_CONFIG'
IP_SETTING={}

class simpleTopo(Topo):
    "Simple topology for running firewall"

    def __init__(self, *args, **kwargs):
        Topo.__init__(self, *args, **kwargs)
        host1 = self.addHost('host1')
        host2 = self.addHost('host2')
        host3 = self.addHost('host3')
        firewall = self.addSwitch('sw0')
        for h in host1, host2, host3:
            self.addLink(h, firewall)

class simpleController(Controller):
    "Simple controller for running firewall"

    def __init__(self, name, inNamespace=False, command='controller', cargs='-v ptcp:%d',
                cdir=None, ip="127.0.0.1", port=7878, **params):
        Controller.__init__(self, name, ip=ip, port=port, **params)

    def start(self):
        pathCheck(self.command)
        cout = '/tmp/' + self.name + '.log'
        if self.cdir is not None:
            self.cmd('cd' + self.cdir)
        self.cmd(self.command, self.cargs % self.port, '>&', cout, '&')

    def stop(self):
        self.cmd('kill %' + self.command)
        self.terminate()

def set_default_route(host):
    info('*** setting default gateway of host %s\n' % host.name)
    if(host.name == 'host1'):
        routerip = IP_SETTING['sw0-eth1']
    elif(host.name == 'host2'):
        routerip = IP_SETTING['sw0-eth2']
    elif(host.name == 'host3'):
        routerip = IP_SETTING['sw0-eth3']
    print host.name, routerip
    host.cmd('route add %s/32 dev %s-eth0' % (routerip, host.name))
    host.cmd('route add default gw %s dev %s-eth0' % (routerip, host.name))
    ips = IP_SETTING[host.name].split(".") 
    host.cmd('route del -net %s.0.0.0/8 dev %s-eth0' % (ips[0], host.name))

def get_ip_setting():
    try:
        with open(IPCONFIG, 'r') as f:
            for line in f:
                if( len(line.split()) == 0):
                  break
                name, ip = line.split()
                print name, ip
                IP_SETTING[name] = ip
            info( '*** Successfully loaded ip settings for hosts\n %s\n' % IP_SETTING)
    except EnvironmentError:
        exit("Couldn't load config file for ip addresses, check whether %s exists" % IPCONFIG_FILE)

def simplenet():
    get_ip_setting()
    topo = simpleTopo()
    info( '*** Creating network\n' )
    net = Mininet( topo=topo, controller=RemoteController, ipBase=IPBASE )
    net.start()
    host1, host2, host3, firewall = net.get( 'host1', 'host2', 'host3', 'sw0')
    h1intf = host1.defaultIntf()
    h1intf.setIP('%s/8' % IP_SETTING['host1'])
    h2intf = host2.defaultIntf()
    h2intf.setIP('%s/8' % IP_SETTING['host2'])
    h3intf = host3.defaultIntf()
    h3intf.setIP('%s/8' % IP_SETTING['host3'])


    for host in host1, host2, host3:
        set_default_route(host)
    CLI( net )
    net.stop()


if __name__ == '__main__':
    setLogLevel( 'info' )
    ee323net()






