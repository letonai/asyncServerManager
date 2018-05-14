#!/usr/bin/python
# -*- coding: utf-8 -*-
import shutil
import sys
import subprocess
import os



def run(path):
        try:
                return str(os.listdir("/apps"))
        except Exception as err:
                return "FileSystem Error"

