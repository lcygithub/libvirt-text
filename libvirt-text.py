#!/usr/bin/python
#-*- coding:utf8-*-
'''
    libvirt-text.py
    ~~~~~~~~~~~~~~~~

    note the detail

    :copyright: (c) 2012 by Liu Chongyang.
    :license: BSD, see LICENSE for more details.
'''
import libvirt
import sys
if __name__ == "__main__":
    # connection
    conn = libvirt.open("qemu:///system")
    if conn == None:
        print "Failed"
        sys.exit(1)

    # create new guest domains
    demoxml1 = '''
    <domain type='kvm'>
      <name>demo1</name>
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
            <source file='/var/lib/libvirt/images/lcyang.img'/>
            <target dev='hda'/>
        </disk>
        <interface type='network'>
          <mac address='52:54:00:19:25:7b'/>
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
        <graphics type='vnc' port='5910' listen='0.0.0.0'/>
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
    </domain>
    '''
    newdom = conn.createLinux(demoxml1, 0)
    if newdom == None:
        print "failed"
        sys.exit(1)

    # domain
    dom = conn.lookupByName("lcy")

    #1.create
    dom.create()
    #2.suspend
    dom.suspend()
    #3.resume()
    dom.resume()
    #4.shutdown
    dom.shutdown()
    #5.shutoff
    dom.destroy()

    #info
    dom.info()[0]
    # libvirt定义的状态
    # virDomainStateenum virDomainState {
    #   VIR_DOMAIN_NOSTATE = 0 : no state
    #   VIR_DOMAIN_RUNNING = 1 : the domain is running
    #   VIR_DOMAIN_BLOCKED = 2 : the domain is blocked on resource
    #   VIR_DOMAIN_PAUSED = 3 : the domain is paused by user
    #   VIR_DOMAIN_SHUTDOWN = 4 : the domain is being shut down
    #   VIR_DOMAIN_SHUTOFF = 5 : the domain is shut off
    #   VIR_DOMAIN_CRASHED = 6 : the domain is crashed
    # }
