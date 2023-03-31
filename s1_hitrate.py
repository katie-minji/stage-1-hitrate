# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 12:42:07 2022

@author: Katie Kim
"""
# =============================================================================
# 
# PLEASE READ THIS!!!
# 
# 
# << Instructions >>
# 
# Purpose: 
# This code creates hitrate for each mouse in stage1, with date/session labeled. 
# It gives baseline of 75% and scatter dots to indicate hitrate in each training trial.
#
# Batching == Possible: (options) 
# [1: by cohort --> e.g. c6 folder: mouse's stage1 training session of all mouse in cohort 6],
# [2: by mouse --> e.g. wt871_N folder: wt871_N mouse's stage1 training session] 
#
# To access:
# [SooB --> Projects --> Association --> COHORT --> MOUSE]
#
# =============================================================================


import os
from glob import glob
from tkinter import filedialog as fd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time


def data_extraction(maindir):
    os.chdir(str(maindir))  #set currently working directory to maindir
    # create dictionary of mouse, file directory, filename in stage1
    everything = list(os.walk(os.getcwd()))  #list of folder, subfolder, files
    filelist = []
    dirlist = []
    for dirpath, dirnames, filenames in everything:
        if 'wt' in os.path.basename(everything[0][0]):
            mouselist = [os.path.basename(everything[0][0])]
        else:
            mouselist = [x for x in everything[0][1]]  #list mouse in cohort
        if os.path.basename(dirpath) == 'Stage1':  #files in Stage1
            flist = [x for x in filenames if x.endswith('.txt')]
            filelist.append(flist)
            dirlist.append(dirpath)
    mylist = list(zip(dirlist,filelist))  #combine directory and files into tuples
    file_dict = {mouselist[i]: mylist[i] for i in range(len(mouselist))}  #make dictionary key=mouse, value=directory&files
    
    return file_dict


def make_dataframe(files):
    def hitrate(directory):  # extract hit rate
        hit_list = []
        miss_list = []
        temp = glob(os.path.join(directory,'*.txt'))
        for path in temp:
            with open(path) as f:
                lines = [line.rstrip() for line in f.readlines()]
                hit = [int(y.strip(" hit: ")) for y in [x for x in lines if isinstance(x,str)] if 'hit:' in y]
                miss = [int(y.strip(" miss: ")) for y in [x for x in lines if isinstance(x,str)] if 'miss:' in y]          
                hit_list.append(hit)
                miss_list.append(miss) 
        if len(hit_list) == len(miss_list):
            hit_list = [x for x in hit_list if x != []]  
            miss_list = [x for x in miss_list if x != []]  
            hit_rate_list = [hit_list[i][0]/(hit_list[i][0] + miss_list[i][0])* 100 for i in range(len(hit_list)) if (hit_list[i][0] + miss_list[i][0]) != 0]
        hit_rate_final = pd.Series(np.asarray(hit_rate_list))
        return hit_rate_final
    def df_dict():
        df_dict = {}
        final_df_dict = {}
        for mouse in files:
            day_series = pd.Series(np.asarray([y.replace('_', '-') for y in [x[0:10] for x in files[mouse][1]]]))
            time_series = pd.Series(np.asarray([y.replace('_', '') for y in [x[13:21] for x in files[mouse][1]]]))
            hit_rate_series = hitrate(files[mouse][0])
            df_dict[mouse] = pd.DataFrame({'day': day_series, 'time': time_series, 'hit rate': hit_rate_series})
            session_list = []
            df_mouse = df_dict[mouse]
            count_df = df_mouse.groupby('day').size()
            for day, day_df in df_mouse.groupby('day'):
                day_df.sort_values(by=['time'])
                session_per_day = count_df[day]
                for i in range(session_per_day):
                    session_list.append('S'+str(i+1))
            df_mouse.insert(2, "session", np.asarray(session_list))
            del df_mouse['time']
            final_df_dict.update({mouse: df_mouse})
        return final_df_dict
    final_df = df_dict()
    
    return final_df


def graphing(final_df_dict):
    for mouse in final_df_dict:
        plt.figure()
        plt.style.use('seaborn')    
        i=0
        x_axis = []
        while i < len(final_df_dict[mouse]):
            day_session = final_df_dict[mouse]['day'].iloc[i] + ', ' + final_df_dict[mouse]['session'].iloc[i]  
            x_axis.append(day_session)
            i+=1
        plt.scatter(x_axis, final_df_dict[mouse]['hit rate'])
        plt.axhline(y = 75, color = 'r', linestyle = '-')  #plot x line
        plt.gcf().autofmt_xdate()
        plt.xlabel("Training Trials", fontsize=13)
        plt.ylabel('Hit Rate', fontsize=13)
        plt.yticks(np.arange(0,101,20))
        plt.title(mouse + ' Stage 1 Hit Rate', fontsize=16) 
        plt.tight_layout()


#%%


start = time.time()


data_needed = data_extraction(fd.askdirectory())  #prints cohort, gives dictionary of all data needed
df = make_dataframe(data_needed)
graphing(df)    


end = time.time()
execution_time = time.strftime('%H:%M:%S', time.gmtime(end-start))
print(f'This took {execution_time} to run!')



    