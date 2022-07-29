#!/usr/bin/env python3.8

import sys
import string
import random
import argparse

parser = argparse.ArgumentParser(description="Generate random password")
parser.add_argument("-n", dest="len", required=True, type=int)

args = parser.parse_args()

char = list(string.ascii_letters + string.digits)
random.shuffle(char)
password = []

for i in range(args.len):
    password.append(random.choice(char))

random.shuffle(password)
print("".join(password))