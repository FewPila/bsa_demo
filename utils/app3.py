import pandas as pd
import numpy as np
import os
import re
import time
import streamlit as st


def assign_byIsic(*args,condition = True):

    def get_sna_isic(sna,isic,isic_action):
        # if have isic
        if not pd.isna(isic):
            # if isic match
            for idx,row in isic_action.iterrows():
                if bool(re.search(row.isic4,isic)):
                    return row.target_sna10
            # if don't match
            return sna
        # if don't have isic
        else: 
            return sna

    sna = args[0][args[1][0]]
    nat = args[0][args[1][1]]
    isic = args[0][args[1][2]]
    isic_action = args[2]

    # assign if non-assigned-sna
    if pd.isna(sna):
        # assign only when nat
        if condition == True:
            if not pd.isna(nat):
                # if th
                th_search = bool(re.search('TH|Thai|ไทย',nat))
                if th_search:
                    out =  get_sna_isic(sna,isic,isic_action) # apply function
                # if non-th
                else:
                    out = sna
            # if non-nationalities       
            else:
                out = sna

        # assign whatever condition
        else:
            out = get_sna_isic(sna,isic,isic_action) # apply function

    # if snaed
    else:
        out = sna

    return out

def assign_byKeywords(*args,condition = True):

    def get_sna_keywords(sna,name,keywords_action):
        for idx,row in keywords_action.iterrows():
            # if match
            if bool(re.search(row.word_token,name)):
                return row.target_sna10
        # if don't match
        return sna
   
    sna = args[0][args[1][0]]
    nat = args[0][args[1][1]]
    name = args[0][args[1][2]]
    keywords_action = args[2]
    
    # assign if non-assigned-sna
    if pd.isna(sna):
        # assign only when nat
        if condition == True:
            if not pd.isna(nat):
                # if th
                th_search = bool(re.search('TH|Thai|ไทย',nat))
                if th_search:
                    out = get_sna_keywords(sna,name,keywords_action) # apply function
                # if non-th
                else:
                    out = sna
            # if non-nationalities       
            else:
                out = sna

        # assign whatever condition
        else:
            out = get_sna_keywords(sna,name,keywords_action) # apply function

    # if snaed
    else:
        out = sna
    return out

def assign_byMatchedSNA(*args,condition = True):
    def get_sna_nmmatched(sna,matched_sna,sna_action):
        for idx,row in sna_action.iterrows():
            if bool(re.search(row.sna_code,matched_sna)):
                return row.target_sna10 # return in SNA10 format
        # if don't match
        return sna
    
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
                th_search = bool(re.search('TH|Thai|ไทย',nat))
                if th_search:
                    out = get_sna_nmmatched(sna,matched_sna,sna_action) # apply function
                # if non-th
                else:
                    out = sna
            # if non-nationalities       
            else:
                out = sna
            
        # assign whatever condition
        else:
            out = get_sna_nmmatched(sna,matched_sna,sna_action) # apply function  
        
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
            th_search = bool(re.search('TH|Thai|ไทย',nat))
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