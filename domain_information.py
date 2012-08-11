#!/usr/bin/python
#-*- coding:utf8-*-
'''
    libvirt-text.py
    ~~~~~~~~~~~~~~~~

    note the detail

    :copyright: (c) 2012 by Liu Chongyang.
'''
import libvirt
import sys
import libxml2


def usage():
    print "Usage: %s Domain" % sys.argv[0]
    print "    print information about the domain Domain"


def print_section(title):
    print "\n%s\n" % title
    print "=" * 60


def print_entry(key, value):
    print "%-10s %-10s" % (key, value)


def print_xml(key, ctx, path):
    res = ctx.xpathEval(path)
    if res is None or len(res) == 0:
        value = "Unknwon"
    else:
        value = res[0].content
    print_entry(key, value)
    return value

if len(sys.argv) != 2:
    usage()
    sys.exit(1)

name = sys.argv[1]

#connect to libvirtc

conn = libvirt.open("qemu:///system")
if conn == None:
    print "failed"
    sys.exit(2)

try:
    dom = conn.lookupByName(name)
except libvirt.libvirtError:
    print "Domain %s is not runing" % name
    sys.exit(3)

info = dom.info()

print_section("Domain info")
print_entry("State:", info[0])
print_entry("MaxMem:", info[1])
print_entry("usedMem:", info[2])
print_entry("VCPus:", info[3])

#Read some info from the XML desc
xmldesc = dom.XMLDesc(0)
doc = libxml2.parseDoc(xmldesc)
ctx = doc.xpathNewContext()
print_section("Kernel")
print_xml("Type:", ctx, "/domain/os/type")
print_xml("Boot:", ctx, "/domain/os/boot/@dev")
print_xml("Kernel:", ctx, "/domain/os/kernel")
print_xml("initrd:", ctx, "/domain/os/inirtd")
print_xml("cmdline:", ctx, "/domain/os/cmdline")

print_section("devices")
devs = ctx.xpathEval("/domain/devices/*")
for d in devs:
    ctx.setContextNode(d)
    #pdb.set_trace()
    type = print_xml("type:", ctx, "@type")
    if type == "file":
        print_xml("source:", ctx, "source/@file")
        print_xml("Target:", ctx, "target/@dev")
    elif type == "block":
        print_xml("Source:", ctx, "source/@dev")
        print_xml("Target:", ctx, "source/@dec")
    elif type == "bridge":
        print_xml("Source", ctx, "source/@bridge")
        print_xml("MAC Addr:", ctx, "mac/@address")
    elif type == "vnc":
        print_xml("address", ctx, "listen/@address")
