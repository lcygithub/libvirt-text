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
import os


def usage():
    print "Usage: %s DIR" % sys.argv[0]
    print "    Restore all the domains contained in DIR"
    print "    It is assumed that all files in DIR area"
    print "    images or domU\'s previously created with save"

    if len(sys.argv) != 2:
        usage()
        sys.exit(2)

dir = sys.argv[1]
imgs = os.listdir(dir)

conn = libvirt.open("qemu:///system")
if conn == None:
    print "Failed to open connection to the hypervisro"
    sys.exit(1)


for img in imgs:
    file = os.path.join(dir, img)
    print "Restoring %s..." % img,
    sys.stdout.flush()
    ret = conn.restore(file)
    if ret == 0:
        print "done"
    else:
        print "error %d" % ret
