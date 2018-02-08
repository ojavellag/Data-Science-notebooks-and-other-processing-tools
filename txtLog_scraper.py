#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 13:10:03 2018

@author: oavellagonzalez

this script creates a class to extract all
relevant information from a txt
file

"""

import os
import sys
import glob
import re
import datetime
import logging

class CiftiLog(object):

    _MAYBE_HALTED = "the process may have halted."
    _RUNNING = "The job is running."
    _TIMEDOUT = "the processing halted at {}"
    _ERROR = "Exited with error."

    def __init__(self, hcp_subj_folder):
        self._path = hcp_subj_folder
        self.content = self.parse_cif_rec_all(os.path.join(hcp_subj_folder,'cifti_recon_all.log'))
        self.start   = self.get_time(self.content,'Starting')
        self.done    = self.get_time(self.content,'Done')
        self.sysInfo = self.get_args(self.content,'System Info:')
        self.FS_Info = self.get_args(self.content,'freesurfer:')
        self.Cifty_Info = self.get_args(self.content,'ciftify:')
        self.wb_Info = self.get_args(self.content,'wb_command:')
        self.FSL_Info = self.get_args(self.content,'FSL:')
        self.subj_Info = self.get_args(self.content,'Arguments:')

    def get_args(self,parsed_list,arg_key):
        argum={}

        for i in range(len(parsed_list)):
            line=parsed_list[i]
            if(arg_key in line):
                if (arg_key == "System Info:"):
                    argum['Username']=parsed_list[i-1].split(None, 2)[1]
                    argum['OS']=parsed_list[i+1].split(None, 2)[1]
                    argum['Hostname']=parsed_list[i+2].split(None, 2)[1]
                    argum['Release']=parsed_list[i+3].split(None, 2)[1]
                    argum['Version']=parsed_list[i+4].split(None, 2)[1]
                    argum['Machine']=parsed_list[i+5].split(None, 2)[1]
                elif arg_key =='ciftify:':
                    argum['Version']=parsed_list[i+1].split(None, 2)[1]
                elif arg_key =='wb_command:':
                    argum['Path']=parsed_list[i+1].split(None, 2)[1]
                    argum['Version']=parsed_list[i+2].split(None, 2)[1]
                    argum['commit date']=parsed_list[i+3].split(None, 2)[2]
                    argum['OS']=parsed_list[i+4].split(None, 2)[1]
                elif arg_key =='freesurfer:':
                    argum['Path']=parsed_list[i+1].split(None, 2)[1]
                    argum['Built Stamp']=parsed_list[i+2].split(None, 2)[2]
                elif arg_key =='FSL:':
                    argum['Path']=parsed_list[i+1].split(None, 2)[1]
                    argum['Version']=parsed_list[i+2].split(None, 2)[1]
                elif arg_key =='Arguments:':
                    argum['subject:']=parsed_list[i+3].split(None, 2)[1]
                    argum['fs_subj_dir']=parsed_list[i+1].split(None, 2)[2]
                    argum['hcp_subj_dir']=parsed_list[i+2].split(None, 2)[2]
                break
        return argum


    def get_time(self,parsed_list,time_point):
        time_stamp={}
        for i in range(len(parsed_list)):
            line=parsed_list[i]
            if(time_point in line):
                line=line.split(None, 2)[0:2]
                time_stamp[time_point]=line
                break
        return time_stamp


    def parse_cif_rec_all(self, log_script):
        recon_contents = self.read_log(log_script)

        if len(log_script) < 2:
            # If length is less than two, log is malformed and will cause a
            # crash when the for loop is reached below
            return []
#        parsed_contents =  recon_contents
        parsed_contents = []
#       Skip first 10 lines, which is just a bunch of dashes
        for i in range(10,len(recon_contents)):
            fields = recon_contents[i].strip('\n')#.split(None, 1)
#            print(fields)
            parsed_contents.append(fields)

        return parsed_contents


    def read_log(self, path):
        try:
            with open(path, 'r') as log:
                contents = log.readlines()
        except IOError:
            return []
        return contents


#
