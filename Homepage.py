import streamlit as st
from streamlit_tags import st_tags
import pandas as pd
import os
import re
import io
import numpy as np
#from tqdm import tqdm
from stqdm import stqdm
from streamlit_extras.dataframe_explorer import dataframe_explorer
import copy
from streamlit_extras.switch_page_button import switch_page

stqdm.pandas()
st.title('Menu')

st.subheader(':green[1.Application: Classify Holder]')
st.write('ใช้สำหรับคัดแยกประเภทผู้ถือหุ้น')
nav_app1 = st.button('1. Go To Classify Holder App')
if nav_app1:
    switch_page('classify holder')

st.subheader(':red[2.Application: Name Matching]')
st.write('ใช้ทำ Name matching ระหว่าง dataset')
nav_app2 = st.button('2. Go To Name Matching App')
if nav_app2:
    switch_page('name matching')

st.subheader(':orange[3.Application: Assign SNA]')
st.write('ใช้สำหรับ Assign SNA ให้กับผู้ถือหุ้นเพื่อนำไปจัดทำ Sectoral Balance Sheet ต่อไป')
nav_app3 = st.button('3. Go To Assign SNA App')
if nav_app3:
    switch_page('assign sna')