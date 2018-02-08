#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 09:55:19 2017

@author: Oscar Javier Avella Gonzalez
"""
#
import ref_classif as sf
import pandas as pd


def remove_cols(df,cols):
    df.drop(df.columns[[cols]], axis=1, inplace=True)
    return df

def create_table(table, headers=["case","gender","scan type"
                                 ,"expected scans",
                                 "number of subjects" ]):

    rslt = remove_cols(pd.DataFrame(table,columns=headers),3)
    return rslt


def conditional_count(input_data):
    df = input_data[0]
    case_ = input_data[1]
    gendr = input_data[2]
    scan_t = input_data[3]
    site_ = input_data[4]
    data_ = []
    total_subj = []
    for group in case_:
        for gender in gendr:
            for scan in scan_t:
                """ n_scans is the minimum number of expected scans
                    however as long as they are not black listed, more scans
                    of the same type can be present in the folder
                """
                n_scans = 1
                if (scan == "t1" and (site_ == "MRC" or site_ == "MRP")) or (scan == "emp"):
                    n_scans = 3
                count = len(sf.get_by_feature(df,"case",[group],'gender',[gender],scan,range(n_scans,n_scans+3)))
                data_.append([group,gender,scan,n_scans,count])
#            this line adds the total count of subjects  in that group and gender case
                if (scan == "rest"):
                    total_subj.append(len(sf.get_by_feature(df,"case",[group],'gender',[gender],scan,range(0,10))))
    return data_, total_subj


def comprehens_table(site_info,df, subj_numb, label,scan = ["t1","t2","dti","emp","imi","obs","rest","flair"],
                     case = ["control_arm_1","case_arm_2"], gndr = [2,1] ):
    out_table = []
    cols_name = []
#    print(label)
    subj_numb[0],subj_numb[1],subj_numb[2],subj_numb[3] = subj_numb[2],subj_numb[3],subj_numb[0],subj_numb[1]
#    subj_numb.append("Number of subjects")
#    reversing the list to add row's name
    total_subj = ["Total Subjects"]+subj_numb

    complete_subj = ["complete Subjects"]+get_completeSubj(site_info,label)
#    print(total_subj)
    out_table.append(scan)
    cols_name.append("scan")
    for case_ in case:
        if case_ == case[0]:
                cse ="control"
        elif case_ == case[1]:
            cse ="patient"
        for gender in gndr:
            if gender == gndr[0]:
                sex ="m"
            elif gender == gndr[1]:
                sex="f"
            df1 = list(df[(df['case'] == case_) & (df['gender'] == gender)].iloc[:,(3)])
            out_table.append(df1)
            cols_name.append(label+"_"+cse+"_"+sex)
    pre_table = list(zip(*out_table))
    pre_table.append(total_subj)
    pre_table.append(complete_subj)
    return pd.DataFrame(pre_table,columns= cols_name)


def generateSite_tables(Sites, labels=sf.sites):
    rslt=[]
    spc = pd.DataFrame({' ':[],' ':[]})
    for i in range(0,len(Sites)):
        csv_name ='sites_table'+labels[i]+'.csv'
        site_info = Sites[i]
#        print(i)
        inputData = [site_info, ["case_arm_2", "control_arm_1"],[2,1],
              ["t1",  "t2",  "dti",  "emp",  "imi", "obs",  "rest", "flair"],labels[i]]
        cd,ts =conditional_count(inputData)
        df = create_table(cd)
        a = comprehens_table(site_info,df,ts,labels[i])
#        a.to_csv(csv_name,sep='\t', mode='a', header=True)
        comp_subj = get_completeSubj(Sites[i],labels[i])
#        spc.to_csv(csv_name,sep='\t', mode='a', header=True)

#        comp_subj.to_csv('sites_table'+labels[i]+'.csv',sep='\t', mode='a', header=True)
        rslt.append(a)
    return rslt


def get_completeSubj(siteInfo,site_name):
    scan = ["t1","t2","dti","emp","imi","obs","rest","flair"]
    case1 = ["control_arm_1","case_arm_2"]
    rslt = []
    gndr = [2,1]
    expect_vals  = [1,1,1,3,1,1,1,1]
    if (site_name == 'MRC' or site_name == 'MRP'):
        expect_vals[0]=3
    for case_ in case1:
        if case_ == case1[0]:
                cse ="control"
        elif case_ == case1[1]:
            cse ="patient"
        for gender in gndr:
            df1 = siteInfo[(siteInfo['case'] == case_) & (siteInfo['gender'] == gender)]
            df1 = df1.drop(["subj","gender","case"],axis = 1)
            df1 =df1.as_matrix()
            counter = 0
            if gender == gndr[0]:
                sex ="m"
            elif gender == gndr[1]:
                sex="f"
            for i in range(len(df1)):
#                range(0,df1.shape[0]):
                if(df1[i][0] >= expect_vals[0] and df1[i][1] >= expect_vals[1]
                    and df1[i][2] >= expect_vals[2] and df1[i][3] >= expect_vals[3]
                    and df1[i][4] >= expect_vals[4] and df1[i][5] >= expect_vals[5]
                    and df1[i][6] >= expect_vals[6] and df1[i][7] >= expect_vals[7]):
                        counter+=1
                """ ad-hoc condition for  subject SPN01_ZHP_0096 EMP"""
                if(site_name == 'ZHP' and df1[i][3] == 7 ):
                    counter+=1
#            rslt.append([counter,cse+"_"+sex])
            rslt.append(counter)
    return rslt




tables_=generateSite_tables(sf.SitesInfo)
for i in range(1,len(tables_)):
    tables_[i] = tables_[i].drop(["scan"],axis=1)

result = pd.concat([tables_[0], tables_[1],tables_[2],tables_[3],tables_[4]], axis=1, join='inner')
result.to_csv('Sites_table.csv',sep='\t', mode='a', header=True)
