import streamlit as st
import pandas as pd
import numpy as np
import copy
import os
import re
from tqdm import tqdm
import time
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from Utils.nm_utils import *

from stqdm import stqdm
from streamlit_tags import st_tags
from PIL import Image
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_extras.colored_header import colored_header
from streamlit_extras.switch_page_button import switch_page

#st.set_page_config(page_title="Name Matching APP", layout="centered",initial_sidebar_state="collapsed")
st.set_page_config(initial_sidebar_state = 'collapsed')
st.title("Name Matching APP")

@st.cache_data
def init_data(path,name_colname):
    df = pd.read_csv(path)
    df = df.dropna(subset = name_colname)
    return df

@st.cache_data
def init_dataV2(path,name_colname,index_colname):
    df = pd.read_csv(path)
    df = df.dropna(subset = name_colname)
    df = df.reset_index(drop = True).reset_index()
    df.rename(columns = {'index':index_colname},inplace = True)
    return df

@st.cache_data(ttl=3600)
def init_data_upload_query(uploaded_file,option):
    user_df = uploaded_file.copy(deep = True)
    user_colname = copy.deepcopy(option)
    user_df = user_df.dropna(subset = user_colname)
    user_df = user_df.reset_index(drop = True).reset_index()
    user_df.rename(columns = {'index':'query_index'},inplace = True)
    return user_df,user_colname

@st.cache_data(ttl=3600)
def init_data_upload_corpus(uploaded_file,option):
    user_df = uploaded_file.copy(deep = True)
    user_colname = copy.deepcopy(option)
    user_df = user_df.dropna(subset = user_colname)
    user_df = user_df.reset_index(drop = True).reset_index()
    user_df.rename(columns = {'index':'corpus_index'},inplace = True)
    return user_df,user_colname

@st.cache_data(ttl=3600)
def load_in(input_):
    output = input_
    return output

if 'regex_list' not in st.session_state:
    st.session_state.regex_list = None
    st.session_state.default_regex_list = copy.deepcopy(default_regex_list)
    st.session_state.developer_regex_list = copy.deepcopy(soft_simp_words)
    st.session_state.developer_regex_listV2 = copy.deepcopy(hard_simp_words)
    st.session_state.regex_listV1 = None
    st.session_state.regex_listV2 = None

possible_threshold_list = ["tfidf_score >= 60 & fuzzy_ratio >= 90 & fuzzy_partialratio >= 90","tfidf_score >= 66.7 & fuzzy_partialratio >= 97","tfidf_score >= 70"]
if 'possible_threshold_list' not in st.session_state:
    st.session_state.possible_threshold_list = possible_threshold_list

if 'preprocessNM' not in st.session_state:
    st.session_state.preprocessNM = False

def finish_upload_click():
    st.session_state.upload_stage = True
    st.session_state.start_nm = True

if 'upload_stage' not in st.session_state:
    st.session_state.upload_stage = False
    st.session_state.preprocessed = False
    st.session_state.start_nm = False
    st.session_state.choices  = 'default'

if 'app1_ExportOutput' not in st.session_state:
    st.session_state.app1_ExportOutput = None
################################################ Application ################################################

###### 0. Upload Dataset
if not st.session_state.upload_stage:
    q_option = None
    c_option = None
    df_query = None
    st.header("Please Upload Your Dataset")
    left,right = st.columns(2)
    with left:
        query_section = st.empty()
        with query_section.container():
            # check query input
            if st.session_state.app1_ExportOutput is None:
                query_upload = st.file_uploader("Choose a file to query",key = 'query_upload')
                if query_upload is not None:
                    df_query = pd.read_csv(query_upload)
            elif st.session_state.app1_ExportOutput is not None:
                df_query = st.session_state.app1_ExportOutput
            # select columns
            if df_query is not None:
                # select col
                q_box_list = [None]
                q_box_list.extend(df_query.columns)
                q_option = st.selectbox(
                'Which is Names Column ?',
                    q_box_list)
                if q_option is not None:
                    st.session_state.df_query,st.session_state.query_colname = init_data_upload_query(df_query,q_option)
                    st.write('your query dataset')
                    st.write(st.session_state.df_query.head())
    with right:
        corpus_section = st.empty()
        with corpus_section.container():
            corpus_upload = st.file_uploader("Choose a file to match with ",key = 'corpus_upload')
            if corpus_upload is not None:
                df_corpus_upload = pd.read_csv(corpus_upload)
                #select col
                c_box_list = [None]
                c_box_list.extend(df_corpus_upload.columns)
                c_option = st.selectbox(
                'Which is Names Column ?',
                    c_box_list)
                if c_option is not None:
                    st.session_state.df_corpus,st.session_state.corpus_colname = init_data_upload_corpus(df_corpus_upload,c_option)
                    st.write('your corpus dataset')
                    st.write(st.session_state.df_corpus.head())

    if (q_option is not None) and (c_option is not None):
        finish_upload_button =  st.button('Submit To Start',on_click = finish_upload_click)                

if st.session_state.upload_stage:
    with st.expander('See More Explanation'):
        mat_img = Image.open("Material/images/nm_textprep.jpg")
        st.image(mat_img)
################################################ 1. Text Preprocess 
if (st.session_state.upload_stage == False) and (st.session_state.regex_list is None):


    #colored_header("1. Text Preprocess",color_name= "red-70",description='')
    st.header("1. Text Preprocess",divider= 'orange')
    st.caption("Text Preprocess จะทำการลบ keywords (regex) ดังกล่าว ในชื่อทั้งหมดของ Dataset")
    st.caption('_(หากกรอก keyword ที่เป็นภาษาอังกฤษ กรุณาใช้ UPPER CASE)_')
    #st.header("1. Text Preprocess")

    regex_section = st.empty()
    with regex_section.container():
        container = st.container()
        container2 = st.container()

        double_prep = st.checkbox('Optional Double Text Preprocess (for more specific)')
        if double_prep:
            st.session_state.double_prep = True
        else:
            st.session_state.double_prep = False

        agree = st.checkbox('Developer Choices*')
        if agree:
            st.session_state.choices = 'developer'
        else:
            st.session_state.choices = 'default'            

        with container: # to put it to top of checkbox
            if st.session_state.choices == 'default':
                regex_tags = st_tags(label = 'Text Preprocess',value = st.session_state.default_regex_list,text = 'regex',maxtags = -1)
            elif st.session_state.choices == 'developer':
                regex_tags = st_tags(label = 'Text Preprocess',value = st.session_state.developer_regex_list,text = 'soft_simplify',maxtags= -1)

        if st.session_state.double_prep:
            with container2: # to put it to top of checkbox
                if st.session_state.choices == 'default':
                    regex_tagsV2 = st_tags(label = 'Text Preprocess II.',value = ['บริษัท','จำกัด','มหาชน','INC'],text = 'regex',maxtags = -1)
                elif st.session_state.choices == 'developer':
                    regex_tagsV2 = st_tags(label = 'Text Preprocess II.',value = st.session_state.developer_regex_listV2,text = 'hard_simplify',maxtags= -1)
            
        ### submit to next-step                            
        regex_submit_button = st.button("Submit your Regex choices",key = 'regex_customize_submit_button')
        if regex_submit_button:
            if st.session_state.double_prep:
                st.session_state.regex_listV1 = load_in(regex_tags)
                st.session_state.regex_listV2 = load_in(regex_tagsV2)
                st.session_state.regex_list = load_in(['not_empty'])
            else:
                st.session_state.regex_list = load_in(regex_tags)
            regex_section.empty()
            
if (st.session_state.regex_list is None):
    backPage = st.button('Back',key = 'get_back')
    if backPage:
        st.session_state.app1_nameseer = True 
        st.session_state.app1_regex = False
        switch_page('classify holder')
################################################ 2. Name Matching ################################################
if st.session_state.regex_list is not None:
    #colored_header("2. Name Matching",color_name= "red-70",description='')
    st.header("2. Name Matching",divider = 'orange')

    if st.session_state.double_prep:
        # prep 1
        query_names1,corpus_names1 = text_preprocess_byRegex(st.session_state.df_query,st.session_state.query_colname,
                                                       st.session_state.df_corpus,st.session_state.corpus_colname,
                                                       regex_list = st.session_state.regex_listV1)
        df_query1,df_corpus1 = wrap_up_material(st.session_state.df_query,st.session_state.df_corpus,
                                            query_names1,corpus_names1)

        matched_df1 = extract_NM(df_query1,df_query1.query_name,st.session_state.query_colname,
                                df_corpus1,df_corpus1.corpus_name,st.session_state.corpus_colname)
        matched_df1['text_preprocess'] = '1'

        # prep 2
        query_names2,corpus_names2 = text_preprocess_byRegex(st.session_state.df_query,st.session_state.query_colname,
                                                       st.session_state.df_corpus,st.session_state.corpus_colname,
                                                       regex_list = st.session_state.regex_listV2)
        df_query2,df_corpus2 = wrap_up_material(st.session_state.df_query,st.session_state.df_corpus,
                                            query_names2,corpus_names2)

        matched_df2 = extract_NM(df_query2,df_query2.query_name,st.session_state.query_colname,
                                df_corpus2,df_corpus2.corpus_name,st.session_state.corpus_colname)
        matched_df2['text_preprocess'] = '2'
        
        matched_df = load_in(pd.concat([matched_df1,matched_df2]))
        matched_df.rename(columns = {'query_name':f'cleaned_{st.session_state.query_colname}','corpus_name':f'cleaned_{st.session_state.corpus_colname}'},inplace = True)
       
        st.session_state.preprocessNM = True

    else:
        query_names,corpus_names = text_preprocess_byRegex(st.session_state.df_query,st.session_state.query_colname,
                                                        st.session_state.df_corpus,st.session_state.corpus_colname,
                                                        regex_list = st.session_state.regex_list)
        df_query,df_corpus = wrap_up_material(st.session_state.df_query,st.session_state.df_corpus,
                                            query_names,corpus_names)

        
        matched_df = extract_NM(df_query,df_query.query_name,st.session_state.query_colname,
                                df_corpus,df_corpus.corpus_name,st.session_state.corpus_colname)
        matched_df.rename(columns = {'query_name':f'cleaned_{st.session_state.query_colname}','corpus_name':f'cleaned_{st.session_state.corpus_colname}'},inplace = True)
        #st.subheader("Candidate Matched Results")
        #st.dataframe(dataframe_explorer(matched_df),use_container_width= True)
        st.session_state.preprocessNM = True

################################################ 3. Matched Results ################################################
if st.session_state.preprocessNM:
    ## Interactive session
    #st.warning('กรุณากำหนด Matching Rules')
    st.subheader("2.1 กรุณากำหนด :orange[Matching Rules]")
    #st.error('กรุณากำหนด Matching Rules')
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

        st.slider(label = 'fuzzy_partial_ratio >= ',min_value = 0,max_value =  100,value =  70, step = 1,
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

        st.slider(label = 'fuzzy_tokenset_ratio >= ',min_value = 0,max_value =  100,value =  70, step = 1,
                    key = 'Fuzzy_Partial_Ratio',disabled = st.session_state.fuzzy_partial_checkbox)
        print(st.write(st.session_state.Fuzzy_Partial_Ratio))

    if st.session_state.double_prep:
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
        if st.session_state.double_prep:
            if agree4:
                rules = rules + ' & text_preprocess == "1"'
            if agree5:
                rules = rules + ' & text_preprocess == "2"'
        st.session_state.rules = rules
        st.write(st.session_state.rules)
    
    submit_botton = st.button('Click to Add Your Rule',key = 'submit_button')
    if submit_botton:
        if rules not in st.session_state.possible_threshold_list:
            st.session_state.possible_threshold_list.append(rules)
        if st.session_state.double_prep:
            agree4 = False
            agree5 = False
                
    Thresh_List = st_tags(label = '',value = st.session_state.possible_threshold_list,text = '')
    st.caption("*หมายเหตุ: เป็น OR Condition ซึ่งจะ Apply ใช้ทุก Rules เพื่อ Match ชื่อออกมา")
    for v in st.session_state.possible_threshold_list:
        if v not in Thresh_List:
            st.session_state.possible_threshold_list.remove(v)

    st.write("ข้อมูลทั้งหมดที่ Query ขึ้นมาได้และมีความน่าจะเป็นชื่อที่ Match")
    st.dataframe(dataframe_explorer(matched_df),use_container_width= True)
    st.divider()

    ## from user threshold
    nm_matched = pd.DataFrame()
    for thresh in Thresh_List:
        nm_matched = pd.concat([nm_matched,matched_df.query(thresh)])
    nm_matched = nm_matched.drop_duplicates(st.session_state.query_colname)
    st.session_state.preprocessNM = True

if st.session_state.preprocessNM:
    st.header("3. Matched Results",divider = 'green')
    #colored_header("3. Matched Results",color_name= "green-70",description='')
    #st.header("3. Matched Results")
    total_matched_len = len(nm_matched)
    matched_percent = np.round(total_matched_len/len(st.session_state.df_query)* 100,1)
    #st.subheader(f'สามารถ Match ได้ {matched_percent}% จากทั้งหมด')
    st.success(f'สามารถ Match ได้ :green[{matched_percent}%] จากทั้งหมด', icon="✅")
    st.write(f'เป็นจำนวน {total_matched_len} ชื่อ จากทั้งหมด {len(st.session_state.df_query)}')
    st.caption('หมายเหตุ: ผลสามารถเป็นได้ทั้ง False Positive/Negative ไม่ใช่เป็นการ Confirm Matched')
    if 'possible_col' not in st.session_state:
        st.session_state.possible_col = nm_matched.columns.values
    col_selection = st.multiselect(label = 'Select Column',
                        options = st.session_state.possible_col, default = st.session_state.possible_col,
                        key = 'col_selection')
    filtered_df = dataframe_explorer(nm_matched.filter(col_selection))
    st.dataframe(filtered_df)
    st.info("กรณีชื่อที่ไม่ Matched จะมี Next Step สำหรับกการ Assign SNA")
    #st.caption(':green[กรณีชื่อที่ไม่ Matched จะมี Next Step สำหรับกการ Assign SNA]')

def click_get_back():
    st.session_state.regex_list = None
    st.session_state.start_nm = True
    st.session_state.preprocessNM = False
    
if st.session_state.preprocessNM:
    get_back = st.button('Back',key = 'get_back',on_click = click_get_back)