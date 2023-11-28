import streamlit as st
import pandas as pd
import numpy as np
import copy
import re
from utils.classify_holder_utils import * 
#from tqdm import tqdm
import time
from sklearn.metrics import accuracy_score,f1_score,precision_score,recall_score
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_extras.switch_page_button import switch_page
from stqdm import stqdm
from PIL import Image
from streamlit_extras.colored_header import colored_header
import io
stqdm.pandas()

################## 1.Regex
def protect_indiv_key():
    st.session_state.app1_possible_indiv_regex = st.session_state.app1_possible_indiv_regex
    st.session_state.app1_possible_indiv_default = st.session_state.app1_selected_indiv

def protect_company_key():
    st.session_state.app1_possible_company_regex = st.session_state.app1_possible_company_regex
    st.session_state.app1_possible_company_default = st.session_state.app1_selected_company

@st.cache_data
def load_in(input_):
    output = copy.deepcopy(input_)
    return output


@st.cache_data
def init_data_upload(uploaded_file,option):
    holder_names_df = uploaded_file.copy(deep = True)
    holder_col_name = copy.deepcopy(option)
    return holder_names_df,holder_col_name

@st.cache_data
def concat_name(selected_df):
    text_list = selected_df.values
    concated_names = []
    for t_list in stqdm(text_list):
        z = ['' if pd.isna(x) else x for x in t_list]
        text = ' '.join(z)
        concated_names.append(text.strip())
    return concated_names

def click_clean_restName(person_score,comp_score):
    st.session_state.app1_dev_CleanRestName = True
    st.session_state.nameseer_person = person_score
    st.session_state.nameseer_company = comp_score

def RevertToUserChoices():
    st.session_state.app1_dev_CleanRestName = False

def click_evaluation():
    st.session_state.app1_MockupEvaluation = True

def click_get_back():
    st.session_state.app1_regex = True
    st.session_state.app1_nameseer = False
    st.session_state.app1_dev_CleanRestName = False
    st.session_state.app1_MockupEvaluation = False
    
def ClickToNext():
    st.session_state.app1_NextPage = True

def click_startClassify():
    st.session_state.app1_nameseer = True

@st.cache_data
def Export_ToNext(input_):
    output = copy.deepcopy(input_)
    return output

def click_evaluation():
    st.session_state.app1_MockupEvaluation = True

def click_concat_mult():
    st.session_state.app1_prep_mult_nmcol = True
def click_get_back():
    st.session_state.app1_regex = True
    st.session_state.app1_nameseer = False
    st.session_state.app1_dev_CleanRestName = False
    st.session_state.app1_MockupEvaluation = False

default_indiv_options = ['นาย','นาง','นางสาว']
default_company_options = ['บริษัท','หส','หจ','หจก','ห้างหุ้น','จำกัด','มหาชน','ประเทศไทย']

if 'app1_possible_indiv_regex' not in st.session_state:
    #init for multiselect
    st.session_state.app1_possible_indiv_regex = None
    st.session_state.app1_possible_indiv_default = None
    #default vs developer choices
    st.session_state.app1_user_indiv_regex = default_indiv_options
    st.session_state.app1_developer_indiv_regex = ord_all_options
    #output
    st.session_state.app1_indiv_regex_output = None

if 'app1_possible_company_regex' not in st.session_state:
    #init for multiselect
    st.session_state.app1_possible_company_regex = None
    st.session_state.app1_possible_company_default = None
    #default vs developer choices
    st.session_state.app1_user_company_regex = default_company_options
    st.session_state.app1_developer_company_regex = firm_all_options
    #output
    st.session_state.app1_company_regex_output = None

if 'app1_NameClassify' not in st.session_state:
    st.session_state.app1_NameClassify = False
    st.session_state.app1_NameClassify_Output = None
    
    st.session_state.app1_upload = False
    st.session_state.app1_prep_mult_nmcol = False
    st.session_state.app1_regex = False
    st.session_state.app1_nameseer = False
    st.session_state.app1_dev_CleanRestName = False
    st.session_state.app1_MockupEvaluation = False
    st.session_state.app1_NextPage = False

################## 0. Upload Dataset ##################
if st.session_state.app1_upload == False:
    first_section = st.empty()
    with first_section.container():
        st.header("Please Upload Your Dataset (.csv หรือ .xlsx)")
        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file is not None:
            dataframe = pd.read_csv(uploaded_file)
            # glimpse result
            col1,col2 = st.columns(2)
            col1.write('First 5 Rows ')
            col1.write(dataframe.head())
            col2.write('Last 5 Rows')
            col2.write(dataframe.tail())

            col3,col4 = st.columns(2)
            col3.write('Summarized Fields')
            #col3.write(dataframe.columns.values)
            buf = io.StringIO()
            dataframe.info(buf=buf)
            s = buf.getvalue()
            lines = [line.split() for line in s.splitlines()[3:-2]]
            col3.write(pd.DataFrame(lines))

            col4.write(f'Total Rows = {len(dataframe)}')

            box_list = [None]
            box_list.extend(dataframe.columns)
           
            optional_concat = st.checkbox('IF Your Names Column is Multiple')
            if not optional_concat:
                option = st.selectbox('Which is Names Column ?',box_list,key = 'selected_option')
                st.session_state.option = st.session_state.selected_option
            elif optional_concat:
                option = st.multiselect(label = '',options = dataframe.columns.values,default = None,key = 'multiple_name_columns')
                submit_option = st.button('submit Name columns',on_click = click_concat_mult)
                if submit_option:
                    st.session_state.option = 'concated_name'
                    st.success("OK please start")
                
            if option is not None:
                start_name_classify =  st.button('Submit To Start')
                if start_name_classify:
                    if st.session_state.app1_prep_mult_nmcol:
                        dataframe['concated_name'] = concat_name(dataframe.filter(st.session_state.multiple_name_columns))
                        print(dataframe)
                    dataframe = dataframe.dropna(subset = st.session_state.option).reset_index(drop = True)
                    st.session_state.app1_dataframe,st.session_state.app1_name_column = init_data_upload(dataframe,st.session_state.option)
                    print(st.session_state.app1_dataframe)
                    print(st.session_state.app1_name_column)
                    st.session_state.app1_regex = True
                    first_section.empty()

#print(dataframe)
################## 1. Classify by Regex ##################
if st.session_state.app1_regex:
    st.session_state.app1_upload = True
    ### 1.1 Individuals
    indiv_regex_section = st.empty()
    with indiv_regex_section.container():
        st.header("1. คัดแยกบุคคล/บริษัท ด้วย Regex")
        with st.expander('more explanation about Regex'):
            st.write('regex is ...')
            
        st.write('ใช้ keyword ในการคัดแยกว่าเป็นบุคคลหรือบริษัท')
        st.subheader("1.1 คัดแยกบุคคลธรรมดา")
        
        user_indiv_regex_choices = st.radio(label = '',options = ['default_regex','developer_regex'],
                                            captions = ['keywords สำหรับคัดแยกบุคคลธรรมดา','*(Recommend) keywords ที่ developer ทำเอาไว้'], 
                                            index = 0,key = 'user_indiv_regex_choices_')
        if user_indiv_regex_choices == 'default_regex':
            st.session_state.app1_possible_indiv_regex = st.session_state.app1_user_indiv_regex
            st.session_state.app1_possible_indiv_default = copy.deepcopy(st.session_state.app1_user_indiv_regex)
        elif user_indiv_regex_choices == 'developer_regex':
            st.session_state.app1_possible_indiv_regex = st.session_state.app1_developer_indiv_regex
            st.session_state.app1_possible_indiv_default = copy.deepcopy(st.session_state.app1_developer_indiv_regex)

        t_indiv = st.text_input(label = 'add your person regex here',key = 'individuals_customize_input')
        if t_indiv != '':
            if t_indiv not in st.session_state.app1_possible_indiv_regex:
                st.session_state.app1_possible_indiv_regex.append(t_indiv)
                st.session_state.app1_possible_indiv_default.append(t_indiv)
        
        multi_indiv = st.multiselect(label = 'Choose your ordinary regex',
                        options = st.session_state.app1_possible_indiv_regex, default = st.session_state.app1_possible_indiv_default,
                        key='app1_selected_indiv',on_change = protect_indiv_key)
    ### 1.2 Company
    company_regex_section = st.empty()
    with company_regex_section.container():
        st.subheader("1.2 คัดแยกบริษัท")
        
        user_company_regex_choices = st.radio(label = '',options = ['default_regex','developer_regex'],
                                            captions = ['keywords สำหรับคัดแยกบริษัท','*(Recommend) keywords ที่ developer ทำเอาไว้'], 
                                            index = 0,key = 'user_company_regex_choices_')
        if user_company_regex_choices == 'default_regex':
            st.session_state.app1_possible_company_regex = st.session_state.app1_user_company_regex
            st.session_state.app1_possible_company_default = copy.deepcopy(st.session_state.app1_user_company_regex)
        elif user_company_regex_choices == 'developer_regex':
            st.session_state.app1_possible_company_regex = st.session_state.app1_developer_company_regex
            st.session_state.app1_possible_company_default = copy.deepcopy(st.session_state.app1_developer_company_regex)

        t_company = st.text_input(label = 'add your company regex here',key = 'company_customize_input')
        if t_company != '':
            if t_company not in st.session_state.possible_company_regex:
                st.session_state.app1_possible_company_regex.append(t_company)
                st.session_state.app1_possible_company_default.append(t_company)
        
        multi_company = st.multiselect(label = 'Choose your Company regex',
                        options = st.session_state.app1_possible_company_regex, default = st.session_state.app1_possible_company_default,
                        key='app1_selected_company',on_change = protect_company_key)

    ### submit to start classify process
    page1_section = st.empty()
    with page1_section.container():
        start_classify = st.button('Next',key = 'start_classify',on_click= click_startClassify)
        if start_classify:
            st.session_state.app1_inidiv_regex_output = load_in(st.session_state.app1_selected_indiv)
            st.session_state.app1_company_regex_output = load_in(st.session_state.app1_selected_company)
            indiv_regex_section.empty()
            company_regex_section.empty()
            #st.session_state.app1_nameseer = True
            page1_section.empty()


################## 2. Classify by Nameseer ##################
if st.session_state.app1_nameseer:
    st.session_state.app1_regex = False
    #names_df,names_namecolname = init_data()
    # if isinstance(st.session_state.app1_name_column,list):
    #     st.session_state.app1_name_column = load_in(st.session_state.app1_name_column[0])
    #st.session_state.app1_dataframe =  st.session_state.app1_dataframe.dropna(subset = st.session_state.app1_name_column).reset_index(drop = True)
    st.header('2. คัดแยกบุคคล/บริษัท ด้วย Nameseer')
    image = Image.open('material/images/nameseer.jpg')

    with st.expander("See More Explanation"):
        st.subheader('เป็นโมเดลสำหรับคัดแยกชื่อภาษาไทยว่าเป็น person หรือ company โดยจะมี score ซึ่งหมายถึงความมั่นใจของโมเดลในการคัดแยก')
        st.write("ซึ่งมีประโยชน์สำหรับกรณีชื่อที่ไม่มีคำระบุประเภท (ตามตัวอย่างด้านล่าง) รวมถึงเมื่อใช้ร่วมกับ Regex จะทำให้การคัดแยกแม่นยำมากขึ้น")
        st.image(image)

    st.subheader("User สามารถปรับ Threshold Score ของบุคคล/บริษัท ได้ตามความเหมาะสม")
    # print(st.session_state.app1_inidiv_regex_output)
    # print(st.session_state.app1_company_regex_output)
    thai_names,regex_ord_df,regex_firm_df,classified_person_eng,classified_firm_eng = preprocess_byRegex(st.session_state.app1_dataframe,
                                                                                                        st.session_state.app1_name_column,
                                                                                                       st.session_state.app1_inidiv_regex_output,
                                                                                                       st.session_state.app1_company_regex_output)
    
    slider_container = st.container()
    
    developer_choices_checkBox = st.checkbox("USE Developer Choices !!!")
    st.caption("หมายเหตุ: จะเป็น Rules ที่ Developer ลอง trial & error เพื่อให้ได้ผลที่คิดว่าดีที่สุด")
    if developer_choices_checkBox:
        st.session_state.nameseer_person = 0.8
        st.session_state.nameseer_company = 0.6

    with slider_container:
        st.slider(label = 'คัดแยกเป็นบุคคลธรรมดาเมื่อ person_score >=',min_value = 0.5,max_value =  1.0,value =  0.5, step = 0.01,key = 'nameseer_person')
        st.markdown("<div style='text-align: right;'><pre>ยิ่งมากยิ่งลด False Positive </pre>แต่มีความเสี่ยงที่ False Negative เพิ่มขึ้นหรือเกิด UNK ขึ้น</div>", unsafe_allow_html=True)
        st.slider(label = 'คัดแยกเป็นบริษัทเมื่อ company_score >=',min_value = 0.5,max_value =  1.0,value =  0.6, step = 0.01,key = 'nameseer_company')

    thai_names_ = thai_names.copy()
    nameseer_ord_df = thai_names_.query('tag_person >= @st.session_state.nameseer_person')
    nameseer_firm_df = thai_names_.query('tag_company >= @st.session_state.nameseer_company')
    nameseer_ord_df = anti_join(nameseer_ord_df,nameseer_firm_df.filter([st.session_state.app1_name_column]))
    nameseer_firm_df = anti_join(nameseer_firm_df,nameseer_ord_df.filter([st.session_state.app1_name_column]))
    ## unk names
    rest_name_th = anti_join(thai_names_,nameseer_ord_df.filter([st.session_state.app1_name_column]))
    rest_name_th = anti_join(rest_name_th,nameseer_firm_df.filter([st.session_state.app1_name_column]))
    ## output session
    regex_ord_df['Classified_By'] = 'regex'
    nameseer_ord_df['Classified_By'] = 'nameseer'
    classified_person_th = pd.concat([regex_ord_df.filter([st.session_state.app1_name_column,'Classified_By']),
                                      nameseer_ord_df.filter([st.session_state.app1_name_column,'Classified_By'])])
    classified_person_th['Class'] = 'person_th'


    classified_firm_th = pd.concat([regex_firm_df.filter([st.session_state.app1_name_column,'Classified_By']),
                                   nameseer_firm_df.filter([st.session_state.app1_name_column,'Classified_By'])])
    classified_firm_th['Class'] = 'firm_th'

    rest_name_th['Class'] = 'Unknown'
    rest_name_th['Classified_By'] = None
    
    output_classified = pd.concat([classified_person_th,
                              classified_firm_th,
                              classified_person_eng,
                              classified_firm_eng,
                              rest_name_th]).filter([st.session_state.app1_name_column,'Class','Classified_By']).reset_index(drop = True)
    
    if developer_choices_checkBox:
        suspect_ord_1 = nameseer_ord_df.query('tag_person >= 0.8')
        suspect_ord_2 = nameseer_firm_df.query('tag_company < 0.6')
        total_the_rest = pd.concat([suspect_ord_1.filter([st.session_state.app1_name_column]),suspect_ord_2.filter([st.session_state.app1_name_column]),
                            rest_name_th.filter([st.session_state.app1_name_column])])
        
        firm_keywords = ['CO', 'COMPANY', 'CORPORATION', 'CO\\.', 'CO\\s', 'ENTERPRISE',
            'ENTERPRISES', 'INC', 'INTERNATIONAL', 'LIMITED', 'LLC', 'LTD','TRUST','SERVICE',
            'NOMINEE', 'NOMINEES', 'PLC', 'PTE', 'PUBLIC', 'THAILAND', 'THE','คาร์โก้','FUND','BANK',
            '^.?บจ\\.?', '^.?หส\\.?', '^บ', '^บ\\s', '^บจ', '^หจ', '^หส','อาคาร','เจแปน',
            'กรม.*พัฒ', 'กรมการ', 'กลุ่ม', 'กอง.*โดย', 'กองมรดก', 'การประปา','โตโย','เซรามิค','แอส.*เ.*ท'
            'กิจการ', 'กิจการร่วมค้า', 'คอร์ปอร์เรชั่น', 'คอร์ปอเรชั่น','เทคนิค','แค.*ตอล','เอเนเจ','คอมแพนนี',
            'คอร์ปอเรชั้น', 'คอร์ปอเรท', 'คอร์เปอร์เรชั่น', 'คอร์เปอเรชั่น','เอ.*เนอ','ฮ่อง.*กง','โซ.*ล.?า',
            'คัมปะนี', 'คัมพะนี', 'คัมพานี', 'จดทะเบียน', 'จำกัด', 'จีเอ็มบี','บี\\.?วี','นิติบ','ฟา.*มา',
            'จีเอ็มบีเอช', 'ทรัสต', 'ทีม', 'นอมินี', 'บ\\.', 'บจก', 'บมจ','การบิน','แลนด์','โฮม','เบ.*เกอ',
            'บริษัท', 'บริษํท', 'บลจ', 'บี\\.วี\\.?', 'ประเทศไทย', 'พีทีวาย','ซิสเ','บีเอชดี','หลักทร',
            'พีทีอี', 'พีแอลซี', 'มหาชน', 'มหาลัย', 'มหาวิทยาลัย', 'มูลนิธิ','เวิร์คส','เวิ.*ค','โตเกีย','เวเคช',
            'ร้าน', 'ลิมิเ.*ด', 'ลิมิเด็ด', 'ลิมิเต็ด', 'วิสาหกิจ','คอมโพ','ไพรเวท','การคลัง','เทคโน','คลับ',
            'ศูนย์บริหาร', 'สถานสงเคราะห์', 'สถาบัน', 'สมาคม', 'สหกรณ์','ลิมิเต็ต','ลิมิเ','โกลบอล','คอน.*ัล',
            'สาขา', 'สำนักงาน', 'หจ\\.?', 'หจก', 'หจก\\.?', 'หส\\.', 'หุ้น','นิป.*ปอน','โรงพยาบาล','ประกัน',
            'ห้างหุ้นส่วนสามัญ', 'อิงค์', 'อิงส์', 'อินเตอร์เนชันแนล','มอเตอ','กองทุน','แอล.?แอล.?ซี','อิ.*ทริก',
            'อินเตอร์เนชั่นแนล', 'อิ้งค์', 'อุตสาหกรรม', 'เทศบาล', 'เอเชีย','ครอป','คอร์ป','ฟูด','แอส','แอร์',
            'เอเซีย', 'เอ็นเตอร์ไพรส์', 'เอ็นเตอร์ไพรส์เซส', 'เอ็นเตอร์ไพร์ส','คอมพะนี','คอมปา','โฮ.*ด.*ง',
            'แอนด', 'แอลซี', 'แอลทีดี', 'แอลเอซี', 'แอลแอลซี', 'แอสเสท','เอ็มบี','อินเวส','เอเจน',
            'โดย.*จำกัด', 'โดย.*นา', 'โฮลดิง', 'โฮลดิ้ง','กรุ.*ป','อีโอโอ','ไฟแนน','ซิสเต็ม','ทูล']

        bool_list = [bool(re.search('|'.join(firm_keywords),x.strip().upper())) for x in total_the_rest[st.session_state.app1_name_column]]
        if sum(bool_list) > 0:
            ord_the_rest = total_the_rest[~np.array(bool_list)]
            
        firm_the_rest = anti_join(total_the_rest,ord_the_rest.filter([st.session_state.app1_name_column]))

        ord_the_rest['Class'] = 'person_th'
        firm_the_rest['Class'] = 'firm_th'
        output_classified = pd.concat([ord_the_rest.filter([st.session_state.app1_name_column,'Class']),
                                    firm_the_rest.filter([st.session_state.app1_name_column,'Class']),
                                    classified_person_th.filter([st.session_state.app1_name_column,'Class']),
                                    classified_firm_th.filter([st.session_state.app1_name_column,'Class']),
                                    classified_person_eng.filter([st.session_state.app1_name_column,'Class']),
                                    classified_firm_eng.filter([st.session_state.app1_name_column,'Class'])]).drop_duplicates(st.session_state.app1_name_column).reset_index(drop = True)
    
    #refer count
    class_values = ['person_th','person_eng','firm_th','firm_eng','Unknown']
    values = [0,0,0,0,0]
    refer_c = pd.DataFrame({'Class':class_values,'Count':values})

    classifier_results = output_classified.Class.value_counts().reset_index()
    classifier_results.columns = ['Class','Count']

    result_c = refer_c.merge(classifier_results,
                on=['Class'],
                how='left',
                suffixes=('_x', None)).ffill(axis=1).drop(columns='Count_x')
    result_c['Count'] = result_c['Count'].astype(int)
    result_c = result_c.sort_values('Count',ascending = False).query('Count > 0').reset_index(drop = True)

    #st.header('3. Classify Results')
    st.divider()
    colored_header("3. Classify Results",color_name= "green-70",description='')
    st.subheader('จำนวนชื่อแยกรายประเภทที่คัดแยกได้') 
    st.write(result_c)
    st.subheader("Output ที่คัดแยกเสร็จแล้ว")
    #st.write(output_classified)
    
    filtered_df = dataframe_explorer(output_classified, case=False)
    st.dataframe(filtered_df, use_container_width=True)
    st.divider()
    
################## 2.1 Evaluation ##################
if st.session_state.app1_nameseer:
    with st.expander('Psuedo Evaluation'):
        st.subheader('เป็นการประเมินผลของ Classifiers (Regex/Nameseer)')
        st.caption('Disclaimer ผลของ evaluation มาจาก psuedo_label (เป็นผลที่โมเดลทำนายยังไม่ใช่ของจริง) จึงไม่เหมาะกับการนำไปอ้างอิงแบบจริงจัง')
        evaluation_button = st.button('Get Evaluation Results',key = 'evaluation_click',on_click = click_evaluation)
        if st.session_state.app1_MockupEvaluation:
            #mockup_df = st.session_state.app1_dataframe
            #mockup_df.rename(columns = {st.session_state.app1_name_column:'name'},inplace = True)
            indiv_answ,comp_answ = evaluation_mockup(st.session_state.app1_dataframe,st.session_state.app1_name_column)
            
            eva_col1,eva_col2 = st.columns(2)
            with eva_col1:
                if indiv_answ is not None:
                    st.write('Psuedo Evaluation Class: บุคคลธรรมดาที่เป็นชื่อภาษาไทย (person_th)')
                    indiv_answ = indiv_answ.filter([st.session_state.app1_name_column,'tag_person']).merge(output_classified,how = 'left').filter([st.session_state.app1_name_column,'Class','tag_person'])
                    indiv_answ['Psuedo_Label'] = 1
                    indiv_answ['Predict'] = [1 if x == 'person_th' else 0 for x in indiv_answ['Class']]

                    indiv_acc = accuracy_score(indiv_answ['Psuedo_Label'],indiv_answ['Predict'])
                    indiv_precision = precision_score(indiv_answ['Psuedo_Label'],indiv_answ['Predict'])
                    indiv_recall = recall_score(indiv_answ['Psuedo_Label'],indiv_answ['Predict'])
                    indiv_f1 = f1_score(indiv_answ['Psuedo_Label'],indiv_answ['Predict'])
                    indiv_total_samples = len(indiv_answ)
                    indiv_eva = pd.DataFrame({'acc':[indiv_acc],'precision':[indiv_precision],'recall':[indiv_recall],'f1_score':[indiv_f1],'sample':[indiv_total_samples]})
                    
                    indiv_answ['Psuedo_Label'] = 'person_th'
                    indiv_answ['Predict'] = indiv_answ['Class']
                    indiv_answ = indiv_answ.filter([st.session_state.app1_name_column,'Psuedo_Label','Predict'])
                    #indiv_answ.rename(columns = {st.session_state.app1_name_column:st.session_state.app1_name_column},inplace = True)
                    st.write(indiv_eva)
                    #st.write(indiv_answ.query('Actual != Predict'))
                    st.write('ตัวอย่างชื่อที่ classify ไม่ตรงกับ Psuedo Label')
                    st.dataframe(indiv_answ.query('Psuedo_Label != Predict'), use_container_width=True)
            with eva_col2:
                if comp_answ is not None:
                    st.write('Psuedo Evaluation Class: บริษัทที่เป็นชื่อภาษาไทย (company_th)')
                
                    comp_answ = comp_answ.filter([st.session_state.app1_name_column,'tag_company']).merge(output_classified,how = 'left').filter([st.session_state.app1_name_column,'Class','tag_company'])
                    comp_answ['Psuedo_Label'] = 1
                    comp_answ['Predict'] = [1 if x == 'firm_th' else 0 for x in comp_answ['Class']]

                    comp_acc = accuracy_score(comp_answ['Psuedo_Label'],comp_answ['Predict'])
                    comp_precision = precision_score(comp_answ['Psuedo_Label'],comp_answ['Predict'])
                    comp_recall = recall_score(comp_answ['Psuedo_Label'],comp_answ['Predict'])
                    comp_f1 = f1_score(comp_answ['Psuedo_Label'],comp_answ['Predict'])
                    comp_total_samples = len(comp_answ)
                    comp_eva = pd.DataFrame({'acc':[comp_acc],'precision':[comp_precision],'recall':[comp_recall],'f1_score':[comp_f1],'sample':[comp_total_samples]})
                    comp_answ['Psuedo_Label'] = 'firm_th'
                    
                    comp_answ['Predict'] = comp_answ['Class']
                    comp_answ = comp_answ.filter([st.session_state.app1_name_column,'Psuedo_Label','Predict'])
                    #comp_answ.rename(columns = {'name':st.session_state.app1_name_column},inplace = True)
                    st.write(comp_eva)
                    st.write('ตัวอย่างชื่อที่ classify ไม่ตรงกับ Psuedo Label')
                    st.dataframe(comp_answ.query('Psuedo_Label != Predict'), use_container_width=True)
                    #st.write(comp_answ.query('Actual != Predict'))

mult_cols = st.columns(9)
back_col = mult_cols[0]
next_col = mult_cols[-1]
with back_col:
    if (st.session_state.app1_regex == False) and (st.session_state.app1_upload == True):
        get_back = st.button('Back',key = 'get_back',on_click = click_get_back)
with next_col:
    if (st.session_state.app1_nameseer):
        get_next = st.button('Next')
        if get_next:
            st.session_state.app1_ExportOutput = Export_ToNext(output_classified)
            switch_page('name matching')
            