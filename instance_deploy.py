#!/usr/bin/env python3

import os
import shutil

def main(config_name):
    shutil.move(config_name, "/etc/rathole/")
    instance_name = config_name.split(".", -1)[0]
    os.popen(f"sudo systemctl enable ratholes@{instance_name} --now &>/dev/null")