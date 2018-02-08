# -*- coding: utf-8 -*-

"""
Created on Thu Dec 28 09:55:19 2017
@author: Oscar Javier Avella Gonzalez
#
"""

import os, os.path
import numpy as np
import pandas as pd

"""
    Short-cut to open any csv, providing the full
    path to the file and the desired separator
    to use e.g. '\t'," ", "," etc.
"""
def open_file(csv_file,separ):
    readCSV = pd.read_csv(csv_file,sep=separ,error_bad_lines=False)
    return readCSV


    """
    Function specifically used here to extract the
    blacklisted files contained in the blacklist.csv
    of the project
    """
def get_list_of_Files(csv_file):

    """csv_file => full path to the blacklist file"""
    bl_list=csv_file.iloc[:,(0)]
    bl_names=[]
    temp_s=" "
    for s in bl_list:
        temp_s=s.split(' ')[0]
        if(temp_s.split('\t')):
            temp_s=temp_s.split('\t')[0]
        bl_names.append(temp_s)
    return bl_names


"""
    Explores all subdirs in a given folder and
    collects the filenames in that folder including
    extensions
"""
def files_in_path(Dir):
    """Dir => it is recommended to use the full path
       although relative paths are also valid"""
    filesIn=[]
    for directory, dirnames, filenames in os.walk(Dir):
        filesIn.append(filenames)
    return filesIn

def get_subjects_by_site(Study_path,sites):
    """
        This function collect the valid subjects
        in a given folder, excluding any possible
        phantom in the list
        Input
        Study_path => /path/tho/the/folder/of/interest/
        sites => list with all site-labels
    """
    subjects= []
    subjects.append(os.listdir(Study_path))
    is_phan='_P'
    sites_count = []
    sites_list = []
    for site in sites:
        site_list_temp = []
        c=0
#        print(site)
        for subjectName in subjects[0]:
            if site in subjectName and is_phan not in subjectName:
                c+=1
                site_list_temp.append(subjectName)
        sites_list.append(site_list_temp)
        sites_count.append(c)
    return sites, sites_count, sites_list



def find_filename(ref_files, files_in_dir):
    """
        Helper function to check blacklisted files in the project's path.
        Inputs
            ref_files    => list of reference files (e.g. blacklist.csv)
            files_in_dir => list of files found in the target dir
            found_files  => list of coincidence
            not_found    => list of files in the target path not in
                            the blacklist.
    """
    found_files = []
    not_found = []
    for s in files_in_dir:
        for s1 in ref_files:
            if s1 in s:
                print(s, s1," found")
                found_files.append([s1,s])
            else:
                 not_found.append([s1,s])
    return found_files, not_found

def find_blackListed_files_in_study(refeFiles,targetFiles):
    """
        Main function used to inspect blacklisted files possibly
        present in the project's path (nii/).
    """
    found=[]
    notFound=[]
    for i in (0,len(targetFiles)-1):
        found, notFound = find_filename(refeFiles, targetFiles[i][:])
    print(i)
    return found, notFound

blacklist_file='/location/of/file/blacklist.csv'
Study_path = '/location/of/files/with/type/nii/'
blacklist=open_file(blacklist_file," ")
bl_files=get_list_of_Files(blacklist)
FilesIN_Study=files_in_path(Study_path)


""" Remove artifact line created in the files found in the path """
del FilesIN_Study[0]
blacklisted_files, no_bl_files =  find_blackListed_files_in_study(bl_files,
                                                                  FilesIN_Study)
"""
    Up to this point the script only checks for consistency of the valid subjects
"""


def exclude_subjects(study_path, csv_file, col_label):
    """
     This function compares the dir_names in the study folder against
     those in the demographic info file, removes phantoms, "9999"
     and those with 2 and 8 in the "term_early_withdraw" column
     Inputs
         study_path= > Project's folder
        csv_file  = > Demographic info file (csv)
        col_label = > column  in the csv_file with the inclussion criteria
    Outputs
        SubjIn = >        list of subjects (subfolders) in the project's path (nii/)
        valid_subj = >    list with the name of subjects not satisfying exclusion
                          nor belonging to the blackfile list
        files2Exclude = > List of subjects (subfolders) that satisfy the exclusion
       criteria
    """

    SubjIn = []
    for directory, dirnames, filenames in os.walk(study_path):
        s_temp = directory.split('/')[len(directory.split('/'))-1]
        if "_P" not in s_temp and "_9999" not in s_temp:
            SubjIn.append(s_temp)
    files2Exclude = list(csv_file[csv_file[col_label].isin([2,8])].iloc[:,(0)])
    SubjIn = remove_ending0(SubjIn)
    valid_subj = list(filter(lambda x: x not in files2Exclude,SubjIn))

    return SubjIn, valid_subj, files2Exclude


def Valid_Subjects_by_condition(valid_subjects,condit):
    """
        Helper function used to
        classify subjects by site

        inputs
        valid_subjects => list of all subjects with valid demogr. info
        condit => uses the list of site names and loops over it

        outputs
        condit_count => number of subjects by site
        condit_list => list of subject-names by site
    """
    condit_list = []
    condit_count = []
    for site in condit:
        site_list_temp = []
        c=0
#        print(site)
        for subject in valid_subjects:
            if site in subject:
                c+=1
                site_list_temp.append(subject)
        condit_list.append(site_list_temp)
        condit_count.append(c)
    return condit_count, condit_list



def check_difference(data1,data2):
    """
        function to check the difference betwween the content of two lists
        i.e. it calculates the elements of data2 not in data1
    """
    difference = list(filter(lambda x: x not in data1,data2))
    return difference

def check_coincidence(data1,data2):
    """
        function to check the intersection betwween the content of two lists
        data1 and data2

    """
    coincidence = list(filter(lambda x: x in data1,data2))
    return coincidence


def remove_ending0(string1):
    """
        this function removes the ending of the session in the folder
        in order to extract the name of the subject. This is internally
        used by exclude_subjects
        input:
        string1 => expects a folder name with sesssion number at the end
        output:
        a => folder name without session number
    """
    a=[]
    sess = ['01','02','03','04','05','06','07','08']
    for str_t in string1:
        str2 = str_t.split("_")
        if str2[len(str2)-1] in sess:
            del str2[len(str2)-1]
            str3 = "_".join(str2)
            a.append(str3)
        else:
            a.append(str_t)
    return a

def DemogInfo(subject,demog_file,col_label,subj_names):
    """
        Helper function to pair demographic information
        for each subject associated to birth gender and population
        it belongs to; i.e. control/patient

        input:
            subject    => string with the subject-id of interest
            demog_file => path to the csv file with demographic info
            col_label  => label of the column with subject-names
            subj_names => list with all subject names
        output:
            gend       => returns the gender of the subject of interest
            rc_event   => returns the population of the subject of interest
    """
    if subject in subj_names:
        gend = list(demog_file[demog_file[col_label].isin([subject])].iloc[:,(2)])
        gend=gend[0]
        rc_event = list(demog_file[demog_file[col_label].isin([subject])].iloc[:,(1)])
        rc_event = rc_event[0]
    else:
        gend = 0
        rc_event = 0

    return gend, rc_event


def get_DemogrAndScans(subjects_list,study_path,demogFile):
    """
    This function combines info from files in path and demographics
    to produce a combined output for the analysis.
    Inputs
        subjects_list => list of subject-id's
        study_path => absolute path to the base (study -nii)  directory
        demogFile => datasheet (csv) with demographic info
    Outputs
        subjScans => list of subject-id's paired with demog. info.
    """
    subjScans = []
    base_ext='.nii.gz'
    sub_names = list(demogFile.iloc[:,(0)])
    file_types = ["_T1_","_T2_","_DTI","_EMP_","_IMI_","_OBS_","_RST_","_FLAIR_"]
    for subject in subjects_list:
        dir_name = study_path+subject+"_01/"
        found_files =  files_in_path(dir_name)
        found_files = [j for i in found_files for j in i]
        t1_c, t2_c, dti_c, emp_c, im_c, obs_c, rst_c, flair_c = 0,0,0,0,0,0,0,0
        gend, rc_event = DemogInfo(subject,demogFile,
                                   demogFile.iloc[:,(0)].name,sub_names)
#        subjScans.append(subject)
        for fileName in found_files:
            if base_ext in fileName:
#                print(fileName)
                if (file_types[0] in fileName and fileName not in bl_files) :
                    t1_c+=1
                elif (file_types[1] in fileName and fileName not in bl_files):
                    t2_c+=1
                elif (file_types[2] in fileName and fileName not in bl_files):
                    dti_c+=1
                elif (file_types[3] in fileName and fileName not in bl_files):
                    emp_c+=1
                elif (file_types[4] in fileName and fileName not in bl_files):
                    im_c+=1
                elif (file_types[5] in fileName and fileName not in bl_files):
                    obs_c+=1
                elif (file_types[6] in fileName and fileName not in bl_files):
                    rst_c+=1
                elif (file_types[7] in fileName and fileName not in bl_files):
                    flair_c+=1
        subjScans.append([subject,gend, rc_event, t1_c, t2_c,
                          dti_c, emp_c, im_c, obs_c, rst_c, flair_c])

    return subjScans


def organize_output(table, headers=["subj","gender","case","t1","t2","dti",
                                    "emp","imi","obs","rest","flair"]):
    """
       This function organizes the output from a list of list with demographic
       and info from subjects' scans returning an organized pd.dataframe
    """
    rslt = pd.DataFrame(table,columns=headers)
    return rslt


def get_by_feature(dataframe,feature_name1, feature_val1,
                   feature_name2,feature_val2,
                   feature_name3, feature_val3):
    """
       This function takes a pandas dataframe and based on the inputs and values
        of interest produces a second filtered dataframe
        Inputs:
            dataframe
            feature_name1, feature_val1,
            feature_name2,feature_val2,
            feature_name3, feature_val3
        Output:
            df3 => filtered dataframe
    """
    df = dataframe[dataframe[feature_name1].isin(feature_val1)]
    df2 = df[df[feature_name2].isin(feature_val2)]
    df3 = df2[df2[feature_name3].isin(feature_val3)]
    return df3

def get_subjects_with_extra_scans(df,label,max_allowed):
    """
        this functions gets as its input data of interest in a pd.dataframe
        the label of the column to check and the expected number of scans per
        subject and returns a list with subject names
        Inputs
            df          => input dataframe
            label       => scan label of interest e.g. "t1" or "dti"
            max_allowed => expected number of a given scan type
        Output
        subj_names => list of subject-id's with more non-blacklisted
        scans than expected

    """

    r=range(max_allowed+1,20)
    subj_names = list(df[df[label].isin(r)].iloc[:,(0)])
    return subj_names

sites=['CMH', 'MRC', 'ZHH', 'MRP', 'ZHP']
Sites, numb_subjects,SubjectsInSite = get_subjects_by_site(Study_path,sites)

ExtraInfo=open_file('/projects/ojavellag/Desktop/spins_add_info.csv',",")

SubjectsInPath,SubjectsIncluded, SubjectsExcluded =exclude_subjects(
        Study_path, ExtraInfo, ExtraInfo.iloc[:,(3)].name)

count_by_site, subjects_by_site = Valid_Subjects_by_condition(
        SubjectsIncluded,sites)


"""Demographic info"""
Demog_info = ExtraInfo
"""subjects om the demographic SpreadSheet"""
a = list(Demog_info.iloc[:,0])
"""this is an artifact introduced during the conversion from pd. dataframe to list"""
del SubjectsIncluded[0]
"""Subject in the Spread-sheet not present in valid subjects inthe projectPath"""
df1 = check_difference(SubjectsIncluded,a)
"""Subject in the Spread-sheet not present in the projectPath"""
df2 = check_difference(SubjectsInPath,a)

site1= organize_output(get_DemogrAndScans(subjects_by_site[0],Study_path, ExtraInfo))
site2 = organize_output(get_DemogrAndScans(subjects_by_site[1],Study_path, ExtraInfo))
site3 = organize_output(get_DemogrAndScans(subjects_by_site[2],Study_path, ExtraInfo))
site4 = organize_output(get_DemogrAndScans(subjects_by_site[3],Study_path, ExtraInfo))
site5 = organize_output(get_DemogrAndScans(subjects_by_site[4],Study_path, ExtraInfo))

"""Organized dataframe list to build the statistical table of Filling_SPINS_table.py"""
SitesInfo =[site1,site2,site3,site4,site5]
