#!/usr/bin/python

import socket
import time
import sys


settings = list()

for line in file('forward.conf'):
	parts = line.split(":")
	settings.append((int(parts[0]), parts[1], int(parts[2])))

print(settings)