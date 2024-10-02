import streamlit as st
import pandas as pd
import copy
import re
import os

@st.cache_data
def load_in(input_):
    output = copy.deepcopy(input_)
    return output

def highlighther(x_list):
    v_list = []
    for x in x_list:
        if x > 75:
            v = "background-color: #D35D6E; color: black; font-weight: bold;"
        elif x > 50:
            v = "background-color: #EFB08C; color: black; font-weight: bold;"
        elif x > 15:
            v = "background-color: #F8D49D; color: black; font-weight: bold;"
        elif x > 0:
            v = "background-color: #5AA469; color: white; font-weight: bold;"
        else:
            v = "background-color: #5AA469; color: white; font-weight: bold;"
        v_list.append(v)
    return v_list

def highlighther2(x_list):
    v_list = []
    for x in x_list:
        if x > 75:
            v = "background-color: #FF204E; color: white; font-weight: bold;"
        elif x > 50:
            v = "background-color: #A0153E; color: white; font-weight: bold;"
        elif x > 15:
            v = "background-color: #5D0E41; color: white; font-weight: bold;"
        elif x > 0:
            v = "background-color: #00224D; color: black; font-weight: bold;"
        else:
            v = "background-color: #00224D; color: black; font-weight: bold;"
        v_list.append(v)
    return v_list

if 'df' not in st.session_state:
    st.session_state['df'] = load_in(pd.read_csv('corpviz_data/group_data/group_monitor_table.csv'))

st.header('Warning Table')
st.write(st.session_state['df'].apply(highlighther,subset = ['2024-01','2024-02','2024-03','2024-04','2024-05','2024-06']).apply(highlighther2,subset = ['2023H1','2023H2','YTD'])).style.format("{:.4}",subset = ['2024-01','2024-02','2024-03','2024-04','2024-05','2024-06','2023H1','2023H2','YTD'])



if 'box_session' not in st.session_state:
    st.session_state['box_session'] = None

if 'sankey_session' not in st.session_state:
    st.session_state['sankey_session'] = False
    st.session_state['sankey_comp'] = None
    
if 'option' not in st.session_state:
    st.session_state['option'] = [re.sub('\\.html','',x) for x in os.listdir('corpviz_data/sankey_fig')]


# @st.cache_data
def submit_sankey():
    st.session_state['sankey_session'] = True
    st.session_state['sankey_comp'] = load_in(st.session_state['box_session'])
    with open(f"corpviz_data/sankey_fig/{st.session_state['sankey_comp']}.html",'r') as f: 
        html_data = f.read()
    st.session_state['html_data'] = load_in(html_data)

    st.session_state['debtor_data'] = load_in(pd.read_csv(f"corpviz_data/debtors_data/{st.session_state['sankey_comp']}.csv"))

    # st.header(f"Show an external {st.session_state['sankey_comp']}")
    # cache_load_html(st.session_state['html_data'])

@st.cache_resource
def cache_load_html(html):
    st.components.v1.html(html,width = 1080, height=720)

st.header('More Detail for each group')
# options = ['Central Pattana','Central Retail','Charoen Phokphan','CPALL','Centara']
st.selectbox(label= '',index = 0, options=st.session_state['option'],key = 'box_session')
if st.session_state['box_session'] is not None:
    st.write(st.session_state['box_session'])
    st.button('apply',on_click = submit_sankey)

    if st.session_state['sankey_session']:
        # Read file and keep in variable
        st.header(f"{st.session_state['sankey_comp']} : Monitoring Table")
        # st.write(st.session_state['debtor_data'])
        st.write(st.session_state['debtor_data'].apply(highlighther,subset = ['2024-01','2024-02','2024-03','2024-04','2024-05','2024-06']).apply(highlighther2,subset = ['2023H1','2023H2','YTD'])).style.format("{:.4}",subset = ['2024-01','2024-02','2024-03','2024-04','2024-05','2024-06','2023H1','2023H2','YTD'])
        ## Show in webpage
        st.header(f"{st.session_state['sankey_comp']} : Sankey Chart")
        # st.components.v1.html(st.session_state['html_data'],width = 1080, height=720)
        cache_load_html(st.session_state['html_data'])
        # st.session_state['sankey_session'] = False
