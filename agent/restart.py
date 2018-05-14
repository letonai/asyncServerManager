#!/usr/bin/python
# -*- coding: utf-8 -*-
import shutil
import sys
import subprocess




def run(path):
        try:
		cmd = subprocess.Popen(['/apps/PE/Profiles/Acsele/bin/stopServer.sh','AcselePE','-username','automated_deploy','-password','p@ssw0rd10'],stdout=subprocess.PIPE)
		ret = cmd.communicate()
		s = subprocess.Popen(['sleep','3'],stdout=subprocess.PIPE)
		cmd1= subprocess.Popen(['/apps/PE/Profiles/Acsele/bin/startServer.sh','AcselePE'],stdout=subprocess.PIPE)
                return ret[0]+str(cmd1.communicate())
        except Exception as err:
                return "Error: "+str(err)

