#!/usr/bin/python
#-*- coding:utf8-*-
'''
    vmcontrol.py
    ~~~~~~~~~~~~~~~~

    note the detail

    :copyright: (c) 2012 by Liu Chongyang.
'''
import libvirt
# import sys
import os
import shutil


class VMControl:
    def __init__(self, exdir="/home/lcyang/vms/exps/", \
                        template="/home/lcyang/vms/templates/tinycore.img", \
                        userid="lcyang", exid="ex1"):
        '''
            exdir:  experiment dir
            template  template dir
            userid  user id
            exid  experiment id
        '''
        self.user = userid
        self.exdir = exdir
        self.exaddr = exdir + self.user + ".img"
        self.tepaddr = template
        self.exid = exid
        self.conn = libvirt.open("qemu:///system")
        if self.conn == None:
            return {"ok": False, "errmsg": "Failed connect to qemu:///system"}
        self.STATUS = ["No state",
                        "The domain is running",
                        "The domain is blocked on resource",
                        "The domain is paused by user",
                        "The domain is being shut down",
                        "The domain is shut off",
                        "The domain is crashed"]
        print "user:", self.user
        print "experiment id:", self.exid
        if os.path.isfile(self.exaddr):
            print "experiment addr:", self.exaddr, " [exit]"
        else:
            print "experiment addr:", self.exaddr
        print "template addr:", self.tepaddr
        print "connection:", self.conn

    #configure
    def config(self, interface="network", mac="52:54:00:19:25:7b",
                gtype='vnc', gport='5910', glisten='0.0.0.0'):
        self.interface = interface
        self.gtype = gtype
        self.gport = gport
        self.glisten = glisten
        self.mac = mac
        self.xmldesc = '''
          <domain type='kvm'>
          <name>%s</name>
          <memory>524288</memory>
          <currentMemory>524288</currentMemory>
          <vcpu>1</vcpu>
          <os>
            <type arch='x86_64' machine='pc-0.14'>hvm</type>
            <boot dev='hd'/>
            <bootmenu enable='no'/>
          </os>
          <features>
            <acpi/>
            <apic/>
            <pae/>
          </features>
          <clock offset='localtime'/>
          <on_poweroff>destroy</on_poweroff>
          <on_reboot>restart</on_reboot>
          <on_crash>restart</on_crash>
          <devices>
            <emulator>/usr/bin/kvm</emulator>
            <disk type='file' device='disk'>
                <source file='%s'/>
                <target dev='hda'/>
            </disk>
            <interface type='%s'>
              <mac address='%s'/>
              <source network='default'/>
              <model type='virtio'/>
              <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
            </interface>
            <serial type='pty'>
              <target port='0'/>
            </serial>
            <console type='pty'>
              <target type='serial' port='0'/>
            </console>
            <input type='tablet' bus='usb'/>
            <input type='mouse' bus='ps2'/>
            <graphics type='%s' port='%s' listen='%s'/>
            <sound model='ac97'>
              <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
            </sound>
            <video>
              <model type='cirrus' vram='9216' heads='1'/>
              <address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>
            </video>
            <memballoon model='virtio'>
              <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x0'/>
            </memballoon>
          </devices>
        </domain>''' % (self.user, \
                        self.exaddr, \
                        self.interface,\
                        self.mac, \
                        self.gtype, \
                        self.gport, \
                        self.glisten)
        print self.xmldesc

    #clone
    def clone(self):
        print "clone"
        try:
            self.dom = self.conn.lookupByName(self.user)
            return {"ok": False, "errmsg": "Failed to clone the domain is already exit"}
        except libvirt.libvirtError:
            pass
        try:
            if not self.xmldesc:
                return {"ok": False, "errmsg": "Please config vm firstly."}
        except:
            return {"ok": False, "errmsg": "Please config vm firstly."}
        if os.path.isfile(self.exaddr):
            print "delete ", self.exaddr
            os.remove(self.exaddr)
        print "copy from ", self.tepaddr, " to ", self.exaddr
        shutil.copy(self.tepaddr, self.exaddr)
        if not os.path.isfile(self.exaddr):
            return {"ok": False, "errmsg": "Can not copy template to experiment dir %s." % self.exdir}
        print "create dom"
        try:
            self.dom = self.conn.defineXML(self.xmldesc)
        except libvirt.libvirtError:
            self.dom = self.conn.lookupByName(self.user)
        if self.dom == None:
            return {"ok": False, "errmsg": "Failed to create dom"}
        print self.exdir, ":", os.listdir(self.exdir)
        return {"ok": True}

    #start
    def start(self):
        print "start"
        try:
            if self.dom.info()[0] == 6:
                return {"ok": False, "msg": "The domain is crashed"}
            elif self.dom.info()[0] != 5:
                return {"ok": False, "msg": "The domain is already start"}
            elif self.dom.info()[0] == 5:
                if self.dom.create() == 0:
                    return {"ok": True, "msg": "Starting..."}
                else:
                    return {"ok": False, "msg": "Failed to start the domain"}
        except:
            return {"ok": False, "msg": "No domain"}

    #stop
    def stop(self):
        print "stop"
        try:
            if self.dom.info()[0] == 5:
                return {"ok": False, "msg": "The domain is already stoped"}
            elif self.dom.info()[0] == 4:
                return {"ok": False, "msg": "The domain is being shut down"}
            elif self.dom.info()[0] == 3:
                return {"ok": False, "msg": "The domain is paused by user"}
            elif self.dom.info()[0] == 1:
                if self.dom.shutdown() == 0:
                    if self.dom.info()[0] == 1:
                        if self.dom.destroy() == 0:
                            if self.dom.info()[0] == 5:
                                return {"ok": True}
                    elif self.dom.info()[0] == 4:
                        while self.dom.info()[0] == 4:
                            pass
                        if self.dom.info()[0] == 5:
                            return {"ok": True}
                    else:
                        return {"ok": False, "msg": "Can not stop domain"}
                else:
                    return {"ok": False, "msg": "Can not stop domain"}
        except:
            return {"ok": False, "msg": "No domain"}

    #shutoff
    def shutoff(self):
        print "shutoff"
        try:
            if self.dom.info()[0] != 5:
                if self.dom.destroy() != 0:
                    return {"ok": False, "msg": "Can not shutoff"}
                return {"ok": True}
        except:
            return {"ok": False, "msg": "No Domain"}

    #restart
    def restart(self):
        print "restart"
        try:
            if self.dom.info()[0] == 1:
                if self.dom.shutdown() == 0:
                    while self.dom.info()[0] == 1:
                        pass
                    if self.dom.info()[0] == 5:
                        if self.dom.create() != 0:
                            return {"ok": False, "msg": "Can not start the domain"}
                        return {"ok": True}
                    elif self.dom.info()[0] == 6:
                        return {"ok": False, "msg": "The domain is crashed"}
                    else:
                        return {"ok": False, "msg": "Error but not crashed"}
                else:
                    return {"ok": False, "msg": "can not stop the dom"}
            elif self.dom.info()[0] == 3:
                if self.dom.destroy() != 0:
                    return {"ok": False, "msg": "Can not shutoff the domain"}
                else:
                    if self.dom.info()[0] == 5:
                        if self.dom.create() != 0:
                            return {"ok": False, "msg": "Can not start the domain"}
                        return {"ok": True}
            else:
                self.start()
        except AttributeError:
            print "open file"
            try:
                print "defineXML"
                try:
                    if self.xmldesc:
                        pass
                except AttributeError:
                    return {"ok": False, "msg": "No ddomain and please configure firstly"}
                self.dom = self.conn.defineXML(self.xmldesc)
                if self.dom == None:
                    return {"ok": False, "msg": "Failed create dom"}
                if self.dom.create() == 0:
                        return {"ok": True}
            except libvirt.libvirtError:
                try:
                    print "lookupByName"
                    self.dom = self.conn.lookupByName(self.user)
                    if self.dom == None:
                        return {"ok": False, "msg": "Failed create dom"}
                    if self.dom.create() == 0:
                        return {"ok": True}
                except AttributeError:
                    return {"ok": False, "msg": "No ddomain and please configure firstly"}

    #delete
    def delete(self):
        print "delete"
        try:
            print "/home/lcyang/vms/exps/:",
            os.remove(self.exaddr)
            print os.listdir("/home/lcyang/vms/exps/")
        except:
            print "Failed remove"

    #status
    def status(self):
        print "status"
        try:
            return  {"staid": self.dom.info()[0], "stamsg": self.STATUS[self.dom.info()[0]]}
        except AttributeError:
            return "No domain"

    #getIP
    def getIP(self):
        print "getIP"
