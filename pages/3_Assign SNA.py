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
import time
from PIL import Image
#################################################################### App 3 Session ######################################################################
if 'isic_df_left' not in st.session_state:
    st.session_state['isic_df_left'] = pd.read_excel('data/isic_case.xlsx',sheet_name= 'left')
    st.session_state['isic_df_right'] = pd.read_excel('data/isic_case.xlsx',sheet_name= 'right')

if 'keywords_df_left' not in st.session_state:
    st.session_state['keywords_df_left'] = pd.read_excel('data/keywords.xlsx',sheet_name= 'left')
    st.session_state['keywords_df_right'] = pd.read_excel('data/keywords.xlsx',sheet_name= 'right')

if 'nat_df_left' not in st.session_state:
    st.session_state['nat_df_left'] = pd.read_excel('data/nat.xlsx',sheet_name= 'left')
    st.session_state['nat_df_right'] = pd.read_excel('data/nat.xlsx',sheet_name= 'right')

if 'matchedsna_df_left' not in st.session_state:
    st.session_state['matchedsna_df_left'] = pd.read_excel('data/matched_sna.xlsx',sheet_name= 'left')
    st.session_state['matchedsna_df_right'] = pd.read_excel('data/matched_sna.xlsx',sheet_name= 'right')

st.title('App 3. Assign SNA ให้กับผู้ถือหุ้น')
st.write("ซึ่งการจะหา SNA ให้กับผู้ถือหุ้นสามารถทำได้หลายวิธี อาทิ")
st.write("เชื่อมโยงกับถังข้อมูลที่มี SNA อยู่แล้ว (เช่นถัง IPI) ผ่านการทำ :red[Name Matching]")
st.write('หรือใช้ข้อมูล :green["Field" ที่มีความสามารถในการคัดแยก SNA] และกำหนดออกมาเป็น :orange[Rule Based] เช่น')
st.code('1. "รหัส Isic4" เช่น รหัส "ขึ้นต้นด้วย K" มีโอกาสสูงที่ผู้ถือหุ้นจะเป็น -> ตัวกลางทางการเงิน OFC\
        \n2. "คีย์เวิร์ด" ที่ระบุชัดเจนว่าเป็น Sector ไหน เช่น คำว่า "ธนาคาร" มีโอกาสที่จะเป็น -> OFC\
        \n3. "สัญชาติของผู้ถือหุ้น" เช่น หากเป็นผู้ถือหุ้น "ต่างชาติ" ก็มีโอกาสที่จะเป็น -> ROW')

st.subheader('การทำงานของ App 3. Assign SNA จะมีอยู่ 2 ขั้นตอนคือ')
st.write("***:orange[1.กำหนด Rule Based]***")
st.code('"Rule Based" จะเป็นการใช้ประโยชน์จาก "Field" เข้ามาคัดแยก SNA โดยกำหนดรูปแบบตามที่เรากำหนด \nโดยจะแยกการ Apply ตามประเภทของผู้ถือหุ้น 1."Firm TH", 2."Firm ENG", 3."Person"  \nรายละเอียดของแต่ละ Rule สามารถดูได้ด้านล่าง')
img = Image.open('material/images/arrow1.png')
with st.expander('คำอธิบายเพิ่มเติมเกี่ยวกับการกำหนด Rule Based'):
    st.write(':grey[Class จะมีทั้งหมด 3 Class ซึ่งแต่ละ Class จะมี Rule Based ของตัวเองไม่ซ้ำกัน]')
    st.write("1.:blue[Firm TH]  >>  หมายถึง ชื่อผู้ถือหุ้นที่เป็นธุรกิจที่มีชื่อ:blue[ภาษาไทย]")
    st.write("2.:orange[Firm ENG]  >>  หมายถึง ชื่อผู้ถือหุ้นที่เป็นธุรกิจที่มีชื่อ:orange[ภาษาอังกฤษ]")
    st.write("3.:green[Person]  >>  หมายถึง ชื่อผู้ถือหุ้นที่เป็น:green[บุคคลธรรมดา] ที่มีชื่อภาษาไทย หรือ ภาษาอังกฤษ")
    st.divider()
    st.subheader('Rule Based จะมีทั้งหมด 4 ประเภท')
    st.write('***:red[1. Rule Based : Isic]***')
    st.write(':red[*ปกติ Isic จะไม่มีในข้อมูลผู้ถือหุ้นฉะนั้น Field Isic4 ที่เราใช้ คือ Isic4 ได้มาจากการ Name Matching]')
    st.code("#ISIC4 CODE\nBOT = ['K6411'] \nOFC = ['K649250','K651100','K']")
    isic_col1,isic_col2,isic_col3 = st.columns([14,8,20])
    isic_col1.write(st.session_state['isic_df_left'])
    isic_col2.image(img)
    isic_col3.write(st.session_state['isic_df_right'])
    st.write('***:red[2. Rule Based : Keywords]***')
    st.code("#Keywords\nOFC = ['ทรัสต์','ประกันภัย','กองทุน'] \nODC = ['สหกรณ์ออมทรัพย์','ธนาคาร'] \nPNFC = ['องค์การสะพานปลา','องค์การสวนยาง']")
    kw_col1,kw_col2,kw_col3 = st.columns([14,8,20])
    kw_col1.write(st.session_state['keywords_df_left'])
    kw_col2.image(img)
    kw_col3.write(st.session_state['keywords_df_right'])
    st.write('***:red[3. Rule Based : Nationalities]***')
    st.code('#Nationalities \nif nationality == "TH":\n   return "ONFC" \nelse: \n   return "ROW"')
    nat_col1,nat_col2,nat_col3 = st.columns([14,8,20])
    nat_col1.write(st.session_state['nat_df_left'])
    nat_col2.image(img)
    nat_col3.write(st.session_state['nat_df_right'])
    st.write('***:red[4. Rule Based : Matched SNA]***')
    st.write('จะเป็นการใช้ค่า SNA จากที่ Name Matching มาจากได้จาก Process ก่อนหน้า')
    msna_col1,msna_col2,msna_col3 = st.columns([22,6,16])
    msna_col1.dataframe(st.session_state['matchedsna_df_left'],hide_index= True,use_container_width= True)
    msna_col2.image(img)
    msna_col3.dataframe(st.session_state['matchedsna_df_right'],hide_index= True,use_container_width=True)

st.write("***:orange[2.กำหนดลำดับของการ Apply Rule Based]***")
st.code('ใช้กำหนดลำดับความสำคัญของ "Rule Based" ว่าจะ Apply Rule ไหนก่อน')
st.divider()

if 'app3_rule_based' not in st.session_state:
    st.session_state['app3_input'] = False
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

def get_upload():
    st.session_state['upload_data'] = True

@st.cache_data
def load_in(input_):
    output = input_
    return output

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

if 'data' not in st.session_state:
    st.session_state['data'] = None
    st.session_state['upload_data'] = False

if 'app2_ExportOutput' not in st.session_state:
    st.session_state['app2_ExportOutput'] = None

def submit_app3_input():
    st.session_state['app3_input'] = True

if st.session_state['app3_input'] == False :
    first_container = st.container()
    ### check app2 input
    if st.session_state['app2_ExportOutput'] is not None:
        check_box = st.checkbox('Use App2 Input')
        if check_box:
            st.session_state['data'] = load_in(st.session_state['app2_ExportOutput'])
            conditional_st_write_df(st.session_state['data'])
            st.write(f"{st.session_state['data'].shape[0]} rows , {st.session_state['data'].shape[1]} columns")
    else:
        check_box = False
    if check_box == False:
        first_container.header("กรุณาอัพโหลด Dataset เพื่อเริ่ม (.csv)")
        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file is not None:
            dataframe = read_upload_data(uploaded_file)
            conditional_st_write_df(dataframe)
            st.write(f'{dataframe.shape[0]} rows , {dataframe.shape[1]} columns')
            st.session_state['data'] = load_in(dataframe)

    if st.session_state['data'] is not None:
        st.button('Submit',on_click = submit_app3_input ,key = 'submit_app3_input')

if st.session_state['app3_rule_based'] == False and st.session_state['app3_input']:
    st.header('1. กำหนด Rule Based',divider = 'blue')

############################################################## 1.FIRM_TH ##############################################################
if st.session_state['app3_rule_based'] == False and st.session_state['app3_input']:
    style = (8,2,2,2)
    fake_col,col_page1,col_page2,col_page3 = st.columns(style)

    # def render_page1():
    #     st.session_state['page1'] = True
    #     st.session_state['page2'] = False
    #     st.session_state['page3'] = False

    # def render_page2():
    #     st.session_state['page1'] = False
    #     st.session_state['page2'] = True
    #     st.session_state['page3'] = False

    # def render_page3():
    #     st.session_state['page1'] = False
    #     st.session_state['page2'] = False
    #     st.session_state['page3'] = True   
    # with fake_col:
    #     st.write('Rule Based ของแต่ละประเภท')
    # with col_page1:
    #     st.button('TH',on_click = render_page1,key = 'read1')
    # with col_page2:
    #     st.button('ENG',on_click= render_page2,key = 'read2')
    # with col_page3:
    #     st.button('Person',on_click= render_page3,key = 'read3')

    if st.session_state['page1']:
        rule_based_container1 = st.container()
        #target_rule_based1 =  st.selectbox(label = '',options = ['Firm-TH','Firm-ENG','Person'],index = 0,key = 'target_rule_based1',label_visibility= 'collapsed')
        if 'target_rule_based1' not in st.session_state:
            st.session_state['target_rule_based1'] = 'Firm-TH'
        if bool(re.search('TH',str(st.session_state['target_rule_based1']).upper())):
            with rule_based_container1:
                st.header(f"Rule-based สำหรับ :blue[{st.session_state['target_rule_based1']}]",divider = 'blue')
            
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
                    
                    rule_based1_left_nat_v.subheader(f':grey[กรณีบริษัทเป็นสัญชาติไทย จะมีค่า SNA :]')
                    rule_based1_right_nat_v.selectbox(label = '',options = rule_based1_nat_v_choices,index = 2,key = 'rule_based1_first_nat_v',label_visibility = 'collapsed')
                    rule_based1_left_nat_v.subheader(f':grey[กรณีบริษัทเป็นต่างชาติจะมีค่า SNA :]')
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
                    st.session_state['target_rule_based1_out'] = load_in(st.session_state['target_rule_based1'])
                    st.session_state['page2'] = True
                    st.session_state['page1'] = False
                    
                    
                # submit button
                if st.session_state['rule_based1'] == False:
                    st.button('submit rule-based 1',key ='submit_rule_based1',on_click = submit_rule_based1)
            
            # # after-submit
            # else:
            #     if st.session_state['rule_based1_isic_action'] is not None:
            #         st.write('Isic Rule Based:')
            #         st.write(st.session_state['rule_based1_isic_action'])
            #     if st.session_state['rule_based1_keywords_action'] is not None:
            #         st.write('Keywords Rule Based:')
            #         st.write(st.session_state['rule_based1_keywords_action'])
            #     st.write('Nationality Rule Based:',st.session_state['rule_based1_nat_else_th'], st.session_state['rule_based1_nat_else_nonth'])
            #     st.write('Submitted')
    if st.session_state['rule_based1']:
        st.header(f"Rule-based สำหรับ :blue[{st.session_state['target_rule_based1_out']}]",divider = 'blue')
        if st.session_state['rule_based1_isic_action'] is not None:
            st.write('Isic Rule Based:')
            st.write(st.session_state['rule_based1_isic_action'])
        if st.session_state['rule_based1_keywords_action'] is not None:
            st.write('Keywords Rule Based:')
            st.write(st.session_state['rule_based1_keywords_action'])
        st.write('Nationality Rule Based:',st.session_state['rule_based1_nat_else_th'], st.session_state['rule_based1_nat_else_nonth'])
        st.write('Submitted')

    ############################################################## 1.FIRM_TH ##############################################################


   ############################################################## 2.FIRM_EN ##############################################################
    if st.session_state['page2']:
        rule_based_container2 = st.container()
        #target_rule_based2 =  st.selectbox(label = '',options = ['Firm-TH','Firm-ENG','Person'],index = 1,key = 'target_rule_based2',label_visibility= 'collapsed')
        if 'target_rule_based2' not in st.session_state:
            st.session_state['target_rule_based2'] = 'Firm-ENG'
        if bool(re.search('EN',str(st.session_state['target_rule_based2']).upper())):
            with rule_based_container2:
                st.header(f"Rule-based สำหรับ :orange[{st.session_state['target_rule_based2']}]",divider = 'orange')
            
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
                    
                    rule_based2_left_nat_v.subheader(f':grey[กรณีบริษัทเป็นสัญชาติไทย จะมีค่า SNA :]')
                    rule_based2_right_nat_v.selectbox(label = '',options = rule_based2_nat_v_choices,index = 2,key = 'rule_based2_first_nat_v',label_visibility = 'collapsed')
                    rule_based2_left_nat_v.subheader(f':grey[กรณีบริษัทเป็นต่างชาติจะมีค่า SNA :]')
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
                    st.session_state['target_rule_based2_out'] = load_in(st.session_state['target_rule_based2'])
                    st.session_state['page2'] = False
                    st.session_state['page3'] = True
                    
                    # submit rules-based
                    st.session_state['rule_based2'] = True
                    
                # submit button
                if st.session_state['rule_based2'] == False:
                    st.button('submit rule-based 2',key ='submit_rule_based2',on_click = submit_rule_based2)
            
            # # after-submit
            # else:
            #     if st.session_state['rule_based2_isic_action'] is not None:
            #         st.write('Isic Rule Based:')
            #         st.write(st.session_state['rule_based2_isic_action'])
            #     if st.session_state['rule_based2_keywords_action'] is not None:
            #         st.write('Keywords Rule Based:')
            #         st.write(st.session_state['rule_based2_keywords_action'])
            #     st.write('Nationality Rule Based:',st.session_state['rule_based2_nat_else_th'], st.session_state['rule_based2_nat_else_nonth'])
            #     st.write('Submitted')
    if st.session_state['rule_based2']:
        st.header(f"Rule-based สำหรับ :orange[{st.session_state['target_rule_based2_out']}]",divider = 'blue')
        if st.session_state['rule_based2_isic_action'] is not None:
            st.write('Isic Rule Based:')
            st.write(st.session_state['rule_based2_isic_action'])
        if st.session_state['rule_based2_keywords_action'] is not None:
            st.write('Keywords Rule Based:')
            st.write(st.session_state['rule_based2_keywords_action'])
        st.write('Nationality Rule Based:',st.session_state['rule_based2_nat_else_th'], st.session_state['rule_based2_nat_else_nonth'])
        st.write('Submitted')                    
    ############################################################## 2.FIRM_EN ##############################################################

    ############################################################## 3.Person ##############################################################
    if st.session_state['page3']:
        rule_based_container3 = st.container()
        
        #target_rule_based3 =  st.selectbox(label = '',options = ['Firm-TH','Firm-ENG','Person'],index = 2,key = 'target_rule_based3',label_visibility= 'collapsed')
        if 'target_rule_based3' not in st.session_state:
            st.session_state['target_rule_based3'] = 'Person'

        if bool(re.search('PER',str(st.session_state['target_rule_based3']).upper())):
            with rule_based_container3:
                st.header(f"Rule-based สำหรับ :green[{st.session_state['target_rule_based3']}]",divider = 'green')
            
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
                    st.header('I. Isic Adjust',divider= 'green')
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
                    st.header('II. Keywords Adjust',divider = 'green')
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
                    st.header('III. Nationalities Rule-based',divider= 'green')
                    if 'nat_catalog3' not in st.session_state:
                        st.session_state.nat_catalog3 = []
                    
                    rule_based3_nat_v_choices = [None,'ROW','ONFC','HH']
                    rule_based3_left_nat_v,rule_based3_right_nat_v = st.columns([20,10])
                    
                    rule_based3_left_nat_v.subheader(f':grey[กรณีบริษัทเป็นสัญชาติไทย จะมีค่า SNA :]')
                    rule_based3_right_nat_v.selectbox(label = '',options = rule_based3_nat_v_choices,index = 3,key = 'rule_based3_first_nat_v',label_visibility = 'collapsed')
                    rule_based3_left_nat_v.subheader(f':grey[กรณีบริษัทเป็นต่างชาติจะมีค่า SNA :]')
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
                    st.session_state['target_rule_based3_out'] = load_in(st.session_state['target_rule_based3'])
                    #st.session_state['page2'] = True
                    st.session_state['page3'] = False
                    # submit rules-based
                    st.session_state['rule_based3'] = True
                    
                # submit button
                if st.session_state['rule_based3'] == False:
                    st.button('submit rule-based 3',key ='submit_rule_based3',on_click = submit_rule_based3)
            
            # after-submit
            # else:
            #     if st.session_state['rule_based3_isic_action'] is not None:
            #         st.write('Isic Rule Based:')
            #         st.write(st.session_state['rule_based3_isic_action'])
            #     if st.session_state['rule_based3_keywords_action'] is not None:
            #         st.write('Keywords Rule Based:')
            #         st.write(st.session_state['rule_based3_keywords_action'])
            #     st.write('Nationality Rule Based:',st.session_state['rule_based3_nat_else_th'], st.session_state['rule_based3_nat_else_nonth'])
            #     st.write('Submitted')
    if st.session_state['rule_based3']:
        st.header(f"Rule-based สำหรับ :green[{st.session_state['target_rule_based3_out']}]",divider = 'blue')
        if st.session_state['rule_based3_isic_action'] is not None:
            st.write('Isic Rule Based:')
            st.write(st.session_state['rule_based3_isic_action'])
        if st.session_state['rule_based3_keywords_action'] is not None:
            st.write('Keywords Rule Based:')
            st.write(st.session_state['rule_based3_keywords_action'])
        st.write('Nationality Rule Based:',st.session_state['rule_based3_nat_else_th'], st.session_state['rule_based3_nat_else_nonth'])
        st.write('Submitted')                    
    ############################################################## 3.Person ##############################################################

    def submit_app3_rule_based():
        st.session_state['app3_rule_based'] = True
    
    def back_click1():
        st.session_state['app3_input'] = False

    st.divider()
    mult_cols = st.columns(9)
    back_col = mult_cols[0]
    next_col = mult_cols[-1]
    with next_col:
        if (st.session_state.app3_rule_based == False) and st.session_state['rule_based1'] and st.session_state['rule_based2'] and st.session_state['rule_based3']:
            get_next = st.button('Next',on_click = submit_app3_rule_based )
    with back_col:
        back_bt1 = st.button('Back',on_click= back_click1)

############################################################## Prioritize SNA ##############################################################
if st.session_state['app3_rule_based'] and st.session_state['app3_rule_based_prioritize'] == False:
    ################################################# Select Necessary Column #################################################
    st.header('2. กำหนดลำดับการ Apply Rule Based',divider = 'blue')
    
    st.subheader('โปรดเลือกลำดับการให้ SNA แก่ผู้ถือหุ้น')
    choices = [None,'สัญชาติผู้ถือหุ้น','Isic','Keywords','Matched SNA']
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
        left1,right1,out1 = st.columns([11,7,10])
        left2,right2,out2 = st.columns([11,7,10])
        left3,right3,out3 = st.columns([11,7,10])
        left4,right4,out4 = st.columns([11,7,10])

        right1.selectbox(label = '',options = choices,index = st.session_state['global_prioritize_option_rank1_default'],
                        key = 'global_prioritize_option_rank1',label_visibility = 'collapsed')
        left1.subheader(f':gray[1.Rule: {st.session_state["global_prioritize_option_rank1"]}]')
        with out1:
            findout(st.session_state['global_prioritize_option_rank1'],desired_key = 'rank1')

        right2.selectbox(label = '',options = choices,index = st.session_state['global_prioritize_option_rank2_default'],
                        key = 'global_prioritize_option_rank2',label_visibility = 'collapsed')
        left2.subheader(f':gray[2.Rule: {st.session_state["global_prioritize_option_rank2"]}]')
        with out2:
            findout(st.session_state['global_prioritize_option_rank2'],desired_key = 'rank2')
        
        right3.selectbox(label = '',options = choices,index = st.session_state['global_prioritize_option_rank3_default'],
                        key = 'global_prioritize_option_rank3',label_visibility = 'collapsed')
        left3.subheader(f':gray[3.Rule: {st.session_state["global_prioritize_option_rank3"]}]')
        with out3:
            findout(st.session_state['global_prioritize_option_rank3'],desired_key = 'rank3')

        right4.selectbox(label = '',options = choices,index = st.session_state['global_prioritize_option_rank4_default'],
                        key = 'global_prioritize_option_rank4',label_visibility = 'collapsed')
        left4.subheader(f':gray[4.Rule: {st.session_state["global_prioritize_option_rank4"]}]')
        with out4:
            findout(st.session_state['global_prioritize_option_rank4'],desired_key = 'rank4')
    st.divider()

    # Select Necessary Columns
    st.subheader('โปรดเลือกคอลัมน์')
    choices = [None]
    choices.extend(st.session_state['data'].columns.values)
    #choices = [None,'SNA','NAT','NAME','ISIC'] # df input_column

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

    def submit_prioritize():
        # input column (draft)
        st.session_state['global_input'] = {}
        st.session_state['global_input']['nat'] = st.session_state['input_nat']
        st.session_state['global_input']['isic4'] = st.session_state['input_isic']
        st.session_state['global_input']['hldr_name'] = st.session_state['input_hldrname']
        st.session_state['global_input']['sna'] = st.session_state['input_sna']
        st.session_state['global_input']['sna_action'] = pd.read_csv('data/action_matchedsna.csv')
        
        # ranking
        st.session_state['rank1']['condition'] = st.session_state['rank1_condition'] # get value from findout function
        st.session_state['rank2']['condition'] = st.session_state['rank2_condition']
        st.session_state['rank3']['condition'] = st.session_state['rank3_condition']
        st.session_state['rank4']['condition'] = st.session_state['rank4_condition']
        for rank in range(1,5):
            st.session_state[f'rank{rank}']['rank'] = rank
        
        st.session_state['app3_rule_based_prioritize'] = True

    def back_click2():
        st.session_state['rule_based1'] = False
        st.session_state['rule_based2'] = False
        st.session_state['rule_based3'] = False
        st.session_state['app3_rule_based'] = False

    l2,r2 = st.columns([10,1])
    with r2:
        next_bt2 = st.button('Next',on_click= submit_prioritize)
    with l2:
        back_bt2 = st.button('Back',on_click=back_click2)

############################################################## Assign SNA ##############################################################
from utils.app3 import *
if st.session_state['app3_rule_based_prioritize']:

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

    def find_input(type_,dummy_sna = 'FINAL_SNA'):
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

        for rank in range(1,5):
            if check_target_allowance(type_ = st.session_state[f'rank{rank}']['type'],target_=target):
                st.session_state[f'apply_order{target}_rank{rank}']['function'] = find_func(st.session_state[f'rank{rank}']['type'],st.session_state[f'assign_sna_target{target}]']['Class'])
                st.session_state[f'apply_order{target}_rank{rank}']['input_column'] = find_input(st.session_state[f'rank{rank}']['type'])
                st.session_state[f'apply_order{target}_rank{rank}']['action'] = find_action(st.session_state[f'rank{rank}']['type'],target)
                st.session_state[f'apply_order{target}_rank{rank}']['condition'] = find_condition(type_ = st.session_state[f'rank{rank}']['type'],
                                                                                            option_= st.session_state[f'rank{rank}']['option'],
                                                                                            condition_= st.session_state[f'rank{rank}']['condition']) 

if 'app3_rule_based_process' not in st.session_state:
    st.session_state['app3_rule_based_process'] = True
    st.session_state['app3_finalize_output'] = None

# Process Assign SNA to Dataset
if st.session_state['app3_rule_based_prioritize'] and st.session_state['app3_rule_based_process']:
    st.header('3. Final Results',divider= 'green')
    time.sleep(0.5)
    if st.session_state['app3_finalize_output'] is None:
        st.session_state['data']['FINAL_SNA'] = np.nan
        # 1.firm-th 2.firm_eng 3. person
        total_df = pd.DataFrame()
        for target in range(1,3+1):
            filtered_df =  st.session_state['data'][st.session_state['data']['Class'].str.contains(st.session_state[f'assign_sna_target{target}]']['Class'])]
            block1 = st.empty()
            block1.info(f"Class : {st.session_state[f'assign_sna_target{target}]']['Class']}")
            for rank in range(1,4+1):
                if len(st.session_state[f'apply_order{target}_rank{rank}']) > 0:
                    block2 = st.empty()
                    block2.info(f"{st.session_state[f'apply_order{target}_rank{rank}']['function'].__name__}")
                    # skip matchedsna for person case
                    if bool(re.search('PERSON|ORD',st.session_state[f'assign_sna_target{target}]']['Class'].upper())) and bool(re.search('MATCHEDSNA',st.session_state[f'apply_order{target}_rank{rank}']['function'].__name__.upper())):
                        block2.empty()
                        continue
                    else:
                        filtered_df['FINAL_SNA'] = filtered_df.progress_apply(lambda row: \
                                                st.session_state[f'apply_order{target}_rank{rank}']['function'](row,
                                                                                                                st.session_state[f'apply_order{target}_rank{rank}']['input_column'],
                                                                                                                st.session_state[f'apply_order{target}_rank{rank}']['action'],
                                                                                                                condition =  st.session_state[f'apply_order{target}_rank{rank}']['condition']),
                                                                                                                axis = 1)
                    block2.empty()
            block1.empty()
            # combine red
            total_df = pd.concat([total_df,filtered_df])
            # count res
            target_col = 'FINAL_SNA'
            sna10_c = pd.DataFrame(total_df[f'{target_col}'].value_counts().reset_index())
            total_c = sum(sna10_c[f'{target_col}'])
            if total_c == total_df.shape[0]:
                sna10_c = sna10_c.copy()
                sna10_c.columns = [f'{target_col}','Counts']
            else:
                unk_extension = pd.DataFrame({'index':['UNKOWN'],f'{target_col}':[total_df.shape[0] - total_c]})
                sna10_c = pd.concat([sna10_c,unk_extension]).sort_values(f'{target_col}',ascending= False).reset_index(drop = True)
                sna10_c.columns = [f'{target_col}','Counts']
            
            matched_percent = np.round((total_c/total_df.shape[0])* 100,1)
            if 'app3_output_total_c' not in st.session_state:
                st.session_state['app3_output_total_c'] = load_in(total_c)
                st.session_state['app3_output_matched_percent'] = load_in(matched_percent)
                st.session_state['app3_output_result_c'] = load_in(sna10_c)
            st.session_state['app3_finalize_output'] = load_in(total_df)
            
if st.session_state['app3_finalize_output'] is not None:
    st.write(st.session_state['app3_finalize_output'])
    # if 'app3_output_total_c' not in st.session_state:
    #     st.session_state['app3_output_total_c'] = load_in(total_c)
    #     st.session_state['app3_output_matched_percent'] = load_in(matched_percent)
    #     st.session_state['app3_output_result_c'] = load_in(sna10_c)
    st.session_state['app3_rule_based_process'] = False

    st.success(f"สามารถ Assign SNA ได้ :green[{st.session_state['app3_output_matched_percent']}%] จากทั้งหมด", icon="✅")
    st.write(st.session_state['app3_output_result_c'])

############################## download    
    if 'app3_download_file' not in st.session_state:
        st.session_state.app3_download_file  = False

    def click_download():
        st.session_state.app3_download_file = True

    def click_fin_download():
        st.session_state.app3_download_file = False

    @st.cache_data
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')

    if st.session_state['app3_finalize_output'] is not None:
        #st.divider()
        if len(st.session_state['app3_finalize_output']) > 0:
            download_but = st.button('Download',on_click = click_download)

    if st.session_state.app3_download_file:
        prompt = False
        submitted = False
        csv = convert_df(st.session_state['app3_finalize_output'])
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

    if st.session_state.app3_download_file:
        if prompt and submitted:
            st.download_button(label="Download data as CSV",data = csv,file_name = f'{prompt}.csv',mime='text/csv',on_click = click_fin_download)

############################## Get Back
    def back_click3():
        st.session_state['app3_rule_based_prioritize'] = False
        st.session_state['app3_rule_based_process'] = True
        st.session_state['app3_finalize_output'] = None
        st.session_state.pop('app3_output_total_c',None)

    l3,r3 = st.columns([10,1])
    # with r2:
    #     next_bt2 = st.button('Next',on_click= submit_prioritize)
    with l3:
        back_bt3 = st.button('Back',on_click = back_click3)
