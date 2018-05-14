#!/usr/bin/python
# -*- coding: utf-8 -*-
import shutil
import sys
import subprocess
import os


#WLP_USER_DIR=/opt/wlp-apps/MX/ONLINE/ /opt/IBM/WLP/bin/server stop pims-online
#WLP_USER_DIR=/opt/wlp-apps/MX/ONLINE/ /opt/IBM/WLP/bin/server stop pims-insurance
#/apps/ONLINE/Profiles/Acsele/bin/stopServer.sh Acsele -username admin_a71278 -password Cardif2016
os.putenv("WLP_USER_DIR","/opt/wlp-apps/MX/ONLINE/")


def run(path):
        try:
		libertyonlinecmd = subprocess.Popen(['/opt/IBM/WLP/bin/server','start','pims-online'],stdout=subprocess.PIPE)
		libertyonlineret = libertyonlinecmd.communicate()
                #libertyonlinestartcmd = subprocess.Popen(['WLP_USER_DIR=/opt/wlp-apps/MX/ONLINE/ /opt/IBM/WLP/bin/server stop pims-online','start','pims-online'],stdout=subprocess.PIPE)
                #libertyonlinestartret = cmd.communicate()
                return str(libertyonlineret)
        except Exception as err:
                return "Error: "+str(err)

