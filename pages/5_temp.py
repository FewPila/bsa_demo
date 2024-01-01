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
stqdm.pandas()

#################################################################### App 3 Session ######################################################################


#################################################################### 3.1 Add SNA10 and customize ISIC,Keywords and etc. ######################################################################

if 'app3_rule_based' not in st.session_state:
    st.session_state['app3_rule_based'] = False
    st.session_state['app3_rule_based_prioritize'] = False

if 'page1' not in st.session_state:
    st.session_state['page1'] = True
    st.session_state['page2'] = False
    st.session_state['page3'] = False


@st.cache_data
def load_in(input_):
    return input_


if 'rule_based1' not in st.session_state:
    st.session_state['rule_based1'] = False
    st.session_state['rule_based2'] = False
    st.session_state['rule_based3'] = False


############################################################## 1.FIRM_TH ##############################################################
if st.session_state['app3_rule_based'] == False:
    style = (8,2,2,2)
    fake_col,col_page1,col_page2,col_page3 = st.columns(style)

    def render_page1():
        st.session_state['page1'] = True
        st.session_state['page2'] = False
        st.session_state['page3'] = False

    def render_page2():
        st.session_state['page1'] = False
        st.session_state['page2'] = True
        st.session_state['page3'] = False

    def render_page3():
        st.session_state['page1'] = False
        st.session_state['page2'] = False
        st.session_state['page3'] = True   
    
    with col_page1:
        st.button('TH',on_click = render_page1,key = 'read1')
    with col_page2:
        st.button('ENG',on_click= render_page2,key = 'read2')
    with col_page3:
        st.button('Person',on_click= render_page3,key = 'read3')

    if st.session_state['page1']:
        rule_based_container1 = st.container()
        
        target_rule_based1 =  st.selectbox(label = '',options = ['Firm-TH','Firm-ENG','Person'],index = 0,key = 'target_rule_based1',label_visibility= 'collapsed')
        

        if bool(re.search('TH',str(st.session_state['target_rule_based1']).upper())):
            with rule_based_container1:
                st.header(f"Rule-based สำหรับ {st.session_state['target_rule_based1']}",divider = 'blue')
            
            ## 1. Rule Based
            if st.session_state['rule_based1'] == False:
                st.radio(label = '',options = ['default','customize'],index = 0,key = 'rule_based1_radio',label_visibility= 'collapsed')
                check_box_container1 = st.container()
            ################################################# Rule-based Iisc #################################################
                if bool(re.search('DEFAULT',str(st.session_state['rule_based1_radio']).upper())):
                    st.session_state['isic1_checkbox_bool'] = True
                    st.session_state['keywords1_checkbox_bool'] = True
                    st.session_state['nat1_checkbox_bool'] = True
                else:
                    st.session_state['isic1_checkbox_bool'] = False
                    st.session_state['keywords1_checkbox_bool'] = False
                    st.session_state['nat1_checkbox_bool'] = False

                with check_box_container1:
                    st.divider()
                    st.subheader('Apply')
                    isic1_checkbox = st.checkbox('Rule based : isic',key = 'isic1_checkbox',value =  st.session_state['isic1_checkbox_bool'])
                    keywords1_checkbox = st.checkbox('Rule based : keywords',key = 'keywords1_checkbox',value = st.session_state['keywords1_checkbox_bool'])
                    nat1_checkbox = st.checkbox('Rule based : nationalities',key = 'nat1_checkbox',value = st.session_state['nat1_checkbox_bool'])
                    

                if 'isic_catalog1' not in st.session_state:
                    st.session_state.isic_catalog1 = pd.read_excel("data/app3_demo_info.xlsx",sheet_name= 'isics')

                if 'add_isic_section1' not in st.session_state:
                    st.session_state.add_isic_section1 = False

                def save_submit_isic1(add):
                    fake_df = pd.DataFrame({'target_sna10':[add],'isic4':[None]})
                    st.session_state.isic_catalog1 = pd.concat([st.session_state.isic_catalog1,fake_df])

                isic1_session = []
                
                if bool(re.search('DEFAULT',str(st.session_state['rule_based1_radio']).upper())) and st.session_state['isic1_checkbox']:
                    st.header('I. Isic Adjust',divider= 'blue')
                    # apply on th or all
                    isic_container1 = st.container()
                    isic_left1,isic_right1 = st.columns(2)
                    isic_c1 = 1
                    for sna_10 in st.session_state.isic_catalog1['target_sna10'].unique():
                        with isic_container1:
                            cur_isic1 = st.session_state.isic_catalog1.query("target_sna10 == @sna_10")
                            isic_v1 = cur_isic1['isic4'].values.tolist()
                            if isic_c1 % 2 == 0:
                                with isic_right1:
                                    st.subheader(f":gray[{sna_10}]")
                                    st_tags(label = '',value = isic_v1,key = f'isic1_{sna_10}')
                            else:
                                with isic_left1:
                                    st.subheader(f":gray[{sna_10}]")
                                    st_tags(label = '',value = isic_v1,key = f'isic1_{sna_10}')
                            isic_c1 += 1
                            isic1_session.append(f'isic1_{sna_10}')
                    
                    if st.session_state.add_isic_section1 == False: 
                        with st.container():
                            st.write('เพิ่มประเภท SNA')
                            isic1_left,isic1_right = st.columns([10,20])
                            with isic1_left:
                                add_isic1 = st.text_input(label = '', placeholder= 'พิมพ์ประเภท SNA และกด Add',label_visibility='collapsed',key = 'add_isic1')
                            add_isic_bt1 = st.button(label = 'Add',on_click = save_submit_isic1, args = ([add_isic1]),key = 'add_isic_bt1')

                    ################################################# Rule-based Keyword #################################################
                if bool(re.search('DEFAULT',str(st.session_state['rule_based1_radio']).upper())) and st.session_state['keywords1_checkbox']:
                    if 'keywords_catalog1' not in st.session_state:
                        st.session_state.keywords_catalog1 = pd.read_excel("data/app3_demo_info.xlsx",sheet_name = 'keywords')

                    if 'add_keyword_section1' not in st.session_state:
                        st.session_state.add_keyword_section1 = False

                    def save_submit_keyword1(add):
                        fake_df = pd.DataFrame({'target_sna10':[add],'word_token':[None]})
                        st.session_state.keywords_catalog1 = pd.concat([st.session_state.keywords_catalog1,fake_df])

                    st.divider()
                    st.header('II. Keywords Adjust',divider = 'blue')
                    keywords_container1 = st.container()
                    keywords_left1,keywords_right1 = st.columns(2)
                    keywords_c1 = 1
                    keywords1_section = []
                    for sna_10 in st.session_state.keywords_catalog1['target_sna10'].unique():
                        cur_keyword1 = st.session_state.keywords_catalog1.query("target_sna10 == @sna_10")
                        keywords_v1 = cur_keyword1['word_token'].values.tolist()
                        with keywords_container1:
                            if keywords_c1 % 2 == 0:
                                with keywords_right1:
                                    st.subheader(f":gray[{sna_10}]")
                                    st_tags(label = '',value = keywords_v1,key = f'keywords1_{sna_10}')
                            else:
                                with keywords_left1:
                                    st.subheader(f":gray[{sna_10}]")
                                    st_tags(label = '',value = keywords_v1,key = f'keywords1_{sna_10}')
                        keywords_c1  += 1
                        keywords1_section.append(f'keywords1_{sna_10}')
                    

                    if st.session_state.add_keyword_section1 == False: 
                        with st.container():
                            st.write('เพิ่มประเภท SNA')
                            keywords1_left,keywords1_right = st.columns([10,20])
                            with keywords1_left:
                                add_keyword1 = st.text_input(label = '', placeholder= 'พิมพ์ประเภท SNA และกด Add',label_visibility='collapsed',key = 'add_keyword1')
                            add_keyword_bt1 = st.button(label = 'Add',on_click = save_submit_keyword1, args = ([add_keyword1]),key = 'add_keyword_bt1')
                    
                    ################################################# Rule-based Nationalities #################################################
                if bool(re.search('DEFAULT',str(st.session_state['rule_based1_radio']).upper())) and st.session_state['nat1_checkbox']:
                    st.divider()
                    
                    st.header('III. Nationalities Rule-based',divider= 'blue')
                    if 'nat_catalog1' not in st.session_state:
                        st.session_state.nat_catalog1 = []
                    
                    rule_based1_nat_v_choices = [None,'ROW','ONFC']
                    rule_based1_left_nat_v,rule_based1_right_nat_v = st.columns([20,10])
                    
                    rule_based1_left_nat_v.subheader(f':blue[กรณีบริษัทเป็นสัญชาติไทย จะมีค่า SNA :]')
                    rule_based1_right_nat_v.selectbox(label = '',options = rule_based1_nat_v_choices,index = 2,key = 'rule_based1_first_nat_v',label_visibility = 'collapsed')
                    rule_based1_left_nat_v.subheader(f':blue[กรณีบริษัทเป็นต่างชาติจะมีค่า SNA :]')
                    rule_based1_right_nat_v.selectbox(label = '',options = rule_based1_nat_v_choices,index = 1,key = 'rule_based1_second_nat_v',label_visibility = 'collapsed')
                    st.divider()

                ### Submit rule-based
                # submit rules
                def submit_rule_based1():
                    ### Collect isic's action
                    if st.session_state['isic1_checkbox']:
                        isics_df = pd.DataFrame()
                        for key in isic1_session:
                            new_dict = dict( target_sna10 = np.array([key]), isic4 = np.array(st.session_state[key]))
                            new_df = pd.DataFrame.from_dict(new_dict, orient='index').transpose()
                            isics_df = pd.concat([isics_df,new_df])
                        isics_df['target_sna10'] = isics_df['target_sna10'].ffill()
                        isics_df['target_sna10'] = isics_df['target_sna10'].str.replace('isic1_','') 
                        st.session_state['rule_based1_isic_action'] = isics_df
                    else:
                        st.session_state['rule_based1_isic_action'] = None

                    if st.session_state['keywords1_checkbox']:
                        ### Collect keywords's action
                        keywords_df = pd.DataFrame()
                        for key in keywords1_section:
                            new_dict = dict( target_sna10 = np.array([key]), word_token = np.array(st.session_state[key]))
                            new_df = pd.DataFrame.from_dict(new_dict, orient='index').transpose()
                            keywords_df = pd.concat([keywords_df,new_df])
                        keywords_df['target_sna10'] = keywords_df['target_sna10'].ffill()
                        keywords_df['target_sna10'] = keywords_df['target_sna10'].str.replace('keywords1_','') 
                        st.session_state['rule_based1_keywords_action'] = keywords_df
                    else:
                        st.session_state['rule_based1_keywords_action'] = None

                    ### Collect Nationalities's action
                    if st.session_state['nat1_checkbox']:
                        st.session_state['rule_based1_nat_else_th'] = st.session_state['rule_based1_first_nat_v']
                        st.session_state['rule_based1_nat_else_nonth'] = st.session_state['rule_based1_second_nat_v']
                    else:
                        st.session_state['rule_based1_nat_else_th'] = None
                        st.session_state['rule_based1_nat_else_nonth'] = None

                    # submit rules-based
                    st.session_state['isic1_checkbox_out'] = load_in(st.session_state['isic1_checkbox'])
                    st.session_state['keywords1_checkbox_out'] = load_in(st.session_state['keywords1_checkbox'])
                    st.session_state['nat1_checkbox_out'] = load_in(st.session_state['nat1_checkbox'])
                    st.session_state['rule_based1'] = True
                    
                # submit button
                if st.session_state['rule_based1'] == False:
                    st.button('submit rule-based 1',key ='submit_rule_based1',on_click = submit_rule_based1)
            
            # after-submit
            else:
                st.write(st.session_state['rule_based1_isic_action'])
                st.write(st.session_state['rule_based1_keywords_action'])
                st.write(st.session_state['rule_based1_nat_else_th'], st.session_state['rule_based1_nat_else_nonth'])
                st.write('Submitted')
    ############################################################## 1.FIRM_TH ##############################################################


   ############################################################## 2.FIRM_EN ##############################################################
    if st.session_state['page2']:
        rule_based_container2 = st.container()
        
        target_rule_based2 =  st.selectbox(label = '',options = ['Firm-TH','Firm-ENG','Person'],index = 1,key = 'target_rule_based2',label_visibility= 'collapsed')
        

        if bool(re.search('EN',str(st.session_state['target_rule_based2']).upper())):
            with rule_based_container2:
                st.header(f"Rule-based สำหรับ {st.session_state['target_rule_based2']}",divider = 'blue')
            
            ## 1. Rule Based
            if st.session_state['rule_based2'] == False:
                st.radio(label = '',options = ['default','customize'],index = 0,key = 'rule_based2_radio',label_visibility= 'collapsed')
                check_box_container2 = st.container()
            ################################################# Rule-based Iisc #################################################
                if bool(re.search('DEFAULT',str(st.session_state['rule_based2_radio']).upper())):
                    st.session_state['isic2_checkbox_bool'] = False
                    st.session_state['keywords2_checkbox_bool'] = True
                    st.session_state['nat2_checkbox_bool'] = True
                else:
                    st.session_state['isic2_checkbox_bool'] = False
                    st.session_state['keywords2_checkbox_bool'] = False
                    st.session_state['nat2_checkbox_bool'] = False

                with check_box_container2:
                    st.divider()
                    st.subheader('Apply')
                    isic2_checkbox = st.checkbox('Rule based : isic',key = 'isic2_checkbox',value =  st.session_state['isic2_checkbox_bool'])
                    keywords2_checkbox = st.checkbox('Rule based : keywords',key = 'keywords2_checkbox',value = st.session_state['keywords2_checkbox_bool'])
                    nat2_checkbox = st.checkbox('Rule based : nationalities',key = 'nat2_checkbox',value = st.session_state['nat2_checkbox_bool'])
                    
                if 'isic_catalog2' not in st.session_state:
                    st.session_state.isic_catalog2 = pd.read_excel("data/app3_demo_info.xlsx",sheet_name= 'isics')

                if 'add_isic_section2' not in st.session_state:
                    st.session_state.add_isic_section2 = False

                def save_submit_isic2(add):
                    fake_df = pd.DataFrame({'target_sna10':[add],'isic4':[None]})
                    st.session_state.isic_catalog2 = pd.concat([st.session_state.isic_catalog2,fake_df])

                isic2_session = []
                
                if bool(re.search('DEFAULT',str(st.session_state['rule_based2_radio']).upper()) and st.session_state['isic2_checkbox']):
                    st.header('I. Isic Adjust',divider= 'orange')
                    # apply on th or all
                    isic_container2 = st.container()
                    isic_left2,isic_right2 = st.columns(2)
                    isic_c2 = 1
                    for sna_10 in st.session_state.isic_catalog2['target_sna10'].unique():
                        with isic_container2:
                            cur_isic2 = st.session_state.isic_catalog2.query("target_sna10 == @sna_10")
                            isic_v2 = cur_isic2['isic4'].values.tolist()
                            if isic_c2 % 2 == 0:
                                with isic_right2:
                                    st.subheader(f":gray[{sna_10}]")
                                    st_tags(label = '',value = isic_v2,key = f'isic2_{sna_10}')
                            else:
                                with isic_left2:
                                    st.subheader(f":gray[{sna_10}]")
                                    st_tags(label = '',value = isic_v2,key = f'isic2_{sna_10}')
                            isic_c2 += 1
                            isic2_session.append(f'isic2_{sna_10}')
                    
                    if st.session_state.add_isic_section2 == False: 
                        with st.container():
                            st.write('เพิ่มประเภท SNA')
                            isic2_left,isic2_right = st.columns([10,20])
                            with isic2_left:
                                add_isic2 = st.text_input(label = '', placeholder= 'พิมพ์ประเภท SNA และกด Add',label_visibility='collapsed',key = 'add_isic2')
                            add_isic_bt2 = st.button(label = 'Add',on_click = save_submit_isic2, args = ([add_isic2]),key = 'add_isic_bt2')

                ################################################# Rule-based Keyword #################################################
                if 'keywords_catalog2' not in st.session_state:
                    st.session_state.keywords_catalog2 = pd.read_excel("data/app3_demo_info.xlsx",sheet_name = 'keywords_en')
                    #if df['target_sna10'].value_counts().max() > 1:
                    #    df = df.groupby('target_sna10')['word_token'].apply('|'.join).reset_index()

                if 'add_keyword_section2' not in st.session_state:
                    st.session_state.add_keyword_section2 = False

                def save_submit_keyword2(add):
                    fake_df = pd.DataFrame({'target_sna10':[add],'word_token':[None]})
                    st.session_state.keywords_catalog2 = pd.concat([st.session_state.keywords_catalog2,fake_df])

                if bool(re.search('DEFAULT',str(st.session_state['rule_based2_radio']).upper())) and st.session_state['keywords2_checkbox']:
                    st.divider()
                    st.header('II. Keywords Adjust',divider = 'orange')
                    keywords_container2 = st.container()
                    keywords_left2,keywords_right2 = st.columns(2)
                    keywords_c2 = 1
                    keywords2_section = []
                    for sna_10 in st.session_state.keywords_catalog2['target_sna10'].unique():
                        cur_keyword2 = st.session_state.keywords_catalog2.query("target_sna10 == @sna_10")
                        keywords_v2 = cur_keyword2['word_token'].values.tolist()
                        with keywords_container2:
                            if keywords_c2 % 2 == 0:
                                with keywords_right2:
                                    st.subheader(f":gray[{sna_10}]")
                                    st_tags(label = '',value = keywords_v2,key = f'keywords2_{sna_10}')
                            else:
                                with keywords_left2:
                                    st.subheader(f":gray[{sna_10}]")
                                    st_tags(label = '',value = keywords_v2,key = f'keywords2_{sna_10}')
                        keywords_c2  += 1
                        keywords2_section.append(f'keywords2_{sna_10}')
                    

                    if st.session_state.add_keyword_section2 == False: 
                        with st.container():
                            st.write('เพิ่มประเภท SNA')
                            keywords2_left,keywords2_right = st.columns([10,20])
                            with keywords2_left:
                                add_keyword2 = st.text_input(label = '', placeholder= 'พิมพ์ประเภท SNA และกด Add',label_visibility='collapsed',key = 'add_keyword2')
                            add_keyword_bt2 = st.button(label = 'Add',on_click = save_submit_keyword2, args = ([add_keyword2]),key = 'add_keyword_bt2')
                    st.divider()
                    ################################################# Rule-based Nationalities #################################################
                    
                    
                if bool(re.search('DEFAULT',str(st.session_state['rule_based2_radio']).upper())) and st.session_state['nat2_checkbox']:
                    st.header('III. Nationalities Rule-based',divider= 'orange')
                    if 'nat_catalog2' not in st.session_state:
                        st.session_state.nat_catalog2 = []
                    
                    rule_based2_nat_v_choices = [None,'ROW','ONFC']
                    rule_based2_left_nat_v,rule_based2_right_nat_v = st.columns([20,10])
                    
                    rule_based2_left_nat_v.subheader(f':blue[กรณีบริษัทเป็นสัญชาติไทย จะมีค่า SNA :]')
                    rule_based2_right_nat_v.selectbox(label = '',options = rule_based2_nat_v_choices,index = 2,key = 'rule_based2_first_nat_v',label_visibility = 'collapsed')
                    rule_based2_left_nat_v.subheader(f':blue[กรณีบริษัทเป็นต่างชาติจะมีค่า SNA :]')
                    rule_based2_right_nat_v.selectbox(label = '',options = rule_based2_nat_v_choices,index = 1,key = 'rule_based2_second_nat_v',label_visibility = 'collapsed')
                    st.divider()


                ### Submit rule-based
                # submit rules
                def submit_rule_based2():
                    ### Collect isic's action
                    if st.session_state['isic2_checkbox']:
                        isics_df = pd.DataFrame()
                        for key in isic2_session:
                            new_dict = dict( target_sna10 = np.array([key]), isic4 = np.array(st.session_state[key]))
                            new_df = pd.DataFrame.from_dict(new_dict, orient='index').transpose()
                            isics_df = pd.concat([isics_df,new_df])
                        isics_df['target_sna10'] = isics_df['target_sna10'].ffill()
                        isics_df['target_sna10'] = isics_df['target_sna10'].str.replace('isic2_','') 
                        st.session_state['rule_based2_isic_action'] = isics_df
                    else:
                        st.session_state['rule_based2_isic_action'] = None

                    if st.session_state['keywords2_checkbox']:
                        ### Collect keywords's action
                        keywords_df = pd.DataFrame()
                        for key in keywords2_section:
                            new_dict = dict( target_sna10 = np.array([key]), word_token = np.array(st.session_state[key]))
                            new_df = pd.DataFrame.from_dict(new_dict, orient='index').transpose()
                            keywords_df = pd.concat([keywords_df,new_df])
                        keywords_df['target_sna10'] = keywords_df['target_sna10'].ffill()
                        keywords_df['target_sna10'] = keywords_df['target_sna10'].str.replace('keywords2_','') 
                        st.session_state['rule_based2_keywords_action'] = keywords_df
                    else:
                        st.session_state['rule_based2_keywords_action'] = None

                    ### Collect Nationalities's action
                    if st.session_state['nat2_checkbox']:
                        st.session_state['rule_based2_nat_else_th'] = st.session_state['rule_based2_first_nat_v']
                        st.session_state['rule_based2_nat_else_nonth'] = st.session_state['rule_based2_second_nat_v']
                    else:
                        st.session_state['rule_based2_nat_else_th'] = None
                        st.session_state['rule_based2_nat_else_nonth'] = None
                    
                    st.session_state['isic2_checkbox_out'] = load_in(st.session_state['isic2_checkbox'])
                    st.session_state['keywords2_checkbox_out'] = load_in(st.session_state['keywords2_checkbox'])
                    st.session_state['nat2_checkbox_out'] = load_in(st.session_state['nat2_checkbox'])
                    
                    # submit rules-based
                    st.session_state['rule_based2'] = True
                    
                # submit button
                if st.session_state['rule_based2'] == False:
                    st.button('submit rule-based 2',key ='submit_rule_based2',on_click = submit_rule_based2)
            
            # after-submit
            else:
                st.write(st.session_state['rule_based2_isic_action'])
                st.write(st.session_state['rule_based2_keywords_action'])
                st.write(st.session_state['rule_based2_nat_else_th'], st.session_state['rule_based2_nat_else_nonth'])
                st.write('Submitted')
    ############################################################## 2.FIRM_EN ##############################################################




    ############################################################## 3.Person ##############################################################
    if st.session_state['page3']:
        rule_based_container3 = st.container()
        
        target_rule_based3 =  st.selectbox(label = '',options = ['Firm-TH','Firm-ENG','Person'],index = 2,key = 'target_rule_based3',label_visibility= 'collapsed')
        

        if bool(re.search('PER',str(st.session_state['target_rule_based3']).upper())):
            with rule_based_container3:
                st.header(f"Rule-based สำหรับ {st.session_state['target_rule_based3']}",divider = 'blue')
            
            ## 1. Rule Based
            if st.session_state['rule_based3'] == False:
                st.radio(label = '',options = ['default','customize'],index = 0,key = 'rule_based3_radio',label_visibility= 'collapsed')
                check_box_container3 = st.container()
            ################################################# Rule-based Iisc #################################################
                if bool(re.search('DEFAULT',str(st.session_state['rule_based3_radio']).upper())):
                    st.session_state['isic3_checkbox_bool'] = False
                    st.session_state['keywords3_checkbox_bool'] = False
                    st.session_state['nat3_checkbox_bool'] = True
                else:
                    st.session_state['isic3_checkbox_bool'] = False
                    st.session_state['keywords3_checkbox_bool'] = False
                    st.session_state['nat3_checkbox_bool'] = False

                with check_box_container3:
                    st.divider()
                    st.subheader('Apply')
                    isic3_checkbox = st.checkbox('Rule based : isic',key = 'isic3_checkbox',value =  st.session_state['isic3_checkbox_bool'])
                    keywords3_checkbox = st.checkbox('Rule based : keywords',key = 'keywords3_checkbox',value = st.session_state['keywords3_checkbox_bool'])
                    nat3_checkbox = st.checkbox('Rule based : nationalities',key = 'nat3_checkbox',value = st.session_state['nat3_checkbox_bool'])
                    
                if 'isic_catalog3' not in st.session_state:
                    st.session_state.isic_catalog3 = pd.read_excel("data/app3_demo_info.xlsx",sheet_name= 'isics')

                if 'add_isic_section3' not in st.session_state:
                    st.session_state.add_isic_section3 = False

                def save_submit_isic3(add):
                    fake_df = pd.DataFrame({'target_sna30':[add],'isic4':[None]})
                    st.session_state.isic_catalog3 = pd.concat([st.session_state.isic_catalog3,fake_df])

                isic3_session = []
                
                if bool(re.search('DEFAULT',str(st.session_state['rule_based3_radio']).upper()) and st.session_state['isic3_checkbox']):
                    st.header('I. Isic Adjust',divider= 'orange')
                    # apply on th or all
                    isic_container3 = st.container()
                    isic_left3,isic_right3 = st.columns(2)
                    isic_c3 = 1
                    for sna_10 in st.session_state.isic_catalog3['target_sna10'].unique():
                        with isic_container3:
                            cur_isic3 = st.session_state.isic_catalog3.query("target_sna10 == @sna_10")
                            isic_v3 = cur_isic3['isic4'].values.tolist()
                            if isic_c3 % 3 == 0:
                                with isic_right3:
                                    st.subheader(f":gray[{sna_10}]")
                                    st_tags(label = '',value = isic_v3,key = f'isic3_{sna_10}')
                            else:
                                with isic_left3:
                                    st.subheader(f":gray[{sna_10}]")
                                    st_tags(label = '',value = isic_v3,key = f'isic3_{sna_10}')
                            isic_c3 += 1
                            isic3_session.append(f'isic3_{sna_10}')
                    
                    if st.session_state.add_isic_section3 == False: 
                        with st.container():
                            st.write('เพิ่มประเภท SNA')
                            isic3_left,isic3_right = st.columns([10,30])
                            with isic3_left:
                                add_isic3 = st.text_input(label = '', placeholder= 'พิมพ์ประเภท SNA และกด Add',label_visibility='collapsed',key = 'add_isic3')
                            add_isic_bt3 = st.button(label = 'Add',on_click = save_submit_isic3, args = ([add_isic3]),key = 'add_isic_bt3')

                ################################################# Rule-based Keyword #################################################
                if 'keywords_catalog3' not in st.session_state:
                    st.session_state.keywords_catalog3 = pd.read_excel("data/app3_demo_info.xlsx",sheet_name = 'keywords_en')

                if 'add_keyword_section3' not in st.session_state:
                    st.session_state.add_keyword_section3 = False

                def save_submit_keyword3(add):
                    fake_df = pd.DataFrame({'target_sna10':[add],'word_token':[None]})
                    st.session_state.keywords_catalog3 = pd.concat([st.session_state.keywords_catalog3,fake_df])

                if bool(re.search('DEFAULT',str(st.session_state['rule_based3_radio']).upper())) and st.session_state['keywords3_checkbox']:
                    st.divider()
                    st.header('II. Keywords Adjust',divider = 'orange')
                    keywords_container3 = st.container()
                    keywords_left3,keywords_right3 = st.columns(2)
                    keywords_c3 = 1
                    keywords3_section = []
                    for sna_10 in st.session_state.keywords_catalog3['target_sna10'].unique():
                        cur_keyword3 = st.session_state.keywords_catalog3.query("target_sna10 == @sna_10")
                        keywords_v3 = cur_keyword3['word_token'].values.tolist()
                        with keywords_container3:
                            if keywords_c3 % 2 == 0:
                                with keywords_right3:
                                    st.subheader(f":gray[{sna_10}]")
                                    st_tags(label = '',value = keywords_v3,key = f'keywords3_{sna_10}')
                            else:
                                with keywords_left3:
                                    st.subheader(f":gray[{sna_10}]")
                                    st_tags(label = '',value = keywords_v3,key = f'keywords3_{sna_10}')
                        keywords_c3  += 1
                        keywords3_section.append(f'keywords3_{sna_10}')
                    

                    if st.session_state.add_keyword_section3 == False: 
                        with st.container():
                            st.write('เพิ่มประเภท SNA')
                            keywords3_left,keywords3_right = st.columns([10,20])
                            with keywords3_left:
                                add_keyword3 = st.text_input(label = '', placeholder= 'พิมพ์ประเภท SNA และกด Add',label_visibility='collapsed',key = 'add_keyword3')
                            add_keyword_bt3 = st.button(label = 'Add',on_click = save_submit_keyword3, args = ([add_keyword3]),key = 'add_keyword_bt3')
                    st.divider()
                    ################################################# Rule-based Nationalities #################################################
                    
                    
                if bool(re.search('DEFAULT',str(st.session_state['rule_based3_radio']).upper())) and st.session_state['nat3_checkbox']:
                    st.header('III. Nationalities Rule-based',divider= 'orange')
                    if 'nat_catalog3' not in st.session_state:
                        st.session_state.nat_catalog3 = []
                    
                    rule_based3_nat_v_choices = [None,'ROW','ONFC','HH']
                    rule_based3_left_nat_v,rule_based3_right_nat_v = st.columns([20,10])
                    
                    rule_based3_left_nat_v.subheader(f':blue[กรณีบริษัทเป็นสัญชาติไทย จะมีค่า SNA :]')
                    rule_based3_right_nat_v.selectbox(label = '',options = rule_based3_nat_v_choices,index = 3,key = 'rule_based3_first_nat_v',label_visibility = 'collapsed')
                    rule_based3_left_nat_v.subheader(f':blue[กรณีบริษัทเป็นต่างชาติจะมีค่า SNA :]')
                    rule_based3_right_nat_v.selectbox(label = '',options = rule_based3_nat_v_choices,index = 1,key = 'rule_based3_second_nat_v',label_visibility = 'collapsed')
                    st.divider()


                ### Submit rule-based
                # submit rules
                def submit_rule_based3():
                    ### Collect isic's action
                    if st.session_state['isic3_checkbox']:
                        isics_df = pd.DataFrame()
                        for key in isic3_session:
                            new_dict = dict( target_sna10 = np.array([key]), isic4 = np.array(st.session_state[key]))
                            new_df = pd.DataFrame.from_dict(new_dict, orient='index').transpose()
                            isics_df = pd.concat([isics_df,new_df])
                        isics_df['target_sna10'] = isics_df['target_sna10'].ffill()
                        isics_df['target_sna10'] = isics_df['target_sna10'].str.replace('isic3_','') 
                        st.session_state['rule_based3_isic_action'] = isics_df
                    else:
                        st.session_state['rule_based3_isic_action'] = None

                    if st.session_state['keywords3_checkbox']:
                        ### Collect keywords's action
                        keywords_df = pd.DataFrame()
                        for key in keywords3_section:
                            new_dict = dict( target_sna10 = np.array([key]), word_token = np.array(st.session_state[key]))
                            new_df = pd.DataFrame.from_dict(new_dict, orient='index').transpose()
                            keywords_df = pd.concat([keywords_df,new_df])
                        keywords_df['target_sna10'] = keywords_df['target_sna10'].ffill()
                        keywords_df['target_sna10'] = keywords_df['target_sna10'].str.replace('keywords3_','') 
                        st.session_state['rule_based3_keywords_action'] = keywords_df
                    else:
                        st.session_state['rule_based3_keywords_action'] = None

                    ### Collect Nationalities's action
                    if st.session_state['nat3_checkbox']:
                        st.session_state['rule_based3_nat_else_th'] = st.session_state['rule_based3_first_nat_v']
                        st.session_state['rule_based3_nat_else_nonth'] = st.session_state['rule_based3_second_nat_v']
                    else:
                        st.session_state['rule_based3_nat_else_th'] = None
                        st.session_state['rule_based3_nat_else_nonth'] = None
                    
                    st.session_state['isic3_checkbox_out'] = load_in(st.session_state['isic3_checkbox'])
                    st.session_state['keywords3_checkbox_out'] = load_in(st.session_state['keywords3_checkbox'])
                    st.session_state['nat3_checkbox_out'] = load_in(st.session_state['nat3_checkbox'])
                    
                    # submit rules-based
                    st.session_state['rule_based3'] = True
                    
                # submit button
                if st.session_state['rule_based3'] == False:
                    st.button('submit rule-based 3',key ='submit_rule_based3',on_click = submit_rule_based3)
            
            # after-submit
            else:
                st.write(st.session_state['rule_based3_isic_action'])
                st.write(st.session_state['rule_based3_keywords_action'])
                st.write(st.session_state['rule_based3_nat_else_th'], st.session_state['rule_based3_nat_else_nonth'])
                st.write('Submitted')
    ############################################################## 3.Person ##############################################################


def submit_app3_rule_based():
    st.session_state['app3_rule_based'] = True

st.divider()
mult_cols = st.columns(9)
back_col = mult_cols[0]
next_col = mult_cols[-1]
with next_col:
    if (st.session_state.app3_rule_based == False):
        get_next = st.button('Next',on_click = submit_app3_rule_based )

############################################################## Prioritize SNA ##############################################################
if st.session_state['app3_rule_based'] and st.session_state['app3_rule_based_prioritize'] == False:
    ################################################# Select Necessary Column #################################################
    st.subheader('โปรดเลือกคอลัมน์')
    choices = [None,'SNA','NAT','NAME','ISIC'] # df input_column
    left,right,out = st.columns([10,10,10])
    left.subheader(f':gray[SNA :]')
    right.selectbox(label = '',options = choices,index = 0,key = 'input_sna',label_visibility = 'collapsed')
    left.subheader(f':gray[สัญชาติผู้ถือหุ้น :]')
    right.selectbox(label = '',options = choices,index = 0,key = 'input_nat',label_visibility = 'collapsed')
    left.subheader(f':gray[ชื่อผู้ถือหุ้น :]')
    right.selectbox(label = '',options = choices,index = 0,key = 'input_hldrname',label_visibility = 'collapsed')
    left.subheader(f':gray[รหัส isic4 :]')
    right.selectbox(label = '',options = choices,index = 0,key = 'input_isic',label_visibility = 'collapsed')
    st.divider()



    st.subheader('โปรดเลือกลำดับการให้ SNA แก่ผู้ถือหุ้น')
    choices = [None,'สัญชาติ','isic','keyword','matched_sna']
    first_container = st.container()
    st.radio(label = '',label_visibility = 'collapsed',options = ['default','customize'],index = 0,key = 'apply_radio')
    if st.session_state['apply_radio'] == 'default':
        st.session_state['global_prioritize_option_rank1_default'] = 2
        st.session_state['global_prioritize_option_rank2_default'] = 3
        st.session_state['global_prioritize_option_rank3_default'] = 4
        st.session_state['global_prioritize_option_rank4_default'] = 1
    else:
        st.session_state['global_prioritize_option_rank1_default'] = 0
        st.session_state['global_prioritize_option_rank2_default'] = 0
        st.session_state['global_prioritize_option_rank3_default'] = 0
        st.session_state['global_prioritize_option_rank4_default'] = 0

    def findout(selectbox_option,desired_key):
        if selectbox_option is not None:
            st.session_state[f'{desired_key}'] = {}
            if bool(re.search('NAT|สัญชาติ',selectbox_option.upper())):
                options = ['Apply เฉพาะสัญชาติไทย','Apply เฉพาะสัญชาติไทย และต้องมีรหัส Isic']
                st.radio(label = '',label_visibility= 'collapsed',options=options,key = f'{desired_key}_condition',horizontal=True)
                st.session_state[f'{desired_key}']['type'] = 'nat'
                st.session_state[f'{desired_key}']['option'] = options
            elif bool(re.search('ISIC|ไอซิก',selectbox_option.upper())):
                options = ['Apply เฉพาะสัญชาติไทย','Apply กับทุกสัญชาติ']
                st.radio(label = '',label_visibility= 'collapsed',options=options,key = f'{desired_key}_condition',horizontal=True)
                st.session_state[f'{desired_key}']['type'] = 'isic'
                st.session_state[f'{desired_key}']['option'] = options
            elif bool(re.search('KEYWORD|คียเว',selectbox_option.upper())):
                options = ['Apply เฉพาะสัญชาติไทย','Apply กับทุกสัญชาติ']
                st.radio(label = '',label_visibility= 'collapsed',options=options,key = f'{desired_key}_condition',horizontal=True)
                st.session_state[f'{desired_key}']['type'] = 'keywords'
                st.session_state[f'{desired_key}']['option'] = options
            elif bool(re.search('MATCHED|SNA',selectbox_option.upper())):
                options = ['Apply เฉพาะสัญชาติไทย','Apply กับทุกสัญชาติ']
                st.radio(label = '',label_visibility= 'collapsed',options=options,key = f'{desired_key}_condition',horizontal=True)
                st.session_state[f'{desired_key}']['type'] = 'matchedsna'
                st.session_state[f'{desired_key}']['option'] = options

    with first_container:
        left1,right1,out1 = st.columns([10,10,10])
        left2,right2,out2 = st.columns([10,10,10])
        left3,right3,out3 = st.columns([10,10,10])
        left4,right4,out4 = st.columns([10,10,10])

        right1.selectbox(label = '',options = choices,index = st.session_state['global_prioritize_option_rank1_default'],
                        key = 'global_prioritize_option_rank1',label_visibility = 'collapsed')
        left1.subheader(f':gray[1.{st.session_state["global_prioritize_option_rank1"]} :]')
        with out1:
            findout(st.session_state['global_prioritize_option_rank1'],desired_key = 'rank1')

        right2.selectbox(label = '',options = choices,index = st.session_state['global_prioritize_option_rank2_default'],
                        key = 'global_prioritize_option_rank2',label_visibility = 'collapsed')
        left2.subheader(f':gray[2.{st.session_state["global_prioritize_option_rank2"]} :]')
        with out2:
            findout(st.session_state['global_prioritize_option_rank2'],desired_key = 'rank2')
        
        right3.selectbox(label = '',options = choices,index = st.session_state['global_prioritize_option_rank3_default'],
                        key = 'global_prioritize_option_rank3',label_visibility = 'collapsed')
        left3.subheader(f':gray[3.{st.session_state["global_prioritize_option_rank3"]} :]')
        with out3:
            findout(st.session_state['global_prioritize_option_rank3'],desired_key = 'rank3')

        right4.selectbox(label = '',options = choices,index = st.session_state['global_prioritize_option_rank4_default'],
                        key = 'global_prioritize_option_rank4',label_visibility = 'collapsed')
        left4.subheader(f':gray[4.{st.session_state["global_prioritize_option_rank4"]} :]')
        with out4:
            findout(st.session_state['global_prioritize_option_rank4'],desired_key = 'rank4')
        st.divider()

    def submit_prioritize():
        # input column (draft)
        st.session_state['global_input_f'] = {}
        st.session_state['global_input_f']['nat'] = st.session_state['input_nat']
        st.session_state['global_input_f']['isic4'] = st.session_state['input_isic']
        st.session_state['global_input_f']['hldr_name'] = st.session_state['input_hldrname']
        st.session_state['global_input_f']['sna'] = st.session_state['input_sna']
        st.session_state['global_input_f']['sna_action'] = None

        # ranking
        st.session_state['rank1']['condition'] = st.session_state['rank1_condition'] # get value from findout function
        st.session_state['rank2']['condition'] = st.session_state['rank2_condition']
        st.session_state['rank3']['condition'] = st.session_state['rank3_condition']
        st.session_state['rank4']['condition'] = st.session_state['rank4_condition']
        for rank in range(1,5):
            st.session_state[f'rank{rank}']['rank'] = rank
        
        st.session_state['app3_rule_based_prioritize'] = True

    next_bt = st.button('next',on_click= submit_prioritize)

from utils.app3 import *

if st.session_state['app3_rule_based_prioritize']:
    st.write(st.session_state['global_input_f'])
    # draft
    st.session_state['global_input'] = {}
    st.session_state['global_input']['nat'] = 'NAT_CODE'
    st.session_state['global_input']['isic4'] = 'isic4'
    st.session_state['global_input']['hldr_name'] = 'holder_name'
    st.session_state['global_input']['sna'] = 'SNA'
    #st.session_state['global_input']['sna_action'] = None
    st.session_state['global_input']['sna_action'] = pd.read_csv('data/action_matchedsna.csv')

    def check_target_allowance(type_,target_):
        if type_ == "isic":
            allowance = st.session_state[f'isic{target_}_checkbox_out']
        elif type_ == "keywords":
            allowance = st.session_state[f'keywords{target_}_checkbox_out']
        elif type_ == 'matchedsna':
            allowance = True
        elif type_ == 'nat':
            allowance = st.session_state[f'nat{target_}_checkbox_out']
        return allowance

    def find_input(type_,dummy_sna = 'TEMP_SNA'):
        if type_ == "isic":
            input_ = [dummy_sna,st.session_state['global_input']['nat'],st.session_state['global_input']['isic4']]
        elif type_ == "keywords":
            input_ = [dummy_sna,st.session_state['global_input']['nat'],st.session_state['global_input']['hldr_name']]
        elif type_ == 'matchedsna':
            input_ = [dummy_sna,st.session_state['global_input']['nat'],st.session_state['global_input']['sna']]
        elif type_ == 'nat':
            input_ = [dummy_sna,st.session_state['global_input']['nat'],st.session_state['global_input']['isic4']]
        return input_

    def find_func(type_,target_class):
        if type_ == "isic":
            func_ = assign_byIsic
        elif type_ == "keywords":
            func_ = assign_byKeywords
        elif type_ == 'matchedsna':
            func_ = assign_byMatchedSNA
        elif type_ == 'nat':
            if bool(re.search('PERSON|ORD',target_class.upper())):
                func_ = assign_byNationalitiesOrd
            else:
                func_ = assign_byNationalities
        return func_

    def find_action(type_,target_):
        if type_ == "isic":
            action = st.session_state[f'rule_based{target_}_isic_action']
        elif type_ == "keywords":
            action = st.session_state[f'rule_based{target_}_keywords_action']
        elif type_ == 'matchedsna':
            action = st.session_state['global_input']['sna_action']
        elif type_ == 'nat':
            action = None
        # check action
        if action is not None:
            cn = action.columns.values
            if action[cn[0]].value_counts().max() > 1:
                action = action.groupby(cn[0])[cn[1]].apply('|'.join).reset_index()
        return action

    def find_condition(type_,option_,condition_):
        idx = np.where(np.isin(option_,condition_))[0][0]
        if type_ == "isic":
            if idx == 0:
                condition = True
            else:
                condition = False
        elif type_ == "keywords":
            if idx == 0:
                condition = True
            else:
                condition = False
        elif type_ == 'matchedsna':
            if idx == 0:
                condition = True
            else:
                condition = False
        elif type_ == 'nat':
            if idx == 0:
                condition = 1
            else:
                condition = 2
        return condition

    
    for target in range(1,4):
        st.session_state[f'assign_sna_target{target}]'] = {}
        if target == 1:
            st.session_state[f'assign_sna_target{target}]']['Class'] = 'firm_th'
        elif target == 2:
            st.session_state[f'assign_sna_target{target}]']['Class'] = 'firm_eng'
        elif target == 3:
            st.session_state[f'assign_sna_target{target}]']['Class'] = 'person'

        st.session_state[f'apply_order{target}_rank1'] = {}
        st.session_state[f'apply_order{target}_rank2'] = {}
        st.session_state[f'apply_order{target}_rank3'] = {}
        st.session_state[f'apply_order{target}_rank4'] = {}

        st.subheader(f'Our Condition : {target}')
        for rank in range(1,5):
            if check_target_allowance(type_ = st.session_state[f'rank{rank}']['type'],target_=target):
                st.session_state[f'apply_order{target}_rank{rank}']['function'] = find_func(st.session_state[f'rank{rank}']['type'],st.session_state[f'assign_sna_target{target}]']['Class'])
                st.session_state[f'apply_order{target}_rank{rank}']['input_column'] = find_input(st.session_state[f'rank{rank}']['type'])
                st.session_state[f'apply_order{target}_rank{rank}']['action'] = find_action(st.session_state[f'rank{rank}']['type'],target)
                st.session_state[f'apply_order{target}_rank{rank}']['condition'] = find_condition(type_ = st.session_state[f'rank{rank}']['type'],
                                                                                            option_= st.session_state[f'rank{rank}']['option'],
                                                                                            condition_= st.session_state[f'rank{rank}']['condition']) 
        st.write(st.session_state[f'apply_order{target}_rank1'])
        st.write(st.session_state[f'apply_order{target}_rank2'])
        st.write(st.session_state[f'apply_order{target}_rank3'])
        st.write(st.session_state[f'apply_order{target}_rank4'])

if 'start_prep' not in st.session_state:
    st.session_state['start_prep'] = False

if 'data' not in st.session_state:
    st.session_state['data'] = None #pd.read_excel('data/fake_data.xlsx',engine = 'openpyxl')
    st.session_state['upload_data'] = False

def get_upload():
    st.session_state['upload_data'] = True

@st.cache_data
def read_upload_data(df):
    section = st.empty()
    section.info('reading uploaded data')
    try:
        out = pd.read_csv(df,skiprows = none_but_please_show_progress_bar())
    except UnicodeDecodeError:
        out = pd.read_excel(df,skiprows = none_but_please_show_progress_bar(),engine = 'openpyxl')
    section.empty()
    return out

def none_but_please_show_progress_bar(*args, **kwargs):
    bar = stqdm(*args, **kwargs)
    def checker(x):
        bar.update(1)
        return False
    return checker

def conditional_st_write_df(df):
    file_size = df.memory_usage().sum()
    file_size_simp = file_size / 1000000
    if file_size_simp > 200:
        divider = file_size_simp/200
        sample_size = int(np.round(len(df)/divider))
        portion_of = np.round(sample_size/len(df) * 100)
        st.write(f'File Size is too large so we sample {portion_of}% of total')
        st.dataframe(df.sample(sample_size),use_container_width = True)
    else:
        st.dataframe(df,use_container_width = True)
        
if st.session_state['app3_rule_based_prioritize'] :
    st.button('upload ja',key = 'upload_data_bt',on_click = get_upload)
    if st.session_state['upload_data']:
        st.header("กรุณาอัพโหลด Dataset เพื่อเริ่ม (.csv)")
        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file is not None:
            dataframe = read_upload_data(uploaded_file)
            conditional_st_write_df(dataframe)
            st.write(f'{dataframe.shape[0]} rows , {dataframe.shape[1]} columns')
            st.session_state['data'] = load_in(dataframe)

    def go_start_prep():
        st.session_state['start_prep'] = True

    st.button('go ja',key = 'go_start_prep',on_click = go_start_prep)

if st.session_state['app3_rule_based_prioritize'] and st.session_state['start_prep']:
    st.info('loading')
    
    st.session_state['data']['TEMP_SNA'] = np.nan
    # 1.firm-th 2.firm_eng 3. person
    total_df = pd.DataFrame()
    for target in range(1,3+1):
        st.write(target)
        filtered_df =  st.session_state['data'][st.session_state['data']['Class'].str.contains(st.session_state[f'assign_sna_target{target}]']['Class'])]
        st.write(filtered_df)
        for rank in range(1,4+1):
            st.write(st.session_state[f'apply_order{target}_rank{rank}'])
            if len(st.session_state[f'apply_order{target}_rank{rank}']) > 0:
                filtered_df['TEMP_SNA'] = filtered_df.progress_apply(lambda row: \
                                        st.session_state[f'apply_order{target}_rank{rank}']['function'](row,
                                                                                                        st.session_state[f'apply_order{target}_rank{rank}']['input_column'],
                                                                                                        st.session_state[f'apply_order{target}_rank{rank}']['action'],
                                                                                                        condition =  st.session_state[f'apply_order{target}_rank{rank}']['condition']),
                                                                                                        axis = 1)
        
        total_df = pd.concat([total_df,filtered_df])
    st.write(total_df)

# สิ่งที่ต้องทำต่อไป
# 3. ทำ column global input ให้มันเลือกมาจาก dataframe

