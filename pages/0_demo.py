import streamlit as st
from streamlit_tags import st_tags
import pandas as pd
import os
import re
import io
import numpy as np
from stqdm import stqdm
from streamlit_extras.dataframe_explorer import dataframe_explorer
import copy
import time
from utils.nm_utils import *


if 't_zero' not in st.session_state:
    st.session_state.t_zero = time.time()

@st.cache_data
def read_upload_data(df):
    def none_but_please_show_progress_bar(*args, **kwargs):
        bar = stqdm(*args, **kwargs)
        def checker(x):
            bar.update(1)
            return False
        return checker
    section = st.empty()
    section.info('reading uploaded data')
    out = pd.read_csv(df,skiprows = none_but_please_show_progress_bar())
    section.empty()
    return out

#@st.cache_resource
def conditional_st_write_df(df):
    file_size = df.memory_usage().sum()
    file_size_simp = file_size / 1000000
    if file_size_simp > 200:
        divider = file_size_simp/200
        sample_size = int(np.round(len(df)/divider))
        portion_of = np.round(sample_size/len(df) * 100)
        st.write(f'File Size is too large so we sample {portion_of}% of total')
        st.dataframe(df.sample(sample_size),use_container_width= True)
    else:
        st.dataframe(df,use_container_width= True)
        
@st.cache_data(ttl=3600)
def init_data_upload_query(uploaded_file,option):
    user_df = uploaded_file.copy(deep = True)
    user_colname = copy.deepcopy(option)
    user_df = user_df.dropna(subset = user_colname)
    user_df = user_df.reset_index(drop = True).reset_index()
    user_df.rename(columns = {'index':'query_index'},inplace = True)
    return user_df,user_colname


def click_query_step1(namecolname):
    st.session_state.query_namecolname = namecolname
    st.session_state.query_step1 = True

@st.cache_data
def load_in(input_):
    output = input_
    return output

# def submit_input_query():
#     st.session_state.query_namecolname = st.session_state.namecol_select_box
#     st.session_state.query_input = True

def click_to_NM():
    st.session_state.app2_input = True

if 'order' not in st.session_state:
    st.session_state.order = {'corpus1':False,'corpus2':False,'corpus3':False}

if 'app1_ExportOutput' not in st.session_state:
    st.session_state.app1_ExportOutput = None

if 'app2_input' not in st.session_state:
    st.session_state.app2_input = False

if 'app2_input' not in st.session_state:
    st.session_state.app2_input = False
    
if 'app2_textprocess' not in st.session_state:
    st.session_state.app2_textprocess = False
    st.session_state.app2_textprocess_regex_list = False
    st.session_state.app2_default_regex_list = copy.deepcopy(default_regex_list)
    st.session_state.app2_developer_regex_list = copy.deepcopy(soft_simp_words)
    st.session_state.app2_developer_regex_listV2 = copy.deepcopy(hard_simp_words)
    st.session_state.app2_regex_listV1 = None
    st.session_state.app2_regex_listV2 = None

if 'app2_preprocessNM' not in st.session_state:
    st.session_state.app2_preprocessNM = False

if 'possible_threshold_list' not in st.session_state:
    st.session_state.possible_threshold_list = ["tfidf_score >= 60 & fuzzy_ratio >= 90 & fuzzy_partialratio >= 90",
                           "tfidf_score >= 66.7 & fuzzy_partialratio >= 97","tfidf_score >= 70"]
    st.session_state.app2_possible_threshold_list = ["tfidf_score >= 60 & fuzzy_ratio >= 90 & fuzzy_partialratio >= 90",
                           "tfidf_score >= 66.7 & fuzzy_partialratio >= 97","tfidf_score >= 70"]

def submit_input_query():
    st.session_state.query_namecolname = st.session_state.namecol_select_box
    st.session_state.query_df = load_in(st.session_state.query_df.filter(st.session_state.query_keep_col))#.sample(50000)
    st.session_state.query_df = st.session_state.query_df.drop_duplicates(st.session_state['query_namecolname']).reset_index(drop = True).reset_index().rename(columns = {'index':'query_index'})
    st.session_state.query_input = True
    

if 'query_input' not in st.session_state:
    st.session_state.query_input = False
    st.session_state.query_cache  = False
    st.session_state.query_df = None
    st.session_state.query_namecolname = None
#################################################################################################### 1 Query Input ####################################################################################################
if  st.session_state.query_input == False:
    st.header("Step 1: Input Query")
    ### check query input
    if st.session_state.app1_ExportOutput is not None:
        check_box = st.checkbox('use app1 input')
    else:
        check_box = False
    if st.session_state.query_cache == False:
        if check_box == False:
            query_upload = st.file_uploader("Choose a file to query",key = 'query_upload')
            if query_upload is not None:
                st.session_state.query_df = read_upload_data(query_upload)
                st.session_state.query_cache = True
        elif check_box:
            if st.session_state.app1_ExportOutput is not None and check_box:
                st.session_state.query_df = load_in(st.session_state.app1_ExportOutput)
                st.session_state.query_cache = True
    # after have input
    if st.session_state.query_df is not None:
        st.subheader('This is Your Query Dataset')
        conditional_st_write_df(st.session_state.query_df)

        st.write(f'{st.session_state.query_df.shape[0]} rows , {st.session_state.query_df.shape[1]} columns')
        # select Name Column
        query_namecol_box = [None]
        query_namecol_box.extend(st.session_state.query_df.columns)
        query_namecol_option = st.selectbox('Which is Names Column ?',query_namecol_box,key = 'namecol_select_box')
        # select Column to keep
        query_keep_col_list = st.session_state.query_df.columns.values.tolist()
        st.multiselect(label = 'Please select column to Keep',options = query_keep_col_list,default = query_keep_col_list,key = 'query_keep_col')
        # submit query_input
        submit_input_query = st.button('Submit_query',on_click = submit_input_query)

if st.session_state.app2_input == False:
    if st.session_state.query_input == True:
        st.header('Step 1: Input Query')
        st.subheader('This is Your Query Dataset')
        conditional_st_write_df(st.session_state.query_df)
        st.write(f'{st.session_state.query_df.shape[0]} rows , {st.session_state.query_df.shape[1]} columns')
#################################################################################################### 1 Query Input ####################################################################################################

if 'corpus1_input' not in st.session_state:
    st.session_state.corpus1_input = False
    st.session_state.corpus1_cache  = False
    # input corpus
    st.session_state.corpus1_df = None
    st.session_state.corpus1_namecolname = None
    st.session_state.corpus1_selected_col_list = None
    st.session_state.corpus1_file_name = None
    # partial nm ?
    st.session_state.corpus1_partial_nm = False
    # adjust query
    st.session_state.adjust_query1 = False
    st.session_state.query1_filter_option = None
    st.session_state.query1_filter_option_dtype = None
    st.session_state.query1_filter_range = None
    st.session_state.query1_filter_choices = None
    st.session_state.query1_filter_option_out = None
    st.session_state.query1_filter_range_out = None
    st.session_state.query1_filter_choices_out = None
    st.session_state.query1_filter_condition = None
    # adjust corpus
    st.session_state.adjust_corpus1 = False
    st.session_state.corpus1_filter_option = None
    st.session_state.corpus1_filter_option_dtype = None
    st.session_state.corpus1_filter_range = None
    st.session_state.corpus1_filter_choices = None
    st.session_state.corpus1_filter_option_out = None
    st.session_state.corpus1_filter_range_out = None
    st.session_state.corpus1_filter_choices_out = None
    st.session_state.corpus1_filter_condition = None
    # add corpus
    st.session_state.add_corpus2 = False

def corpus1_SelectCol_click():
    st.session_state.corpus1_namecolname = load_in(st.session_state.corpus1_namecol_select_box)

def corpus1_SelectCol_list_click():
    st.session_state.corpus1_selected_col_list = load_in(st.session_state.corpus1_col_list_select_box)
    st.session_state.corpus1_df = load_in(st.session_state.corpus1_df.filter(st.session_state.corpus1_selected_col_list))

def corpus1_submit():
    st.session_state.corpus1_partial_nm  = load_in(corpus1_partialnm_box)
    
    # adjust query
    st.session_state.query1_filter_option_out = load_in(st.session_state.query1_filter_option)
    if st.session_state.query1_filter_choices is not None:
        st.session_state.query1_filter_choices_out = load_in(st.session_state.query1_filter_choices)
    elif st.session_state.query1_filter_range is not None:
        st.session_state.query1_filter_range_out = load_in(st.session_state.query1_filter_range)
    # adjust corpus
    st.session_state.corpus1_filter_option_out = load_in(st.session_state.corpus1_filter_option)
    if st.session_state.corpus1_filter_choices is not None:
        st.session_state.corpus1_filter_choices_out = load_in(st.session_state.corpus1_filter_choices)
    elif st.session_state.corpus1_filter_range is not None:
        st.session_state.corpus1_filter_range_out = load_in(st.session_state.corpus1_filter_range)
    
    if st.session_state.query1_filter_option_out is not None:
        st.session_state.adjust_query1 = load_in(True)
        if bool(re.search('num|float|int',query1_type_string)):
            st.session_state.query1_filter_option_dtype = load_in('numeric')
        else:
            st.session_state.query1_filter_option_dtype = load_in('object')

    if st.session_state.corpus1_filter_option_out is not None:
        st.session_state.adjust_corpus1 = load_in(True)
        if bool(re.search('num|float|int',corpus1_type_string)):
            st.session_state.corpus1_filter_option_dtype = load_in('numeric')
        else:
            st.session_state.corpus1_filter_option_dtype = load_in('object')
    
    if st.session_state.query1_filter_choices_out is not None:
        st.session_state.query1_filter_condition = load_in(st.session_state.query1_filter_choices_out)
    elif st.session_state.query1_filter_range_out is not None:
        st.session_state.query1_filter_condition = load_in(st.session_state.query1_filter_range_out)
    
    if st.session_state.corpus1_filter_choices_out is not None:
        st.session_state.corpus1_filter_condition = load_in(st.session_state.corpus1_filter_choices_out)
    elif st.session_state.corpus1_filter_range_out is not None:
        st.session_state.corpus1_filter_condition = load_in(st.session_state.corpus1_filter_range_out)
    
    st.session_state.corpus1_file_name = load_in(re.sub('\\.csv','',corpus1_upload.name))
    st.session_state.corpus1_df = st.session_state.corpus1_df.reset_index(drop = True).reset_index()
    st.session_state.corpus1_df = load_in(st.session_state.corpus1_df.rename(columns = {'index':'corpus_index'}))
    st.session_state.corpus1_input = True
    print(st.session_state.corpus1_input)

def click_add_corpus2():
    st.session_state.add_corpus2 = True

#################################################################################################### 2.1 Corpus Input ####################################################################################################
if st.session_state.query_input == True and st.session_state.corpus1_input == False and st.session_state.app2_input == False:
    st.divider()
    st.header('Step 2: Input Corpus')
    corpus1_upload = st.file_uploader("Choose a file to query",key = 'corpus1_upload')
    if corpus1_upload is not None:
        if st.session_state.corpus1_cache == False:
            st.session_state.corpus1_df = read_upload_data(corpus1_upload)
            st.session_state.corpus1_cache = True
    
    if st.session_state.corpus1_df is not None:
        st.subheader('This is Your Corpus Dataset')
        conditional_st_write_df(st.session_state.corpus1_df)
        st.write(f'{st.session_state.corpus1_df.shape[0]} rows , {st.session_state.corpus1_df.shape[1]} columns')
        
        if st.session_state.corpus1_namecolname is None:
            #select Name Column
            corpus1_namecol_box = [None]
            corpus1_namecol_box.extend(st.session_state.corpus1_df.columns)
            corpus1_namecol_option = st.selectbox('Which is Names Column ?',corpus1_namecol_box,key = 'corpus1_namecol_select_box')
            corpus1_selected_namecol = st.button('next',on_click = corpus1_SelectCol_click)
        
        if st.session_state.corpus1_namecolname is not None and st.session_state.corpus1_selected_col_list is None:
            #select Name Column
            corpus1_columnsFromDf = st.session_state['corpus1_df'].columns.values
            st.multiselect(label = 'Please Select Column to Keep',options = corpus1_columnsFromDf,default = corpus1_columnsFromDf,key = 'corpus1_col_list_select_box')
            #st_tags(value = corpus1_columnsFromDf ,suggestions = corpus1_columnsFromDf ,label = '', text = '',key = 'corpus1_col_list_select_box')
            corpus1_selected_col_list_button = st.button('next',on_click = corpus1_SelectCol_list_click,key = 's_col_button')

        if st.session_state.corpus1_namecolname is not None and st.session_state.corpus1_selected_col_list is not None:
            corpus1_partialnm_box = st.checkbox('Want to Apply Partial Name Matching')
            if corpus1_partialnm_box:
                st.write("↳")
                adjust_query_checkbox = st.checkbox('Adjust on Query Dataset')
                if adjust_query_checkbox:
                    st.write('Adjust Query')
                    query1_filter_box_list = [None]
                    query1_filter_box_list.extend(st.session_state.query_df.columns)
                    query1_filter_option = st.selectbox('Which Column you want to filter?',query1_filter_box_list,key = 'query1_filter_option')
                    if query1_filter_option is not None:
                        # check type of column
                        query1_type_string = str(st.session_state.query_df[query1_filter_option].dtype)
                        # if Integer
                        if bool(re.search('int',query1_type_string)):
                            st.session_state.query1_filter_choices = None
                            st.slider(label = f'filter on {query1_filter_option}',value = [0,max(st.session_state.query_df[query1_filter_option])],key = 'query1_filter_range')
                            if st.session_state.query1_filter_range is not None:
                                filtered_df_query = st.session_state.query_df[(st.session_state.query_df[query1_filter_option] >= st.session_state.query1_filter_range[0]) & (st.session_state.query_df[query1_filter_option] <= st.session_state.query1_filter_range[1])]
                                st.write(f'Now -> {filtered_df_query.shape[0]} rows , {filtered_df_query.shape[1]} columns')
                        # if Float
                        elif bool(re.search('num|float',query1_type_string)):
                            st.session_state.query1_filter_choices = None
                            st.slider(label = f'filter on {query1_filter_option}',value = [0.0,max(st.session_state.query_df[query1_filter_option])],key = 'query1_filter_range')
                            if st.session_state.query1_filter_range is not None:
                                filtered_df_query = st.session_state.query_df[(st.session_state.query_df[query1_filter_option] >= st.session_state.query1_filter_range[0]) & (st.session_state.query_df[query1_filter_option] <= st.session_state.query1_filter_range[1])]
                                st.write(f'Now -> {filtered_df_query.shape[0]} rows , {filtered_df_query.shape[1]} columns')
                        # if Object
                        elif bool(re.search('str|object',query1_type_string)):
                            st.session_state.query1_filter_range = None
                            st.multiselect(label = f'filter on {query1_filter_option}',options = st.session_state.query_df[query1_filter_option].unique().tolist(),default= None,key  = 'query1_filter_choices')
                            if st.session_state.query1_filter_choices is not None:
                                filtered_df_query = st.session_state.query_df[st.session_state.query_df[query1_filter_option].isin(st.session_state.query1_filter_choices)]
                                st.write(f'Now -> {filtered_df_query.shape[0]} rows , {filtered_df_query.shape[1]} columns')

                adjust_corpus_checkbox = st.checkbox('Adjust on Corpus Dataset')
                if adjust_corpus_checkbox:
                    st.write('Adjust Corpus')
                    corpus1_filter_box_list = [None]
                    corpus1_filter_box_list.extend(st.session_state.corpus1_df.columns)
                    corpus1_filter_option = st.selectbox('Which Column you want to filter?',corpus1_filter_box_list,key = 'corpus1_filter_option')
                    if corpus1_filter_option is not None:
                        # check type of column
                        corpus1_type_string = str(st.session_state.corpus1_df[corpus1_filter_option].dtype)
                        # if Integer
                        if bool(re.search('int',corpus1_type_string)):
                            st.session_state.corpus1_filter_choices = None
                            st.slider(label = f'filter on {corpus1_filter_option}',value = [0,max(st.session_state.corpus1_df[corpus1_filter_option])],key = 'corpus1_filter_range')
                            if st.session_state.corpus1_filter_range is not None:
                                filtered_df_corpus1 = st.session_state.corpus1_df[(st.session_state.corpus1_df[corpus1_filter_option] >= st.session_state.corpus1_filter_range[0]) & (st.session_state.corpus1_df[corpus1_filter_option] <= st.session_state.corpus1_filter_range[1])]
                                st.write(f'Now -> {filtered_df_corpus1.shape[0]} rows , {filtered_df_corpus1.shape[1]} columns')
                        # if Float
                        elif bool(re.search('num|float',corpus1_type_string)):
                            st.session_state.corpus1_filter_choices = None
                            st.slider(label = f'filter on {corpus1_filter_option}',value = [0.0,max(st.session_state.corpus1_df[corpus1_filter_option])],key = 'corpus1_filter_range')
                            if st.session_state.corpus1_filter_range is not None:
                                filtered_df_corpus1 = st.session_state.corpus1_df[(st.session_state.corpus1_df[corpus1_filter_option] >= st.session_state.corpus1_filter_range[0]) & (st.session_state.corpus1_df[corpus1_filter_option] <= st.session_state.corpus1_filter_range[1])]
                                st.write(f'Now -> {filtered_df_corpus1.shape[0]} rows , {filtered_df_corpus1.shape[1]} columns')
                        # if Object
                        elif bool(re.search('str|object',corpus1_type_string)):
                            st.session_state.corpus1_filter_range = None
                            st.multiselect(label = f'filter on {corpus1_filter_option}',options = st.session_state.corpus1_df[corpus1_filter_option].unique().tolist(),default= None,key  = 'corpus1_filter_choices')

            submit_button1 = st.button('submit',key = 'submit_c1',on_click = corpus1_submit)

if st.session_state.corpus1_input == True and st.session_state.app2_input == False:
    st.divider()
    st.header('Step 2: Input Corpus')
    st.session_state['order']['corpus1'] = load_in(True)
    
    #conditional_st_write_df(st.session_state.corpus1_df.filter(st.session_state.corpus1_selected_col_list))
    conditional_st_write_df(st.session_state.corpus1_df)
    st.write(f'{st.session_state.corpus1_df.shape[0]} rows , {st.session_state.corpus1_df.shape[1]} columns')
    norm_container1 = st.container()
    left1, right1 = st.columns((1, 20))
    norm_container1.write(f'Column To Apply Name Matching : {st.session_state.corpus1_namecolname}')
    if st.session_state.corpus1_partial_nm:
        norm_container1.write(f'Apply Partial Name Matching : True')
        left1.write("↳")
        
        if st.session_state.query1_filter_option_out is not None:
            right1.write(f'Query Datset Adjust on Column: {st.session_state.query1_filter_option_out} ')
            left1.write("↳")
            if st.session_state.query1_filter_range_out is not None:
                right1.write('Condition =')
                right1.write(f'{st.session_state.query1_filter_option_out} >= {st.session_state.query1_filter_range_out[0]}')
                right1.write(f'{st.session_state.query1_filter_option_out} <= {st.session_state.query1_filter_range_out[1]}')
            if st.session_state.query1_filter_choices_out is not None:
                right1.write('Condition =')
                right1.write(f'{st.session_state.query1_filter_option_out} in {st.session_state.query1_filter_choices_out}')
        
        if st.session_state.corpus1_filter_option_out is not None:
            right1.write(f'Corpus Datset Adjust on Column: {st.session_state.corpus1_filter_option_out} ')
            left1.write("↳")
            if st.session_state.corpus1_filter_range_out is not None:
                right1.write('Condition =')
                right1.write(f'{st.session_state.corpus1_filter_option_out} >= {st.session_state.corpus1_filter_range_out[0]}')
                right1.write(f'{st.session_state.corpus1_filter_option_out} <= {st.session_state.corpus1_filter_range_out[1]}')
            if st.session_state.corpus1_filter_choices_out is not None:
                right1.write('Condition =')
                right1.write(f'{st.session_state.corpus1_filter_option_out} in {st.session_state.corpus1_filter_choices_out}')
    if st.session_state.add_corpus2 == False:
        col1,col2 = st.columns([1,0.2])
        with col1:
            corpus2_add = st.button('Add More Corpus?',on_click = click_add_corpus2,key = 'corpus2_add')
        with col2:
            next_button1 = st.button('Next',on_click = click_to_NM,key = 'next_button1')
#################################################################################################### 2.1 Corpus Input ####################################################################################################

if 'corpus2_input' not in st.session_state:
    st.session_state.corpus2_input = False
    st.session_state.corpus2_cache  = False
    # input corpus
    st.session_state.corpus2_df = None
    st.session_state.corpus2_namecolname = None
    st.session_state.corpus2_selected_col_list = None
    st.session_state.corpus2_file_name = None
    # partial nm ?
    st.session_state.corpus2_partial_nm = False
    # adjust query
    st.session_state.adjust_query2 = False
    st.session_state.query2_filter_option = None
    st.session_state.query2_filter_option_dtype = None
    st.session_state.query2_filter_range = None
    st.session_state.query2_filter_choices = None
    st.session_state.query2_filter_option_out = None
    st.session_state.query2_filter_range_out = None
    st.session_state.query2_filter_choices_out = None
    st.session_state.query2_filter_condition = None
    # adjust corpus
    st.session_state.adjust_corpus2 = False
    st.session_state.corpus2_filter_option = None
    st.session_state.corpus2_filter_option_dtype = None
    st.session_state.corpus2_filter_range = None
    st.session_state.corpus2_filter_choices = None
    st.session_state.corpus2_filter_option_out = None
    st.session_state.corpus2_filter_range_out = None
    st.session_state.corpus2_filter_choices_out = None
    st.session_state.corpus2_filter_condition = None
    # add corpus
    st.session_state.add_corpus3 = False

def corpus2_SelectCol_click():
    st.session_state.corpus2_namecolname = load_in(st.session_state.corpus2_namecol_select_box)

def corpus2_SelectCol_list_click():
    st.session_state.corpus2_selected_col_list = load_in(st.session_state.corpus2_col_list_select_box)
    st.session_state.corpus2_df = load_in(st.session_state.corpus2_df.filter(st.session_state.corpus2_selected_col_list))#.sample(50000)

def corpus2_submit():
    st.session_state.corpus2_partial_nm  = load_in(corpus2_partialnm_box)
    
    # adjust query
    st.session_state.query2_filter_option_out = load_in(st.session_state.query2_filter_option)
    if st.session_state.query2_filter_choices is not None:
        st.session_state.query2_filter_choices_out = load_in(st.session_state.query2_filter_choices)
    elif st.session_state.query2_filter_range is not None:
        st.session_state.query2_filter_range_out = load_in(st.session_state.query2_filter_range)
    # adjust corpus
    st.session_state.corpus2_filter_option_out = load_in(st.session_state.corpus2_filter_option)
    if st.session_state.corpus2_filter_choices is not None:
        st.session_state.corpus2_filter_choices_out = load_in(st.session_state.corpus2_filter_choices)
    elif st.session_state.corpus2_filter_range is not None:
        st.session_state.corpus2_filter_range_out = load_in(st.session_state.corpus2_filter_range)
    
    if st.session_state.query2_filter_option_out is not None:
        st.session_state.adjust_query2 = load_in(True)
        if bool(re.search('num|float|int',query2_type_string)):
            st.session_state.query2_filter_option_dtype = load_in('numeric')
        else:
            st.session_state.query2_filter_option_dtype = load_in('object')

    if st.session_state.corpus2_filter_option_out is not None:
        st.session_state.adjust_corpus2 = load_in(True)
        if bool(re.search('num|float|int',corpus2_type_string)):
            st.session_state.corpus2_filter_option_dtype = load_in('numeric')
        else:
            st.session_state.corpus2_filter_option_dtype = load_in('object')
    
    if st.session_state.query2_filter_choices_out is not None:
        st.session_state.query2_filter_condition = load_in(st.session_state.query2_filter_choices_out)
    elif st.session_state.query2_filter_range_out is not None:
        st.session_state.query2_filter_condition = load_in(st.session_state.query2_filter_range_out)
    
    if st.session_state.corpus2_filter_choices_out is not None:
        st.session_state.corpus2_filter_condition = load_in(st.session_state.corpus2_filter_choices_out)
    elif st.session_state.corpus2_filter_range_out is not None:
        st.session_state.corpus2_filter_condition = load_in(st.session_state.corpus2_filter_range_out)
    
    st.session_state.corpus2_file_name = load_in(re.sub('\\.csv','',corpus2_upload.name))
    st.session_state.corpus2_df = st.session_state.corpus2_df.reset_index(drop = True).reset_index()
    st.session_state.corpus2_df = load_in(st.session_state.corpus2_df.rename(columns = {'index':'corpus_index'}))
    st.session_state.corpus2_input = True
    print(st.session_state.corpus2_input)

def click_add_corpus3():
    st.session_state.add_corpus3 = True


#################################################################################################### 2.2 Corpus Input ####################################################################################################
if st.session_state.query_input and (st.session_state.corpus2_input == False) and st.session_state.add_corpus2 and st.session_state.app2_input == False:
    st.divider()
    st.header('Step 2.2: Added Input Corpus')
    corpus2_upload = st.file_uploader("Choose a file to query",key = 'corpus2_upload')
    if corpus2_upload is not None:
        if st.session_state.corpus2_cache == False:
            st.session_state.corpus2_df = read_upload_data(corpus2_upload)
            st.session_state.corpus2_cache = True
    
    if st.session_state.corpus2_df is not None:
        st.subheader('This is Your Corpus Dataset')
        conditional_st_write_df(st.session_state.corpus2_df)
        st.write(f'{st.session_state.corpus2_df.shape[0]} rows , {st.session_state.corpus2_df.shape[1]} columns')
        
        if st.session_state.corpus2_namecolname is None:
            #select Name Column
            corpus2_namecol_box = [None]
            corpus2_namecol_box.extend(st.session_state.corpus2_df.columns)
            corpus2_namecol_option = st.selectbox('Which is Names Column ?',corpus2_namecol_box,key = 'corpus2_namecol_select_box')
            corpus2_selected_namecol = st.button('next',on_click = corpus2_SelectCol_click)
        
        if st.session_state.corpus2_namecolname is not None and st.session_state.corpus2_selected_col_list is None:
            #select Name Column
            corpus2_columnsFromDf = st.session_state['corpus2_df'].columns.values
            st.multiselect(label = 'Please Select Column to Keep',options = corpus2_columnsFromDf,default = corpus2_columnsFromDf,key = 'corpus2_col_list_select_box')
            #st_tags(value = corpus2_columnsFromDf ,suggestions = corpus2_columnsFromDf ,label = '', text = '',key = 'corpus2_col_list_select_box')
            corpus2_selected_col_list_button = st.button('next',on_click = corpus2_SelectCol_list_click,key = 's_col_button')

        if st.session_state.corpus2_namecolname is not None and st.session_state.corpus2_selected_col_list is not None:
            corpus2_partialnm_box = st.checkbox('Want to Apply Partial Name Matching')
            if corpus2_partialnm_box:
                st.write("↳")
                adjust_query_checkbox = st.checkbox('Adjust on Query Dataset')
                if adjust_query_checkbox:
                    st.write('Adjust Query')
                    query2_filter_box_list = [None]
                    query2_filter_box_list.extend(st.session_state.query_df.columns)
                    query2_filter_option = st.selectbox('Which Column you want to filter?',query2_filter_box_list,key = 'query2_filter_option')
                    if query2_filter_option is not None:
                        # check type of column
                        query2_type_string = str(st.session_state.query_df[query2_filter_option].dtype)
                        # if Integer
                        if bool(re.search('int',query2_type_string)):
                            st.session_state.query2_filter_choices = None
                            st.slider(label = f'filter on {query2_filter_option}',value = [0,max(st.session_state.query_df[query2_filter_option])],key = 'query2_filter_range')
                            if st.session_state.query2_filter_range is not None:
                                filtered_df_query = st.session_state.query_df[(st.session_state.query_df[query2_filter_option] >= st.session_state.query2_filter_range[0]) & (st.session_state.query_df[query2_filter_option] <= st.session_state.query2_filter_range[1])]
                                st.write(f'Now -> {filtered_df_query.shape[0]} rows , {filtered_df_query.shape[1]} columns')
                        # if Float
                        elif bool(re.search('num|float',query2_type_string)):
                            st.session_state.query2_filter_choices = None
                            st.slider(label = f'filter on {query2_filter_option}',value = [0.0,max(st.session_state.query_df[query2_filter_option])],key = 'query2_filter_range')
                            if st.session_state.query2_filter_range is not None:
                                filtered_df_query = st.session_state.query_df[(st.session_state.query_df[query2_filter_option] >= st.session_state.query2_filter_range[0]) & (st.session_state.query_df[query2_filter_option] <= st.session_state.query2_filter_range[1])]
                                st.write(f'Now -> {filtered_df_query.shape[0]} rows , {filtered_df_query.shape[1]} columns')
                        # if Object
                        elif bool(re.search('str|object',query2_type_string)):
                            st.session_state.query2_filter_range = None
                            st.multiselect(label = f'filter on {query2_filter_option}',options = st.session_state.query_df[query2_filter_option].unique().tolist(),default= None,key  = 'query2_filter_choices')
                            if st.session_state.query2_filter_choices is not None:
                                filtered_df_query = st.session_state.query_df[st.session_state.query_df[query2_filter_option].isin(st.session_state.query2_filter_choices)]
                                st.write(f'Now -> {filtered_df_query.shape[0]} rows , {filtered_df_query.shape[1]} columns')

                adjust_corpus_checkbox = st.checkbox('Adjust on Corpus Dataset')
                if adjust_corpus_checkbox:
                    st.write('Adjust Corpus')
                    corpus2_filter_box_list = [None]
                    corpus2_filter_box_list.extend(st.session_state.corpus2_df.columns)
                    corpus2_filter_option = st.selectbox('Which Column you want to filter?',corpus2_filter_box_list,key = 'corpus2_filter_option')
                    if corpus2_filter_option is not None:
                        # check type of column
                        corpus2_type_string = str(st.session_state.corpus2_df[corpus2_filter_option].dtype)
                        # if Integer
                        if bool(re.search('int',corpus2_type_string)):
                            st.session_state.corpus2_filter_choices = None
                            st.slider(label = f'filter on {corpus2_filter_option}',value = [0,max(st.session_state.corpus2_df[corpus2_filter_option])],key = 'corpus2_filter_range')
                            if st.session_state.corpus2_filter_range is not None:
                                filtered_df_corpus2 = st.session_state.corpus2_df[(st.session_state.corpus2_df[corpus2_filter_option] >= st.session_state.corpus2_filter_range[0]) & (st.session_state.corpus2_df[corpus2_filter_option] <= st.session_state.corpus2_filter_range[1])]
                                st.write(f'Now -> {filtered_df_corpus2.shape[0]} rows , {filtered_df_corpus2.shape[1]} columns')
                        # if Float
                        elif bool(re.search('num|float',corpus2_type_string)):
                            st.session_state.corpus2_filter_choices = None
                            st.slider(label = f'filter on {corpus2_filter_option}',value = [0.0,max(st.session_state.corpus2_df[corpus2_filter_option])],key = 'corpus2_filter_range')
                            if st.session_state.corpus2_filter_range is not None:
                                filtered_df_corpus2 = st.session_state.corpus2_df[(st.session_state.corpus2_df[corpus2_filter_option] >= st.session_state.corpus2_filter_range[0]) & (st.session_state.corpus2_df[corpus2_filter_option] <= st.session_state.corpus2_filter_range[1])]
                                st.write(f'Now -> {filtered_df_corpus2.shape[0]} rows , {filtered_df_corpus2.shape[1]} columns')
                        # if Object
                        elif bool(re.search('str|object',corpus2_type_string)):
                            st.session_state.corpus2_filter_range = None
                            st.multiselect(label = f'filter on {corpus2_filter_option}',options = st.session_state.corpus2_df[corpus2_filter_option].unique().tolist(),default= None,key  = 'corpus2_filter_choices')

            submit_button2 = st.button('submit',key = 'submit_c2',on_click = corpus2_submit)

if st.session_state.corpus2_input == True and st.session_state.app2_input == False:
    st.divider()
    st.header('Step 2.2: Added Input Corpus')
    st.session_state['order']['corpus2'] = load_in(True)
    
    conditional_st_write_df(st.session_state.corpus2_df)
    st.write(f'{st.session_state.corpus2_df.shape[0]} rows , {st.session_state.corpus2_df.shape[1]} columns')
    norm_container2 = st.container()
    left2, right2 = st.columns((1, 20))
    norm_container2.write(f'Column To Apply Name Matching : {st.session_state.corpus2_namecolname}')
    if st.session_state.corpus2_partial_nm:
        norm_container2.write(f'Apply Partial Name Matching : True')
        left2.write("↳")
        
        if st.session_state.query2_filter_option_out is not None:
            right2.write(f'Query Datset Adjust on Column: {st.session_state.query2_filter_option_out} ')
            left2.write("↳")
            if st.session_state.query2_filter_range_out is not None:
                right2.write('Condition =')
                right2.write(f'{st.session_state.query2_filter_option_out} >= {st.session_state.query2_filter_range_out[0]}')
                right2.write(f'{st.session_state.query2_filter_option_out} <= {st.session_state.query2_filter_range_out[1]}')
            if st.session_state.query2_filter_choices_out is not None:
                right2.write('Condition =')
                right2.write(f'{st.session_state.query2_filter_option_out} in {st.session_state.query2_filter_choices_out}')
        
        if st.session_state.corpus2_filter_option_out is not None:
            right2.write(f'Corpus Datset Adjust on Column: {st.session_state.corpus2_filter_option_out} ')
            left2.write("↳")
            if st.session_state.corpus2_filter_range_out is not None:
                right2.write('Condition =')
                right2.write(f'{st.session_state.corpus2_filter_option_out} >= {st.session_state.corpus2_filter_range_out[0]}')
                right2.write(f'{st.session_state.corpus2_filter_option_out} <= {st.session_state.corpus2_filter_range_out[1]}')
            if st.session_state.corpus2_filter_choices_out is not None:
                right2.write('Condition =')
                right2.write(f'{st.session_state.corpus2_filter_option_out} in {st.session_state.corpus2_filter_choices_out}')
    if st.session_state.add_corpus3 == False:
        col1,col2 = st.columns([1,0.2])
        with col1:
            corpus2_add = st.button('Add More Corpus?',on_click = click_add_corpus3,key = 'corpus2_add')
        with col2:
            next_button2 = st.button('Next',on_click = click_to_NM,key = 'next_button2')
#################################################################################################### 2.2 Corpus Input ####################################################################################################

if 'corpus3_input' not in st.session_state:
    st.session_state.corpus3_input = False
    st.session_state.corpus3_cache  = False
    # input corpus
    st.session_state.corpus3_df = None
    st.session_state.corpus3_namecolname = None
    st.session_state.corpus3_selected_col_list = None
    st.session_state.corpus3_file_name = None
    # partial nm ?
    st.session_state.corpus3_partial_nm = False
    # adjust query
    st.session_state.adjust_query3 = False
    st.session_state.query3_filter_option = None
    st.session_state.query3_filter_option_dtype = None
    st.session_state.query3_filter_range = None
    st.session_state.query3_filter_choices = None
    st.session_state.query3_filter_option_out = None
    st.session_state.query3_filter_range_out = None
    st.session_state.query3_filter_choices_out = None
    st.session_state.query3_filter_condition = None
    # adjust corpus
    st.session_state.adjust_corpus3 = False
    st.session_state.corpus3_filter_option = None
    st.session_state.corpus3_filter_option_dtype = None
    st.session_state.corpus3_filter_range = None
    st.session_state.corpus3_filter_choices = None
    st.session_state.corpus3_filter_option_out = None
    st.session_state.corpus3_filter_range_out = None
    st.session_state.corpus3_filter_choices_out = None
    st.session_state.corpus3_filter_condition = None


def corpus3_SelectCol_click():
    st.session_state.corpus3_namecolname = load_in(st.session_state.corpus3_namecol_select_box)

def corpus3_SelectCol_list_click():
    st.session_state.corpus3_selected_col_list = load_in(st.session_state.corpus3_col_list_select_box)
    st.session_state.corpus3_df = load_in(st.session_state.corpus3_df.filter(st.session_state.corpus3_selected_col_list))


def corpus3_submit():
    st.session_state.corpus3_partial_nm  = load_in(corpus3_partialnm_box)
    
    # adjust query
    st.session_state.query3_filter_option_out = load_in(st.session_state.query3_filter_option)
    if st.session_state.query3_filter_choices is not None:
        st.session_state.query3_filter_choices_out = load_in(st.session_state.query3_filter_choices)
    elif st.session_state.query3_filter_range is not None:
        st.session_state.query3_filter_range_out = load_in(st.session_state.query3_filter_range)
    # adjust corpus
    st.session_state.corpus3_filter_option_out = load_in(st.session_state.corpus3_filter_option)
    if st.session_state.corpus3_filter_choices is not None:
        st.session_state.corpus3_filter_choices_out = load_in(st.session_state.corpus3_filter_choices)
    elif st.session_state.corpus3_filter_range is not None:
        st.session_state.corpus3_filter_range_out = load_in(st.session_state.corpus3_filter_range)
    
    if st.session_state.query3_filter_option_out is not None:
        st.session_state.adjust_query3 = load_in(True)
        if bool(re.search('num|float|int',query3_type_string)):
            st.session_state.query3_filter_option_dtype = load_in('numeric')
        else:
            st.session_state.query3_filter_option_dtype = load_in('object')

    if st.session_state.corpus3_filter_option_out is not None:
        st.session_state.adjust_corpus3 = load_in(True)
        if bool(re.search('num|float|int',corpus3_type_string)):
            st.session_state.corpus3_filter_option_dtype = load_in('numeric')
        else:
            st.session_state.corpus3_filter_option_dtype = load_in('object')
    
    if st.session_state.query3_filter_choices_out is not None:
        st.session_state.query3_filter_condition = load_in(st.session_state.query3_filter_choices_out)
    elif st.session_state.query3_filter_range_out is not None:
        st.session_state.query3_filter_condition = load_in(st.session_state.query3_filter_range_out)
    
    if st.session_state.corpus3_filter_choices_out is not None:
        st.session_state.corpus3_filter_condition = load_in(st.session_state.corpus3_filter_choices_out)
    elif st.session_state.corpus3_filter_range_out is not None:
        st.session_state.corpus3_filter_condition = load_in(st.session_state.corpus3_filter_range_out)
    
    st.session_state.corpus3_file_name = load_in(re.sub('\\.csv','',corpus3_upload.name))
    st.session_state.corpus3_df = st.session_state.corpus3_df.reset_index(drop = True).reset_index()
    st.session_state.corpus3_df = load_in(st.session_state.corpus3_df.rename(columns = {'index':'corpus_index'}))
    st.session_state.corpus3_input = True
    print(st.session_state.corpus3_input)

def click_add_corpus3():
    st.session_state.add_corpus3 = True


#################################################################################################### 2.3 Corpus Input ####################################################################################################
if st.session_state.query_input and (st.session_state.corpus3_input == False) and st.session_state.add_corpus3 and st.session_state.app2_input == False:
    st.divider()
    st.header('Step 2.3: Added Input Corpus')
    corpus3_upload = st.file_uploader("Choose a file to query",key = 'corpus3_upload')
    if corpus3_upload is not None:
        if st.session_state.corpus3_cache == False:
            st.session_state.corpus3_df = read_upload_data(corpus3_upload)
            st.session_state.corpus3_cache = True
    
    if st.session_state.corpus3_df is not None:
        st.subheader('This is Your Corpus Dataset')
        conditional_st_write_df(st.session_state.corpus3_df)
        st.write(f'{st.session_state.corpus3_df.shape[0]} rows , {st.session_state.corpus3_df.shape[1]} columns')
        
        if st.session_state.corpus3_namecolname is None:
            #select Name Column
            corpus3_namecol_box = [None]
            corpus3_namecol_box.extend(st.session_state.corpus3_df.columns)
            corpus3_namecol_option = st.selectbox('Which is Names Column ?',corpus3_namecol_box,key = 'corpus3_namecol_select_box')
            corpus3_selected_namecol = st.button('next',on_click = corpus3_SelectCol_click)
        
        if st.session_state.corpus3_namecolname is not None and st.session_state.corpus3_selected_col_list is None:
            #select Name Column
            corpus3_columnsFromDf = st.session_state['corpus3_df'].columns.values
            st.multiselect(label = 'Please Select Column to Keep',options = corpus3_columnsFromDf,default = corpus3_columnsFromDf,key = 'corpus3_col_list_select_box')
            #st_tags(value = corpus3_columnsFromDf ,suggestions = corpus3_columnsFromDf ,label = '', text = '',key = 'corpus3_col_list_select_box')
            corpus3_selected_col_list_button = st.button('next',on_click = corpus3_SelectCol_list_click,key = 's_col_button')

        if st.session_state.corpus3_namecolname is not None and st.session_state.corpus3_selected_col_list is not None:
            corpus3_partialnm_box = st.checkbox('Want to Apply Partial Name Matching')
            if corpus3_partialnm_box:
                st.write("↳")
                adjust_query_checkbox = st.checkbox('Adjust on Query Dataset')
                if adjust_query_checkbox:
                    st.write('Adjust Query')
                    query3_filter_box_list = [None]
                    query3_filter_box_list.extend(st.session_state.query_df.columns)
                    query3_filter_option = st.selectbox('Which Column you want to filter?',query3_filter_box_list,key = 'query3_filter_option')
                    if query3_filter_option is not None:
                        # check type of column
                        query3_type_string = str(st.session_state.query_df[query3_filter_option].dtype)
                        # if Integer
                        if bool(re.search('int',query3_type_string)):
                            st.session_state.query3_filter_choices = None
                            st.slider(label = f'filter on {query3_filter_option}',value = [0,max(st.session_state.query_df[query3_filter_option])],key = 'query3_filter_range')
                            if st.session_state.query3_filter_range is not None:
                                filtered_df_query = st.session_state.query_df[(st.session_state.query_df[query3_filter_option] >= st.session_state.query3_filter_range[0]) & (st.session_state.query_df[query3_filter_option] <= st.session_state.query3_filter_range[1])]
                                st.write(f'Now -> {filtered_df_query.shape[0]} rows , {filtered_df_query.shape[1]} columns')
                        # if Float
                        elif bool(re.search('num|float',query3_type_string)):
                            st.session_state.query3_filter_choices = None
                            st.slider(label = f'filter on {query3_filter_option}',value = [0.0,max(st.session_state.query_df[query3_filter_option])],key = 'query3_filter_range')
                            if st.session_state.query3_filter_range is not None:
                                filtered_df_query = st.session_state.query_df[(st.session_state.query_df[query3_filter_option] >= st.session_state.query3_filter_range[0]) & (st.session_state.query_df[query3_filter_option] <= st.session_state.query3_filter_range[1])]
                                st.write(f'Now -> {filtered_df_query.shape[0]} rows , {filtered_df_query.shape[1]} columns')
                        # if Object
                        elif bool(re.search('str|object',query3_type_string)):
                            st.session_state.query3_filter_range = None
                            st.multiselect(label = f'filter on {query3_filter_option}',options = st.session_state.query_df[query3_filter_option].unique().tolist(),default= None,key  = 'query3_filter_choices')
                            if st.session_state.query3_filter_choices is not None:
                                filtered_df_query = st.session_state.query_df[st.session_state.query_df[query3_filter_option].isin(st.session_state.query3_filter_choices)]
                                st.write(f'Now -> {filtered_df_query.shape[0]} rows , {filtered_df_query.shape[1]} columns')

                adjust_corpus_checkbox = st.checkbox('Adjust on Corpus Dataset')
                if adjust_corpus_checkbox:
                    st.write('Adjust Corpus')
                    corpus3_filter_box_list = [None]
                    corpus3_filter_box_list.extend(st.session_state.corpus3_df.columns)
                    corpus3_filter_option = st.selectbox('Which Column you want to filter?',corpus3_filter_box_list,key = 'corpus3_filter_option')
                    if corpus3_filter_option is not None:
                        # check type of column
                        corpus3_type_string = str(st.session_state.corpus3_df[corpus3_filter_option].dtype)
                        # if Integer
                        if bool(re.search('int',corpus3_type_string)):
                            st.session_state.corpus3_filter_choices = None
                            st.slider(label = f'filter on {corpus3_filter_option}',value = [0,max(st.session_state.corpus3_df[corpus3_filter_option])],key = 'corpus3_filter_range')
                            if st.session_state.corpus3_filter_range is not None:
                                filtered_df_corpus3 = st.session_state.corpus3_df[(st.session_state.corpus3_df[corpus3_filter_option] >= st.session_state.corpus3_filter_range[0]) & (st.session_state.corpus3_df[corpus3_filter_option] <= st.session_state.corpus3_filter_range[1])]
                                st.write(f'Now -> {filtered_df_corpus3.shape[0]} rows , {filtered_df_corpus3.shape[1]} columns')
                        # if Float
                        elif bool(re.search('num|float',corpus3_type_string)):
                            st.session_state.corpus3_filter_choices = None
                            st.slider(label = f'filter on {corpus3_filter_option}',value = [0.0,max(st.session_state.corpus3_df[corpus3_filter_option])],key = 'corpus3_filter_range')
                            if st.session_state.corpus3_filter_range is not None:
                                filtered_df_corpus3 = st.session_state.corpus3_df[(st.session_state.corpus3_df[corpus3_filter_option] >= st.session_state.corpus3_filter_range[0]) & (st.session_state.corpus3_df[corpus3_filter_option] <= st.session_state.corpus3_filter_range[1])]
                                st.write(f'Now -> {filtered_df_corpus3.shape[0]} rows , {filtered_df_corpus3.shape[1]} columns')
                        # if Object
                        elif bool(re.search('str|object',corpus3_type_string)):
                            st.session_state.corpus3_filter_range = None
                            st.multiselect(label = f'filter on {corpus3_filter_option}',options = st.session_state.corpus3_df[corpus3_filter_option].unique().tolist(),default= None,key  = 'corpus3_filter_choices')

            submit_button3 = st.button('submit',key = 'submit_c3',on_click = corpus3_submit)


if st.session_state.corpus3_input == True and st.session_state.app2_input == False:
    st.divider()
    st.header('Step 2.3: Added Input Corpus')
    st.session_state['order']['corpus3'] = load_in(True)
    conditional_st_write_df(st.session_state.corpus3_df)
    st.write(f'{st.session_state.corpus3_df.shape[0]} rows , {st.session_state.corpus3_df.shape[1]} columns')
    norm_container3 = st.container()
    left3, right3 = st.columns((1, 20))
    norm_container3.write(f'Column To Apply Name Matching : {st.session_state.corpus3_namecolname}')
    if st.session_state.corpus3_partial_nm:
        norm_container3.write(f'Apply Partial Name Matching : True')
        left3.write("↳")
        if st.session_state.query3_filter_option_out is not None:
            right3.write(f'Query Datset Adjust on Column: {st.session_state.query3_filter_option_out} ')
            left3.write("↳")
            if st.session_state.query3_filter_range_out is not None:
                right3.write('Condition =')
                right3.write(f'{st.session_state.query3_filter_option_out} >= {st.session_state.query3_filter_range_out[0]}')
                right3.write(f'{st.session_state.query3_filter_option_out} <= {st.session_state.query3_filter_range_out[1]}')
            if st.session_state.query3_filter_choices_out is not None:
                right3.write('Condition =')
                right3.write(f'{st.session_state.query3_filter_option_out} in {st.session_state.query3_filter_choices_out}')

            right3.write(f'Corpus Datset Adjust on Column: {st.session_state.corpus3_filter_option_out} ')
            left3.write("↳")
            if st.session_state.corpus3_filter_range_out is not None:
                right3.write('Condition =')
                right3.write(f'{st.session_state.corpus3_filter_option_out} >= {st.session_state.corpus3_filter_range_out[0]}')
                right3.write(f'{st.session_state.corpus3_filter_option_out} <= {st.session_state.corpus3_filter_range_out[1]}')
            if st.session_state.corpus3_filter_choices_out is not None:
                right3.write('Condition =')
                right3.write(f'{st.session_state.corpus3_filter_option_out} in {st.session_state.corpus3_filter_choices_out}')
    col1,col2 = st.columns([1,0.2])
    with col2:
        next_button3 = st.button('Next',on_click = click_to_NM,key = 'next_button3')

#################################################################################################### 2.3 Corpus Input ####################################################################################################



#################################################################################################### 3. Text-Preprocess ####################################################################################################
# if st.session_state.app2_input == True:
#     st.write('Matafaka')
#     st.write(st.session_state['order'])
#     st.write(st.session_state['corpus1_file_name'])
#     st.write(st.session_state['corpus2_file_name'])
#     st.write(st.session_state['corpus3_file_name'])

def submit_textpreprocess_regex():
    if st.session_state.app2_double_prep:
        st.session_state.app2_regex_listV1 = load_in(regex_tags)
        st.session_state.app2_regex_listV2 = load_in(regex_tagsV2)
        st.session_state.app2_textprocess_regex_list = load_in(['not_empty'])
    else:
        st.session_state.app2_textprocess_regex_list = load_in(regex_tags)
    st.session_state.app2_textprocess  = True

if (st.session_state.app2_input == True) and (st.session_state.app2_textprocess == False) :
    st.header("1. Text Preprocess",divider= 'orange')
    st.caption("Text Preprocess จะทำการลบ keywords (regex) ดังกล่าว ในชื่อทั้งหมดของ Dataset")
    st.caption('_(หากกรอก keyword ที่เป็นภาษาอังกฤษ กรุณาใช้ UPPER CASE)_')

    regex_section = st.empty()
    with regex_section.container():
        container = st.container()
        container2 = st.container()

        app2_double_prep = st.checkbox('Optional Double Text Preprocess (for more specific)')
        if app2_double_prep:
            st.session_state.app2_double_prep = True
        else:
            st.session_state.app2_double_prep = False

        agree = st.checkbox('Developer Choices*')
        if agree:
            st.session_state.app2_choices = 'developer'
        else:
            st.session_state.app2_choices = 'default'            

        with container: # to put it to top of checkbox
            if st.session_state.app2_choices == 'default':
                regex_tags = st_tags(label = 'Text Preprocess',value = st.session_state.app2_default_regex_list,text = 'regex',maxtags = -1)
            elif st.session_state.app2_choices == 'developer':
                regex_tags = st_tags(label = 'Text Preprocess',value = st.session_state.app2_developer_regex_list,text = 'soft_simplify',maxtags= -1)

        if st.session_state.app2_double_prep:
            with container2: # to put it to top of checkbox
                if st.session_state.app2_choices == 'default':
                    regex_tagsV2 = st_tags(label = 'Text Preprocess II.',value = ['บริษัท','จำกัด','มหาชน','INC'],text = 'regex',maxtags = -1)
                elif st.session_state.app2_choices == 'developer':
                    regex_tagsV2 = st_tags(label = 'Text Preprocess II.',value = st.session_state.app2_developer_regex_listV2,text = 'hard_simplify',maxtags= -1)
            
        ### submit to next-step                            
        regex_submit_button = st.button("Submit your Regex choices",key = 'regex_customize_submit_button',on_click=submit_textpreprocess_regex)

#################################################################################################### 3. Text-Preprocess ####################################################################################################

#################################################################################################### 4. Name Matching ####################################################################################################
# if st.session_state.app2_textprocess :
#     st.write('you did great')
#     st.write(st.session_state.app2_textprocess_regex_list)
#     st.write(st.session_state.corpus1_df)
#     st.write(st.session_state.corpus2_df)

@st.cache_data
def adjust_dataset(query_df,corpus_df,
                   adjust_query,query_filter,query_filter_dtype,query_filter_condition,
                   adjust_corpus,corpus_filter,corpus_filter_dtype,corpus_filter_condition):
    final_query_df = query_df.copy()
    final_corpus_df = corpus_df.copy()
    # if adjust query dataset
    if adjust_query:
        if query_filter_dtype == 'object':
            final_query_df = final_query_df[final_query_df[query_filter].isin(query_filter_condition)]
        elif query_filter_dtype == 'numeric':
            final_query_df = final_query_df[final_query_df[query_filter] >= query_filter_condition[0]]
            final_query_df = final_query_df[final_query_df[query_filter] <= query_filter_condition[1]]
    # if adjust corpus dataset
    if adjust_corpus:
        if corpus_filter_dtype == 'object':
            final_corpus_df = final_corpus_df[final_corpus_df[corpus_filter].isin(corpus_filter_condition)]
        elif corpus_filter_dtype == 'numeric':
            final_corpus_df = final_corpus_df[final_corpus_df[corpus_filter] >= corpus_filter_condition[0]]
            final_corpus_df = final_corpus_df[final_corpus_df[corpus_filter] <= corpus_filter_condition[1]]

    # return processed dataset
    return final_query_df,final_corpus_df

@st.cache_data
def name_matching(df_query,query_colname,df_corpus,corpus_colname,regex_list):
    # preprocess-by Regex
    query_names,corpus_names = text_preprocess_byRegex(df_query,query_colname,
                                                df_corpus,corpus_colname,
                                                regex_list = regex_list)
    # prepro data for NM
    syn_df_query,syn_df_corpus = wrap_up_material(df_query,df_corpus,
                                          query_names,corpus_names)
    # NM 
    matched_df = extract_NM(syn_df_query,syn_df_query.query_name,query_colname,
                            syn_df_corpus,syn_df_corpus.corpus_name,corpus_colname)
    #matched_df.rename(columns = {'query_name':f'cleaned_{query_colname}','corpus_name':f'cleaned_{corpus_colname}'},inplace = True)
    
    return matched_df

if st.session_state.app2_textprocess and st.session_state.app2_preprocessNM == False:
    st.header("2. Name Matching",divider = 'orange')
    c = 1
    for world in st.session_state.order.values():
        if world == True:
            # store input
            st.write(f"running corpus: {c}")
            # Filter Dataset
            print(st.session_state[f'corpus{c}_namecolname'])
            st.session_state['final_query_df'],st.session_state['final_corpus_df'] = adjust_dataset(st.session_state['query_df'],
                            st.session_state[f'corpus{c}_df'],
                            st.session_state[f'adjust_query{c}'],st.session_state[f'query{c}_filter_option_out'],
                            st.session_state[f'query{c}_filter_option_dtype'],st.session_state[f'query{c}_filter_condition'],
                            st.session_state[f'adjust_corpus{c}'],st.session_state[f'corpus{c}_filter_option_out'],
                            st.session_state[f'corpus{c}_filter_option_dtype'],st.session_state[f'corpus{c}_filter_condition'])

            new_col_name = []
            for colname in st.session_state[f'corpus{c}_df'].columns.values:
                if colname != 'corpus_index':
                    name = f"{colname}_{st.session_state[f'corpus{c}_file_name']}"
                    new_col_name.append(name)
                
                else:
                    new_col_name.append(colname)
            st.session_state[f'corpus{c}_df'].columns = load_in(new_col_name)
            st.session_state['final_corpus_df'].columns = load_in(new_col_name)
            st.session_state[f'corpus{c}_namecolname'] = load_in(f"{st.session_state[f'corpus{c}_namecolname']}_{st.session_state[f'corpus{c}_file_name']}")
            
            st.session_state['final_query_colname'] = st.session_state[f'query_namecolname']
            st.session_state['final_corpus_colname'] = st.session_state[f'corpus{c}_namecolname']

            # process NM candidate
            if st.session_state.app2_double_prep:
                # prep 1
                info_session = st.empty()
                info_session.info('Text Preprocess 1/2')
                matched_df1 = name_matching(st.session_state['final_query_df'],st.session_state['final_query_colname'],
                                    st.session_state['final_corpus_df'],st.session_state['final_corpus_colname'],
                                    regex_list = st.session_state.app2_regex_listV1)
                matched_df1['text_preprocess'] = '1'

                # prep 2
                info_session.info('Text Preprocess 2/2')
                matched_df2 = name_matching(st.session_state['final_query_df'],st.session_state['final_query_colname'],
                                    st.session_state['final_corpus_df'],st.session_state['final_corpus_colname'],
                                    regex_list = st.session_state.app2_regex_listV2)
                matched_df2['text_preprocess'] = '2'
                info_session.success('Complete')
                time.sleep(1)
                info_session.empty()
                matched_df = pd.concat([matched_df1,matched_df2])
                print('this is matched double df')
                print(matched_df)
                
            
            else:
                matched_df = name_matching(st.session_state['final_query_df'],st.session_state['final_query_colname'],
                                    st.session_state['final_corpus_df'],st.session_state['final_corpus_colname'],
                                    regex_list = st.session_state.app2_textprocess_regex_list)
            # store results each case
            st.session_state[f'matched{c}_df'] = matched_df.copy()
            st.session_state[f'matched{c}_qc'] = st.session_state['final_query_colname']
            st.session_state[f'matched{c}_cc'] = st.session_state['final_corpus_colname']
        c += 1
    # after finish
    st.session_state.app2_preprocessNM = True
#################################################################################################### 4 Name Matching ####################################################################################################


if 'app2_processThreshold' not in st.session_state:
    st.session_state.app2_processThreshold = False
    st.session_state.app2_processThresholdCounter = 0
    st.session_state['query_matched_results'] = None

def click_submit_threshold():
    if rules not in st.session_state.app2_possible_threshold_list:
        st.session_state.app2_possible_threshold_list.append(rules)
    if st.session_state.app2_double_prep:
        agree4 = False
        agree5 = False
    st.session_state.app2_processThreshold = True

if 'read_df1' not in st.session_state:
    st.session_state.read_df1 = True
    st.session_state.read_df2 = False
    st.session_state.read_df3 = False

def click_read_df1():
    st.session_state.read_df1 = True
    st.session_state.read_df2 = False
    st.session_state.read_df3 = False

def click_read_df2():
    st.session_state.read_df1 = False
    st.session_state.read_df2 = True
    st.session_state.read_df3 = False

def click_read_df3():
    st.session_state.read_df1 = False
    st.session_state.read_df2 = False
    st.session_state.read_df3 = True

#################################################################################################### 5. Results ####################################################################################################
if st.session_state.app2_preprocessNM:
    ## Interactive session
    st.subheader("2.1 กรุณากำหนด :orange[Matching Rules]")
    st.caption("สามารถปรับแต่ง Rule ด้วย Score ต่างๆด้านล่างเพื่อ Match ชื่อ")

    with st.expander("See explanation"):
            st.write('ตัวอย่าง')
            st.caption(':red[สามารถใช้ Text Preprocess เข้ามาช่วย เช่นการตัดคำว่า "บริษัท","จำกัด" จะช่วยให่ Score ทำงานได้ดีขึ้น]')
            st.code('''name1 = 'บริษัท เจริญโภคภัณฑ์อาหาร จำกัด (มหาชน)' \nname2 = 'เครือเจริญโภคภัณฑ์' ''')
            st.write("1. TF-IDF (3-Gram TF-IDF + Cosine Similarity)")
            st.code(''' Tokenize(name1)''')
            st.caption("'บริ|ริษ|ิษั|ษัท|ัท |ท เ| เจ|เจร|จริ|ริญ|ิญโ|ญโภ|โภค|ภคภ|คภั|ภัณ|ัณฑ|ณฑ์|ฑ์อ|์อา|อาห|าหา|หาร|าร |ร จ| จำ|จำก|ำกั|กัด|ัด |ด (| (ม|(มห|มหา|หาช|าชน|ชน)'")
            st.code('''Tokenize(name2)''')
            st.caption("เคร|ครื|รือ|ือเ|อเจ|เจร|จริ|ริญ|ิญโ|ญโภ|โภค|ภคภ|คภั|ภัณ|ัณฑ|ณฑ์")
            st.code('''consine_similarity(TfidfVectorize(Tokenize(name1)),TfidfVectorize(Tokenize(name2)))''')
            st.caption('TF-IDF Cosine Similarity : :green[48.9]')
            #st.divider()
            st.write('2. Fuzzy Ratio')
            st.write('see more information [link](https://github.com/maxbachmann/RapidFuzz)')
            st.code('''FuzzyRatio(name1,name2)''')
            st.caption("Fuzzy Ratio : :green[49.1]")
            st.write('3. Fuzzy Partial Ratio')
            st.write('หลักการเหมือนเหมือนกันกับ Fuzzy Ratio แต่จะให้น้ำหนักกับ "คำที่เหมือนกัน" มากกว่า ความยาวของคำ,การเรียงของคำ')
            st.code('''FuzzyPartialRatio(name1,name2) ''')
            st.caption("Fuzzy Partial Ratio : :green[72.2]")
    col1,col2 = st.columns(2)
    with col1:
        agree = st.checkbox('adjust TF-IDF Score')
    with col2:
        if agree:
            st.session_state.tfidf_score_checkbox = False
        else:
            st.session_state.tfidf_score_checkbox = True

        st.slider(label = 'TF-IDF score >= ',min_value = 0,max_value =  100,value =  70, step = 1,
                    key = 'TFIDF_Score',disabled = st.session_state.tfidf_score_checkbox)
        print(st.write(st.session_state.TFIDF_Score))

    col3,col4 = st.columns(2)
    with col3:
        agree2 = st.checkbox('adjust Fuzzy Ratio')
    with col4:
        if agree2:
            st.session_state.fuzzy_checkbox = False
        else:
            st.session_state.fuzzy_checkbox = True

        st.slider(label = 'fuzzy_ratio >= ',min_value = 0,max_value =  100,value =  70, step = 1,
                    key = 'Fuzzy_Ratio',disabled = st.session_state.fuzzy_checkbox)
        print(st.write(st.session_state.Fuzzy_Ratio))

    col5,col6 = st.columns(2)
    with col5:
        agree3 = st.checkbox('adjust Fuzzy Partial Ratio')
    with col6:
        if agree3:
            st.session_state.fuzzy_partial_checkbox = False
        else:
            st.session_state.fuzzy_partial_checkbox = True

        st.slider(label = 'fuzzy_partial_ratio >= ',min_value = 0,max_value =  100,value =  70, step = 1,
                    key = 'Fuzzy_Partial_Ratio',disabled = st.session_state.fuzzy_partial_checkbox)
        print(st.write(st.session_state.Fuzzy_Partial_Ratio))

    if st.session_state.app2_double_prep:
        agree4 = st.checkbox('only text_process 1')
        agree5 = st.checkbox('only text_process 2')

    index = np.where([agree,agree2,agree3])[0]
    display = np.array(['tfidf_score','fuzzy_ratio','fuzzy_partialratio'])
    values = np.array([st.session_state.TFIDF_Score,st.session_state.Fuzzy_Ratio,st.session_state.Fuzzy_Partial_Ratio])
    user_rules = values[index]
    if len(user_rules) == 1:
        rules = f'{display[index][0]} >= {values[index][0]}'
        add_rule = True
    elif len(user_rules) > 1:
        rules = []
        for i in index:
            rule = f'{display[i]} >= {values[i]}'
            rules.append(rule)
        rules = ' & '.join(rules)
        add_rule = True
    else:
        add_rule = False

    if add_rule:
        if st.session_state.app2_double_prep:
            if agree4:
                rules = rules + ' & text_preprocess == "1"'
            if agree5:
                rules = rules + ' & text_preprocess == "2"'
        st.session_state.rules = rules
        st.write(st.session_state.rules)
    
    submit_botton = st.button('Click to Add Your Rule',key = 'submit_thresh_button',on_click = click_submit_threshold)
    # submit_botton = st.button('Click to Add Your Rule',key = 'submit_button')
    # if submit_botton:
    #     if rules not in st.session_state.app2_possible_threshold_list:
    #         st.session_state.app2_possible_threshold_list.append(rules)
    #     if st.session_state.app2_double_prep:
    #         agree4 = False
    #         agree5 = False
                
    Thresh_List = st_tags(label = '',value = st.session_state.app2_possible_threshold_list,text = '')
    st.caption("*หมายเหตุ: เป็น OR Condition ซึ่งจะ Apply ใช้ทุก Rules เพื่อ Match ชื่อออกมา")
    for v in st.session_state.app2_possible_threshold_list:
        if v not in Thresh_List:
            st.session_state.app2_possible_threshold_list.remove(v)

    #inital for the first render
    if st.session_state.app2_processThresholdCounter == 0:
        st.session_state.processThreshold = True
        st.session_state.prev_len = len(Thresh_List)
        st.session_state.current_len = len(Thresh_List)
        st.session_state.app2_processThresholdCounter += 1
    else:
        st.session_state.current_len = len(Thresh_List)
    # for change in thresh
    if st.session_state.current_len != st.session_state.prev_len:
        st.session_state.prev_len = len(Thresh_List)
        st.session_state.processThreshold = True

    # show candidate results
    st.subheader("Candidate Matched Name")
    if st.session_state.read_df1:
        st.write(f"From file: {st.session_state[f'corpus{1}_file_name']}")
        st.write(st.session_state[f'matched{1}_df'])
        st.write(f"{st.session_state[f'matched{1}_df'].shape[0]} rows , {st.session_state[f'matched{1}_df'].shape[1]} columns")

    elif st.session_state.read_df2:
        st.write(f"From file: {st.session_state[f'corpus{2}_file_name']}")
        st.write(st.session_state[f'matched{2}_df'])
        st.write(f"{st.session_state[f'matched{2}_df'].shape[0]} rows , {st.session_state[f'matched{2}_df'].shape[1]} columns")
    elif st.session_state.read_df3:
        st.write(f"From file: {st.session_state[f'corpus{3}_file_name']}")
        st.write(st.session_state[f'matched{3}_df'])
        st.write(f"{st.session_state[f'matched{3}_df'].shape[0]} rows , {st.session_state[f'matched{3}_df'].shape[1]} columns")

    if sum(st.session_state.order.values()) > 1:
        if st.session_state.order['corpus1'] and st.session_state.order['corpus2'] and st.session_state.order['corpus3']:
            style = (10,1,1,1)
            col1,col2,col3,col4 = st.columns(style)
            with col1:
                st.write('result of each corpus')
            with col2:
                st.button('1',on_click = click_read_df1,key = 'read1')
            with col3:
                st.button('2',on_click= click_read_df2,key = 'read2')
            with col4:
                st.button('3',on_click= click_read_df3,key = 'read3')
        elif st.session_state.order['corpus1'] and st.session_state.order['corpus2']:
            style = (10,1,1)
            col1,col2,col3 = st.columns(style)
            with col1:
                st.write('result of each corpus')
            with col2:
                st.button('1',on_click = click_read_df1,key = 'read1')
            with col3:
                st.button('2',on_click= click_read_df2,key = 'read2')
        


    if st.session_state.processThreshold:
        st.info('Processing NM')
        time.sleep(1)
        #query_mat = pd.DataFrame()
        query_mat = st.session_state['query_df'].filter([st.session_state['query_namecolname']])
        query_mat['MATCHED_NAME'] = np.nan
        c = 1
        for world in st.session_state.order.values():
            print(c)
            if world == True:
                ## from user threshold
                nm_matched = pd.DataFrame()
                #for thresh in st.session_state.possible_threshold_list:
                for thresh in Thresh_List:
                    nm_matched = pd.concat([nm_matched,st.session_state[f'matched{c}_df'].query(thresh)])
                nm_matched = nm_matched.drop_duplicates(st.session_state[f'matched{c}_qc'])

                # get matched results
                if st.session_state.app2_double_prep:
                    res = nm_matched.iloc[:,[-3,-2]]
                else:
                    res = nm_matched.iloc[:,[-2,-1]]
                    
                re_merged = res.merge(st.session_state[f'corpus{c}_df'],
                                    on = st.session_state[f'corpus{c}_namecolname']).drop('corpus_index',axis = 1)

                # collect each corpus results
                if query_mat.MATCHED_NAME.isnull().sum() == len(query_mat):
                    query_mat = query_mat.merge(re_merged,how = 'left',on = st.session_state['query_namecolname'])
                    query_mat.MATCHED_NAME = query_mat.MATCHED_NAME.fillna(query_mat[st.session_state[f'corpus{c}_namecolname']])
                else:
                    re_merged = anti_join(df1 = re_merged,
                                          df2 = query_mat.rename(columns = {"MATCHED_NAME":st.session_state[f'corpus{c}_namecolname']})\
                                                .filter([st.session_state[f'corpus{c}_namecolname']]))
                    if len(re_merged) > 0 :
                        query_mat = query_mat.merge(re_merged,how = 'left',on = st.session_state['query_namecolname'])
                        query_mat.MATCHED_NAME = query_mat.MATCHED_NAME.fillna(query_mat[st.session_state[f'corpus{c}_namecolname']])
                
                # else:
                #     bool_list = np.isin(re_merged[st.session_state[f'corpus{c}_namecolname']],query_mat.MATCHED_NAME,invert = True)
                #     if sum(bool_list) > 1:
                #         re_merged = re_merged[bool_list]
                #         query_mat = query_mat.merge(re_merged,how = 'left',on = st.session_state['query_namecolname'])
                #       query_mat.MATCHED_NAME = query_mat.MATCHED_NAME.fillna(query_mat[st.session_state[f'corpus{c}_namecolname']])
            c += 1
        # duplicate each corpus (sort by number) to get total matched
        query_matched_results = st.session_state['query_df'].merge(query_mat.drop_duplicates(st.session_state['query_namecolname']),\
                                        on = st.session_state['query_namecolname'],how = 'left').drop('query_index',axis = 1)
        st.session_state['query_matched_results'] = query_matched_results
        st.session_state.processThreshold = False
    
    
    # show results
    if st.session_state['query_matched_results'] is not None:
        st.header("3. Matched Results",divider = 'green')
        #total_matched_len = len(nm_matched)
        print(len(st.session_state.query_df))
        total_matched_len = len(st.session_state['query_matched_results'].dropna(subset = 'MATCHED_NAME'))
        matched_percent = np.round(total_matched_len/len(st.session_state.query_df)* 100,1)
        st.success(f'สามารถ Match ได้ :green[{matched_percent}%] จากทั้งหมด', icon="✅")
        st.write(f'เป็นจำนวน {total_matched_len} ชื่อ จากทั้งหมด {len(st.session_state.query_df)}')
        st.caption('หมายเหตุ: ผลสามารถเป็นได้ทั้ง False Positive/Negative ไม่ใช่เป็นการ Confirm Matched')
        st.write(st.session_state['query_matched_results'])
    if 't_end' not in st.session_state:
        st.session_state.t_end = time.time()
        st.write(st.session_state.t_end - st.session_state.t_zero)
        print(st.session_state.t_end - st.session_state.t_zero)

################## Download Results ##################
if 'app2_download_file' not in st.session_state:
    st.session_state.app2_download_file  = False

def click_download():
    st.session_state.app2_download_file = True

def click_fin_download():
    st.session_state.app2_download_file = False

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

if st.session_state.app2_preprocessNM:
    #st.divider()
    if len(st.session_state['query_matched_results']) > 0:
        download_but = st.button('Download',on_click = click_download)

if st.session_state.app2_download_file:
    prompt = False
    submitted = False
    csv = convert_df(st.session_state['query_matched_results'])
    with st.form('chat_input_form'):
        # Create two columns; adjust the ratio to your liking
        col1, col2 = st.columns([3,1]) 
        # Use the first column for text input
        with col1:
            prompt = st.text_input(label = '',value='',placeholder='please write your file_name',label_visibility='collapsed')
        # Use the second column for the submit button
        with col2:
            submitted = st.form_submit_button('Submit')
        
        if prompt and submitted:
            # Do something with the inputted text here
            st.write(f"Your file_name is: {prompt}.csv")

if st.session_state.app2_download_file:
    if prompt and submitted:
        st.download_button(label="Download data as CSV",data = csv,file_name = f'{prompt}.csv',mime='text/csv',on_click = click_fin_download)
