#!/usr/bin/python
# -*- coding: utf-8 -*-
import shutil
import sys
import subprocess

def run(path):
        try:
		cmd = subprocess.Popen(['/apps/ONLINE/Profiles/Acsele/bin/startServer.sh','Acsele'],stdout=subprocess.PIPE)
		ret = cmd.communicate()
                return ret[0]#+str(cmd1.communicate())
        except Exception as err:
                return "Error: "+str(err)

