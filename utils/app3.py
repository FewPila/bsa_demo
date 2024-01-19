import pandas as pd
import numpy as np
import os
import re
import time
import streamlit as st

def assign_byIsic(*args,condition = True):
    
    def get_sna_isic(sna,isic,isic_action,sna_type):
        sna_name = 'SNA10' #init
        
        if bool(re.search("FINAL_SNA",sna_type)):
            sna_name = 'SNA'
        elif bool(re.search("FINAL_SNA10",sna_type)):
            sna_name = 'SNA10'
        
        # if have isic
        if not pd.isna(isic):
            # if isic match
            for idx,row in isic_action.iterrows():
                if bool(re.search(row.Rule,str(isic))):
                    return str(row[sna_name])
            # if don't match
            return sna
        # if don't have isic
        else: 
            return sna
        
    sna = args[0][args[1][0]]
    sna_type = args[1][0]
    nat = args[0][args[1][1]]
    isic = args[0][args[1][2]]
    isic_action = args[2]

    # assign if non-assigned-sna
    if pd.isna(sna):
        # assign only when nat
        if condition == True:
            if not pd.isna(nat):
                # if th
                th_search = bool(re.search('TH|Thai|ไทย',str(nat)))
                if th_search:
                    out =  get_sna_isic(sna,isic,isic_action,sna_type) # apply function
                # if non-th
                else:
                    out = sna
            # if non-nationalities       
            else:
                out = sna

        # assign whatever condition
        else:
            out = get_sna_isic(sna,isic,isic_action,sna_type) # apply function

    # if snaed
    else:
        out = sna

    return out

def assign_byKeywords(*args,condition = True):

    def get_sna_keywords(sna,name,keywords_action,sna_type):
        #init
        sna_name = 'SNA10'
        if bool(re.search("FINAL_SNA",sna_type)):
            sna_name = 'SNA'
        elif bool(re.search("FINAL_SNA10",sna_type)):
            sna_name = 'SNA10'
        for idx,row in keywords_action.iterrows():
            # if match
            if bool(re.search(row['Rule'],str(name))):
                return str(row[sna_name])
        # if don't match
        return sna
   
    sna = args[0][args[1][0]]
    sna_type = args[1][0]
    nat = args[0][args[1][1]]
    name = args[0][args[1][2]]
    keywords_action = args[2]
    
    # assign if non-assigned-sna
    if pd.isna(sna):
        # assign only when nat
        if condition == True:
            if not pd.isna(nat):
                # if th
                th_search = bool(re.search('TH|Thai|ไทย',str(nat)))
                if th_search:
                    out = get_sna_keywords(sna,name,keywords_action,sna_type) # apply function
                # if non-th
                else:
                    out = sna
            # if non-nationalities       
            else:
                out = sna

        # assign whatever condition
        else:
            out = get_sna_keywords(sna,name,keywords_action,sna_type) # apply function

    # if snaed
    else:
        out = sna
    return out

def assign_byMatchedSNA(*args,condition = True):
    
    sna = args[0][args[1][0]]
    nat = args[0][args[1][1]]
    matched_sna = args[0][args[1][2]]
    matched_sna = re.sub('\.+\d','',str(matched_sna))
    sna_action = args[2]
    
    if pd.isna(sna):
        # assign only when nat
        if condition == True:
            if not pd.isna(nat):
                # if th
                th_search = bool(re.search('TH|Thai|ไทย',str(nat)))
                if th_search:
                    if matched_sna != "nan":
                        out = matched_sna
                    else:
                        out = sna
                # if non-th
                else:
                    out = sna
            # if non-nationalities       
            else:
                out = sna
            
        # assign whatever condition
        else:
            if matched_sna != "nan":
                out = matched_sna
            else:
                out = sna
#            out = matched_sna
        
    # if snaed
    else:
        out = sna
    return out

def assign_byNationalities(*args,condition):

    sna = args[0][args[1][0]]
    nat = args[0][args[1][1]]
    isic = args[0][args[1][2]]

    # assign if it non-assigned-sna
    if pd.isna(sna):
        # Non-NA Nationalities
        if not pd.isna(nat):
            th_search = bool(re.search('TH|Thai|ไทย',str(nat)))
            if th_search:
                if condition == 1: # just nat == th
                    out = 'ONFC'
                elif condition == 2:  # if nat == th and isic not None
                    if not pd.isna(isic):
                        out = 'ONFC'
                    else:
                        out = sna
            else: # if non-th
                out = 'ROW'
        # if Nationality == 'NA'
        else:
            out = sna
    # if have sna
    else:
        out = sna
    
    return out

def assign_byNationalitiesOrd(*args,condition):

    sna = args[0][args[1][0]]
    nat = args[0][args[1][1]]
    isic = args[0][args[1][2]]

    # assign if it non-assigned-sna
    if pd.isna(sna):
        # Non-NA Nationalities
        if not pd.isna(nat):
            th_search = bool(re.search('TH|Thai|ไทย',nat))
            if th_search:
                out =  'HH'
            else: # if non-th
                out =  'ROW'
        # if Nationality == 'NA'
        else:
            out =  sna
    # if have sna
    else:
        out =  sna
    
    return out


############################### Tidy SNA 
def tidy_sna(sna,sna10,action):
    if pd.isna(sna):
        #if na and SNA10 is have
        if not pd.isna(sna10): #sna10_sna
            for idx,row in action.iterrows(): #sna10_sna
                if bool(re.search(row.reference,str(sna10))):
                    return row['value'] # SNA
            return sna
    else:
        # if Class is not Correct #ถ้าเจอ ONFC ใน SNA ต้องเอา SNA10 ไป look แล้วหา SNA ลงมา
        if bool(re.search('^.?\D',str(sna))):
            for idx,row in action.iterrows(): #sna10_sna
                if bool(re.search(row.reference,str(sna10))):
                    return row['value'] # SNA
            return sna
        else:
            return sna
        
def tidy_sna10(sna,sna10,action):
    if pd.isna(sna10):
        #if na and SNA is have
        if not pd.isna(sna): #sna10_sna
            for idx,row in action.iterrows(): #sna_sna10
                if bool(re.search(row.reference,str(sna))):
                    return row['value'] # SNA10
            return sna10
    else:
        # if Class is not Correct #ถ้าเจอ 443080 ใน SNA10 ต้องเอา SNA ไป look แล้วหา SNA10 ลงมา
        if bool(re.search('^.?\d',str(sna10))):
            for idx,row in action.iterrows(): #sna_sna10
                if bool(re.search(row.reference,str(sna))):
                    return row['value'] # SNA10
            return sna10
        else:
            return sna10