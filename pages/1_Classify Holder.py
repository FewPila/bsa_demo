import streamlit as st
import pandas as pd
import numpy as np
import copy
import re
#from utils.classify_holder_utils import * 
#from tqdm import tqdm
import time
from sklearn.metrics import accuracy_score,f1_score,precision_score,recall_score
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_extras.switch_page_button import switch_page
from stqdm import stqdm
from PIL import Image
from streamlit_extras.colored_header import colored_header
import io
import requests
stqdm.pandas()

def anti_join(df1,df2):
    outer = df1.merge(df2, how='outer', indicator=True)
    return outer[(outer._merge=='left_only')].drop('_merge', axis=1)

ord_all_options = ['(นาย|นาง).*โดย', '^.?MIS', '^.?MISS', 'MISS ', 'MISSนาย', 'MRS','MRS\\.',
   '^.?MR\\.',"MR\\s", 'MS\\.', 'MS\\. ', '^.(.)?(นาย|นาง)', '^.?.?(นาย|นาง)',
   '^.?.?นาง', '^.?.?นาย', '^.?คุณ', '^.?พัน', '^.?ร้อย', '^.?เรือ',
   '^นาง', '^นาย', 'กองทุนส่วนบุคคล', 'กองทุนส่วนบุคคุล', 'คณะ',
   '^.?คุณ', '^.?จ\\.ส\\.', '^.?จ\\.อ\\.', '^.?จ\\.อ\\.', 'จ่า', '^.?ด\\.ช', '^.?ด\\.ญ',
   '^.?ด\\.ต', '^.?ดร\\.', 'ดาบ', 'ด็อกเตอร์', 'ทันตแพทย์', '^.?น\\.ต','นส\\.',
   '^.?น\\.ท', '^.?น\\.พ', '^.?น\\.ส', '^.?น\\.ส\\', '^.?น\\.ส\\.', '^.?น\\.อ', '^.?นพ\\.',
   'นาง ', 'นางสาว', 'นางสาว ', 'นาย ', 'นายแพท',
   'นาวา', 'ผศ\\.', 'ผู้', '^.?พ\\.จ', 'พ\\.ญ', 'พ\\.ต', 'พ\\.ต\\.',
   '^.?พ\\.ท', '^.?พ\\.อ', '^.?พล\\.', '^.?พลต', '^.?พลอากา', '^.?พลอากาศ',
   'พลอากาศเอก', '^.?พลเ', '^.?พลเอ', '^.?พลโ', '^.?ม\\.ร', '^.?ม\\.ล', '^.?ร\\.ต',
   '^.?ร\\.ต', '^.?ร\\.ท', '^.?ร\\.อ', '^.?รศ\\.', 'รอง', 'รอง ', 'รอง\\s',
   '^.?ร้อย', '^.?ร้อยตร', '^.?ร้อยตรคณะ', '^.?ร้อยเอ', '^.?ร้อยโ', '^.?วท\\.ร\\.',
   '^.?ว่าที่', 'ศาสตราจารย์', '^.?ส\\.ต', '^.?ส\\.ท\\.', '^.?ส\\.อ', '^.?สาว',
   '^.?สิบ', 'หม่อมราชวง', 'หม่อมหลวง', 'เกตุ', 'เด็ก',
   'แพทย์หญิง', 'โดยบมจ','\\(นาง','\\(นาย','ดอกเตอร์']

firm_all_options = ['(กรุงเทพ)', '(ประเทศไทย)', '(มหาชน)', '(เอเชีย)', '(ไทย)',
        '(ไทยแลนด์)', 'BANK', 'BHD', 'CO.', 'COPO', 'CORP', 'CO\\.','FUND', 'GLOBAL', 'GPH', 'LC', 'LIMITED',
        'BRANCH','HOLD','SERVICE','TRUST','ประกัน','โรงพย','คอปอร์เร','เจริญโภคภัณฑ์','อิน.*ชัน','อิน.*ชั่น','โรงงา','ธนาคาร',
        'LLC', 'LTD', 'NOMINEES','PTE', 'SDN', 'SECURITIES', 'SINGAPORE', 'กฎหมาย', 'กราฟฟิค','กรีน', 'กรุ๊ป','ดีเวล',
        'กลาส', 'กลุ่ม', 'กอ.*ท.?น', 'กองทุน', 'กอล์ฟ','การก่อสร้าง', 'การค้า', 'การช่าง', 'การบัญชี', 'การพิมพ์','ห้องเย',
        'การาจ', 'การเกษตร', 'การโยธา', 'การไฟฟ้า', 'การ์ด', 'การ์เด้น','การ์เด้นท์', 'การ์เมนท์', 'การ์เม้นท์', 'กู๊ด', 'ก่อสร้าง',
        'ขนส่ง', 'ครอป', 'คราฟท์', 'ครีเอชั่น', 'ครีเอท', 'ครีเอทีฟ','คลับ', 'คลาวด์', 'คลินิก', 'คลีน', 'คลีนนิ่ง', 'ควอลิตี้','คอน.*ซัล',
        'คอนกรีต', 'คอนซัลติ้ง', 'คอนซัลท์', 'คอนซัลแตนท์','คอนซัลแทนซี่', 'คอนซัลแทนต์', 'คอนซัลแทนท์', 'คอนซัลแทนส์',
        'คอนวีเนี่ยนสโตร์', 'คอนสตรัค', 'คอนสตรัคชั่น', 'คอนสตรั๊คชั่น','คอนสทรัคชั่น', 'คอนเทนเนอร์', 'คอนเนคชั่น', 'คอนเน็คชั่น',
        'คอนแทรคเตอร์', 'คอนโด', 'คอนโดมิเนียม', 'คอนโทรล', 'คอฟฟี่','คอม.*นี', 'คอมปะ', 'คอมปะนี', 'คอมปา', 'คอมพิวเตอร์',
        'คอมมิวนิเคชั่น', 'คอมมูนิเคชั่น', 'คอมเพล็กซ์', 'คอมเมอร์เชียล','คอมเมิร์ซ', 'คอมโพ', 'คอร์ป', 'คอร์ปอร์เรชั่น', 'คอร์ปอเรชั่น',
        'คอร์ปอเรชั้น', 'คอร์ปอเรท', 'คอร์เปอร์เรชั่น', 'คอร์เปอเรชั่น','คอลเลคชั่น', 'คอสเมติก', 'คอสเมติกส์', 'คัมปะนี', 'คัมพานี',
        'คัมพานีแมเนจ', 'คัลเลอร์', 'คาร์', 'คาร์เร้นท์', 'คาร์โก้','คาเฟ่', 'คิทเช่น', 'ค้าวัสดุ', 'ค้าไม้', 'จัดหางาน', 'จำกัด',
        'จิวเวลรี่', 'จิเอ็มบีเอช', 'จี เอ็ม บี เอชนอมีนี', 'จีเอ็มบีเอช','ชิปปิ้ง', 'ช็อป', 'ซอฟต์แวร์', 'ซอฟท์แวร์', 'ซัคเซส', 'ซัพพลาย',
        'ซัพพลายส์', 'ซัพพลายเออร์', 'ซัพพอร์ต', 'ซัพพอร์ท', 'ซาวด์','ซิตี้', 'ซิลเวอร์', 'ซิสเต.*ม', 'ซิสเต็ม', 'ซิสเต็มส์', 'ซิสเทม',
        'ซิสเท็ม', 'ซิสเท็มส์', 'ซีฟู้ด', 'ซีวิล', 'ซีสเต็ม','ซีเคียวริตี้', 'ซึ่งจดทะเบียนแล้ว', 'ซุปเปอร์', 'ซุปเปอร์โปร','พลังงา',
        'ดอท', 'ดาต้า', 'ดิจิตอล', 'ดิจิทัล', 'ดิสทริบิวชั่น','ดิสทริบิวเตอร์', 'ดิเวลลอปเม้นท์', 'ดีซายน์', 'ดีเวลลอป','ผลิตภัณฑ์',
        'ดีเวลลอปเมนท์', 'ดีเวลลอปเม้นท์', 'ดีเวลล็อปเม้นท์','ดีเวลอปเมนท์', 'ดีเวลอปเม้นท์', 'ดีไซน์', 'ทนายความ', 'ทรัพย์ทวี',
        'ทรานสปอ', 'ทรานสปอร์ต', 'ทรานสปอร์ท', 'ทรานส์', 'ทราฟฟิค','ทราเวล', 'ทราเวิล', 'ทะเบียน', 'ทัวร์', 'ทาวเวอร์', 'ทิสโก้',
        'ทีม', 'ทูลลิ่ง', 'ทูลส', 'ทูลส์', 'ธุรกิจ', 'นอมีนี','นำคนต่างด้าวมาทำงานในประเทศ', 'นิตติ้ง', 'นิปปอน', 'บจ','บริวเวอ',
        'บจ\\.บริษัท', 'บจก', 'บมจ', 'บมจ\\.บริษัท', 'บรรจุภัณฑ์','บริการ', 'บริษัท', 'บริษํท', 'บลจ', 'บางกอก', 'บาร์', 'บิซิเนส',
        'บิลดิ้ง', 'บิลเดอร์', 'บิวดิ้ง', 'บิวตี้', 'บิวเดอร์', 'บิสซิเนส','บิสสิเนส', 'บิสิเนส', 'บี.วี', 'บี\\.วี', 'บี\\.วีกลุ่ม', 'บีช',
        'บีเอชดี', 'บ้าน', 'ปักกิ่ง', 'ปาร์ค', 'ปาล์ม', 'ปิโตรเลียม','ปิโตรเลี่ยม', 'พรอพเพอร์ตี้', 'พริ้นติ้ง', 'พริ้นท์', 'พรีซิชั่น',
        'พร็อพ', 'พร็อพเพอร์ตี้', 'พร็อพเพอร์ตี้ส์', 'พร๊อพเพอร์ตี้','พลัส', 'พลาซ่า', 'พลาสติก', 'พัฒนา', 'พัฒนาอิสลาม', 'พับลิชชิ่ง',
        'พาณิชย์', 'พาราวู้ด', 'พาราไดซ์', 'พาร์ค', 'พาร์ท', 'พาร์ทเนอ','พาร์ทเนอร์', 'พาร์ทเนอร์ส', 'พาวเวอร์', 'พีทีวาย', 'พีทีอี',
        'พีแอลซี', 'ฟรุ๊ต', 'ฟอร์เวิร์ด', 'ฟาร์ม', 'ฟาร์มา', 'ฟิตเนส','ฟิล์ม', 'ฟูดส์', 'ฟู้ด', 'ฟู้ดส์', 'ฟู๊ด', 'ฟู๊ดส์', 'มอเตอ',
        'มอเตอร์', 'มันนี่', 'มัลติมีเดีย', 'มา.*เกต', 'มาร์ท', 'มาร์เก็ต','มาร์เก็ตติ้ง', 'มาสเตอร์', 'มิวสิค', 'มิสเตอร์', 'มีเดีย',
        'มุลนิธิ', 'มุลนิธิจีเอ็มบีเอช', 'มูลนิธิ', 'ยูนิเวอร์แซล','ยูเนี่ยน', 'ยูไนเต็ด', 'รักษาความปลอดภัย', 'รับเบอร์','แลบบอ','แฟบริ',
        'รีซอร์สเซส', 'รีสอร์ท', 'รีเทล', 'รีเสิร์ช', 'รีไซเคิล', 'ร้าน','ลอนดรี้', 'ลอว์', 'ลิงค์', 'ลิซซิ่ง', 'ลิฟวิ่ง', 'ลิมิเด็ด',
        'ลิมิเต็ด', 'ลิสซิ่ง', 'ลีดเดอร์', 'ลีฟวิ่ง', 'ลีสซิ่ง', 'วอเตอร์','วัสดุก่อสร้าง', 'วัสดุภัณฑ์', 'วิชั่น', 'วิลล่า', 'วิลล่าส์',
        'วิลเลจ', 'วิศวกรรม', 'วู้ด', 'วู๊ด', 'ส\\.', 'สกิน', 'สตีล','สตูดิโอ', 'สถาปนิก', 'สปอร์ต', 'สปา', 'สมาคม', 'สมาร์ท', 'สยาม',
        'สยาม ', 'สำนักกฎหมาย', 'สำนักงาน', 'สเตชั่น', 'สเตนเลส', 'สเปซ','สแควร์', 'สแตนดาร์ด', 'สแตนเลส', 'สโตน', 'สโตร์', 'สไตล์', 'หจ',
        'หจ\\.', 'หจ\\.ห้างหุ้นส่วนจำกัด', 'หมู่', 'หลักทรัพ', 'หส\\.','หส\\.ห้างหุ้นส่วนสามัญ', 'หุ้น', 'ห้าง', 'ห้างทอง',
        'ห้างทองเยาวราช', 'ห้างหุ้นส่วนจำกัด', 'ห้างหุ้นส่วนสามัญ','อพาร์ทเมนท์', 'อพาร์ทเม้นท์', 'อลูมินั่ม', 'อลูมิเนียม', 'ออดิท',
        'ออดิทติ้ง', 'ออดิโอ', 'ออนไลน์', 'ออฟฟิศ', 'ออยล์', 'ออร์แกนิค','ออโต', 'ออโตเมชั่น', 'ออโตโมทีฟ', 'ออโตโมบิล', 'ออโต้',
        'ออโต้คาร์', 'ออโต้พาร์ท', 'ออโต้เซอร์วิส', 'อะโกร', 'อะไหล่ยนต์','อันดามัน', 'อาร์คิเทค', 'อาร์ต', 'อาร์ท', 'อิควิปเม้นท์', 'อิงค์',
        'อิงส์', 'อินชัวรันส์', 'อินดัสตรี', 'อินดัสตรีส์', 'อินดัสตรี้','อินดัสทรี', 'อินดัสทรีส์', 'อินดัสทรี่', 'อินดัสเตรียล',
        'อินดัสเทรียล', 'อินทิเกรชั่น', 'อินทีเรีย', 'อินฟอร์เมชั่น','อินสไปร์', 'อินเตอ', 'อินเตอร์', 'อินเตอร์กรุ๊ป', 'อินเตอร์ฟู้ด',
        'อินเตอร์เทค', 'อินเตอร์เทรด', 'อินเตอร์เทรดดิ้ง','อินเตอร์เนชันแนล', 'อินเตอร์เนชั่นแนล', 'อินเทลลิเจนท์', 'อินเวส',
        'อินโนเทค', 'อินโนเวชั่น', 'อินโนเวทีฟ', 'อิมปอร์ต','อิมปอร์ต-เอ็กซ์ปอร์ต', 'อิมพอร์ต', 'อิมพอร์ท', 'อิมเมจ',
        'อิเลคทริค', 'อิเล็กทรอนิกส์', 'อิเล็คทริค', 'อิ้งค์','อีควิปเมนท์', 'อีควิปเม้นท์', 'อีสเทิร์น', 'อีเนอจี้','แอ็คเค้า','อีเลค','อิเลค',
        'อีเลคทริค', 'อีเล็คทริค', 'อีเว้นท์', 'อุตสาหกรรม', 'อโกร','ฮอนดา', 'ฮอนด้า', 'ฮับ', 'ฮาร์ดแวร์', 'ฮ่องกง', 'เคมิคอล',
        'เคมิคัล', 'เคมีคอล', 'เครน', 'เจนเนอรัล', 'เจริญยนต์', 'เจเนอรัล','เจแปน', 'เซนเตอร์', 'เซฟตี้', 'เซรามิค', 'เซล', 'เซลล์', 'เซลส์',
        'เซอ.*วิส', 'เซอร์วิส', 'เซอร์วิสเซส', 'เซอร์เวย์', 'เซิร์ฟ','เซเว่น', 'เซ็นทรัล', 'เซ็นเตอ', 'เซ็นเตอร์', 'เดคคอร์',
        'เดคคอเรชั่น', 'เดคอร์', 'เดอะ', 'เทค', 'เทคนิ', 'เทคนิค','เทคนิคอล', 'เทคโน', 'เทคโนโลยี', 'เทคโนโลยีส์', 'เทคโนโลยี่',
        'เทรด', 'เทรดดิ้ง', 'เทรนนิ่ง', 'เทศบาล', 'เทเลคอม', 'เนเจอร์','เนเชอรัล', 'เน็ตเวิร์ค', 'เน็ทเวิร์ค', 'เบฟเวอเรจ', 'เบย์',
        'เบอเกอ', 'เบเกอรี', 'เบเกอรี่', 'เปเปอร์', 'เพลส', 'เพาเวอร์','เพ็ท', 'เพ้นท์', 'เฟรช', 'เฟอร์นิเจอร์', 'เภสัช', 'เมคเกอร์',
        'เมดดิคอล', 'เมดิคอล', 'เมททอล', 'เมทัล', 'เมทัลชีท','เมนเทนแนนซ์', 'เมอร์ชั่น', 'เมเนจเมนท์', 'เมเนจเม้นท์', 'เยาวราช',
        'เรดิโอ', 'เรสซิเดนซ์', 'เรสซิเด้นซ์', 'เรสเตอรองท์', 'เรียล','เรียลเอสเตท', 'เลิร์นนิ่ง', 'เลเซอร์', 'เวนเจอ', 'เวนเจอร์',
        'เวนเจอร์ส', 'เวลดิ้ง', 'เวลท์', 'เวลธ์', 'เวลเนส', 'เวิร์ค','เวิลด์', 'เวิลด์ไวด์', 'เอ.*จิเนีย', 'เอ.*เตอ', 'เอนจิเนียริ่ง',
        'เอนเตอร์ไพรส์', 'เอนเนอ', 'เอนเนอร์จี', 'เอนเนอร์ยี่','เอสดีเอ็น', 'เอสเตท', 'เอเจนซี่', 'เอเชีย', 'เอเซีย',
        'เอเซียNOMINEES','NOMINEES', 'เอเนเจีย', 'เอเยนซี่', 'เอ็กซ์ปอร์ต','เอ็กซ์พอร์ต', 'เอ็กซ์พอร์ท', 'เอ็กซ์เชนจ์', 'เอ็กซ์เพรส',
        'เอ็กซ์เพิร์ท', 'เอ็ดดูเคชั่น', 'เอ็นจิเนีย', 'เอ็นจิเนียริ่ง','เอ็นจิเนียร์', 'เอ็นจิเนียร์ริ่ง', 'เอ็นจีเนียริ่ง',
        'เอ็นเตอร์เทนเมนท์', 'เอ็นเตอร์เทนเม้นท์', 'เอ็นเตอร์ไพรซ์','เอ็นเตอร์ไพรส์', 'เอ็นเตอร์ไพรส์เซส', 'เอ็นเตอร์ไพร์ส', 'เอ็นเนอ',
        'เอ็นเนอร์จี', 'เอ็นเนอร์ยี', 'เอ็นเนอร์ยี่', 'เอ็ม\\.บี','เอ็มบี', 'เอ็มบีเอช', 'เอ็มไพร์', 'เฮลตี้', 'เฮลท์', 'เฮลท์ตี้',
        'เฮลท์แคร์', 'เฮลธ์', 'เฮอริเทจ', 'เฮาส', 'เฮาส์', 'เฮิร์บ','เฮ้าส์', 'เฮ้าส์ซิ่ง', 'แกลเลอรี่', 'แก๊ส', 'แค(บ|ป).*ตอล',
        'แคปปิตอล', 'แคร์', 'แทรคเตอร์', 'แทรเวล', 'แทรเวิล', 'แบรนด์','แปซิฟิก', 'แปซิฟิค', 'แพคเกจจิ้ง', 'แพลนท์', 'แพลนนิ่ง',
        'แพลนเนอร์', 'แพ็คกิ้ง', 'แพ็คเกจจิ้ง', 'แฟคตอรี่', 'แฟคทอรี่','แฟชั่น', 'แฟบริค', 'แฟมิลี่', 'แมชชินเนอรี่', 'แมชชีน',
        'แมชชีนเนอรี่', 'แมทที', 'แมททีเรียล', 'แมนชั่น', 'แมนู','แมนูแฟคเจอริ่ง', 'แมนเนจเมนท์', 'แมนเนจเม้นท์', 'แมเนจ',
        'แมเนจเมนท์', 'แมเนจเม้นท์', 'แลนด์', 'แลนด์สเคป', 'แลป', 'แล็บ','แอ.*เซท', 'แอคเคาท์', 'แอคเคาท์ติ้ง', 'แอคเคาน์ติ้ง', 'แอดวานซ์',
        'แอดเวอร์ไทซิ่ง', 'แอดไวซอรี่', 'แอดไวซ์', 'แอดไวเซอรี่', 'แอนด์','แอพพาเรล', 'แอร์', 'แอล.*พี', 'แอล.+ซี', 'แอลซี', 'แอลทีดี',
        'แอลพีจี', 'แอลเอซี', 'แอลแอลซี', 'แอสเซท', 'แอสเซ็ท', 'แอสเสท','แอสโซซิเอท', 'แอสโซซิเอทส์', 'แอ๊ดวานซ์', 'โกลด์', 'โกลบอล',
        'โกลเบิล', 'โซลาร์', 'โซลู', 'โซลูชั่น', 'โซลูชั่นส์', 'โซล่า','โซล่าร์', 'โดย ', 'โตเกียว', 'โตโยต้า', 'โตโยต้าเภสัช',
        'โบรกเกอร์', 'โบรคเกอร์', 'โบ๊ท', 'โปรดัก', 'โปรดักชั่น','โปรดักท์', 'โปรดักส์', 'โปรเกรส', 'โปรเจค', 'โปรเจคท์', 'โปรเจ็ค',
        'โปรเทคชั', 'โปรเฟสชั่นนอล', 'โปรเฟสชั่นแนล', 'โปรโมชั่น','โพรดักส์', 'โพรเกรส', 'โพลีเมอ', 'โพลีเมอร์', 'โมบาย', 'โมลด์',
        'โมเดิร์น', 'โรงรับจำนำ', 'โลจิส', 'โลจิสติก', 'โลจิสติกส์','โลจิสติคส์', 'โลหะกิจ', 'โฮ.*เต.?ล', 'โฮด', 'โฮม', 'โฮมส์', 'โฮล',
        'โฮลดิง', 'โฮลดิ้ง', 'โฮลดิ้งส์', 'โฮลเต็ล', 'โฮสด', 'โฮเต็ล','โฮเทล', 'ไซเอนซ์', 'ไทย', 'ไบโอ', 'ไบโอเทค', 'ไพรเวท', 'ไฟเบอร์',
        'ไฟแนน', 'ไมนิ่ง', 'ไลท์ติ้ง', 'ไลฟ์สไตล์', 'ไอที', 'ไฮดรอลิค','ไฮเทค','โปรเจก','จี เอ็ม บี เอช']

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

st.set_page_config(initial_sidebar_state = 'collapsed')
################## 1.Regex
def none_but_please_show_progress_bar(*args, **kwargs):
    bar = stqdm(*args, **kwargs)
    def checker(x):
        bar.update(1)
        return False
    return checker

def prepLines(lines):
    show_df = pd.DataFrame(lines)
    show_df = show_df.iloc[:,1:]
    show_df.columns = show_df.iloc[0]
    show_df.rename(columns = {'Non-Null':'Non-Null-Rows'},inplace = True)
    show_df = show_df.iloc[2:,[0,1]]
    return show_df

#@st.cache_data
def read_upload_data(df):
    section = st.empty()
    section.info('reading uploaded data')
    out = pd.read_csv(df,skiprows = none_but_please_show_progress_bar())
    section.empty()
    return out

@st.cache_data
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

def protect_indiv_key():
    st.session_state.app1_possible_indiv_regex = st.session_state.app1_possible_indiv_regex
    st.session_state.app1_possible_indiv_default = st.session_state.app1_selected_indiv

def protect_company_key():
    st.session_state.app1_possible_company_regex = st.session_state.app1_possible_company_regex
    st.session_state.app1_possible_company_default = st.session_state.app1_selected_company

def click_clean_restName(person_score,comp_score):
    st.session_state.app1_dev_CleanRestName = True
    st.session_state.nameseer_person = person_score
    st.session_state.nameseer_company = comp_score

def RevertToUserChoices():
    st.session_state.app1_dev_CleanRestName = False

def click_evaluation():
    st.session_state.app1_MockupEvaluation = True
    
def ClickToNext():
    st.session_state.app1_NextPage = True

def click_startClassify():
    #st.session_state.app1_nameseer = True
    st.session_state.app1_prepro_regex = True
    st.session_state.app1_indiv_regex_output = load_in(st.session_state.app1_selected_indiv)
    st.session_state.app1_company_regex_output = load_in(st.session_state.app1_selected_company)
    st.session_state.app1_regex = False

    # send to params
    st.session_state['params_person_regex_list'] = load_in(st.session_state.app1_selected_indiv)
    st.session_state['params_company_regex_list'] = load_in(st.session_state.app1_selected_company)

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
    st.session_state['app1_data'] = None
    st.session_state.app1_upload = False
    st.session_state.app1_prep_mult_nmcol = False
    st.session_state.app1_regex = False
    st.session_state.app1_prepro_regex = False
    st.session_state.app1_nameseer = False
    st.session_state.app1_dev_CleanRestName = False
    st.session_state.app1_MockupEvaluation = False
    st.session_state.app1_NextPage = False


if 'params_person_regex_list' not in st.session_state:
    st.session_state['params_person_regex_list'] = None
    st.session_state['params_company_regex_list'] = None
    st.session_state['params_nameseer_person_score'] = None
    st.session_state['params_nameseer_company_score'] = None
    st.session_state['params_nameseer_developer_option'] = None
    st.session_state['params_apply_nationality_classify'] = None


if 'app1_query_input' not in st.session_state:
    st.session_state.app1_query_input = False
    st.session_state.app1_query_cache  = False
    st.session_state.app1_dataframe = None
    st.session_state.app1_name_column = None

def submit_app1_input():
    if st.session_state.app1_prep_mult_nmcol:
        st.session_state.app1_dataframe['concated_name'] = concat_name(st.session_state.app1_dataframe.filter(st.session_state.multiple_name_columns))
    st.session_state.app1_dataframe = st.session_state.app1_dataframe.dropna(subset = st.session_state.selected_option).reset_index(drop = True)
    st.session_state.app1_name_column = load_in(st.session_state.selected_option)
    #st.session_state.app1_dataframe,st.session_state.app1_name_column = init_data_upload(dataframe,st.session_state.option)
    st.session_state.app1_regex = True
    st.session_state.app1_upload = True

@st.cache_data
def request_PreprocessByRegex(app1dataframe,app1_name_column,app1_indiv_regex_list,app1_company_regex_list):
    # define params
    port = 5001
    api_route = 'prep_regex'
    post_data = {
        'dataframe' : app1dataframe.fillna(0).to_dict(orient= 'list'),
        'name_column' : app1_name_column,
        'indiv_regex' : app1_indiv_regex_list,
        'company_regex' : app1_company_regex_list
    }

    with st.spinner('Wait for it...'):
        stm_wn = st.empty()
        stm_info = st.empty()
        stm_rows = st.empty()
        t0 = time.time()
        stm_wn.warning('ไม่สามารถแสดงผล Progress ให้ท่านดูได้')
        stm_info.info('แต่ตามสถิติจำนวนข้อมูลประมาณ 1,00,000 ชื่อใช้เวลาประมาณ 2 นาที')
        stm_rows.write(f"จำนวนข้อมูลของท่านมีจำนวน {st.session_state['app1_dataframe'].shape[0]} rows")
        res = requests.post(f'http://127.0.0.1:{port}/{api_route}', json = post_data)

        results = {}
        for key in res.json().keys():
            try:
                payload = res.json()[key]
                if len(payload) > 0:
                    data = pd.json_normalize(payload)
                else:
                    data = pd.DataFrame(columns = [st.session_state['app1_name_column']])    
            except:
                data = pd.DataFrame(columns = [st.session_state['app1_name_column']])
            results[key] = data
            
        #thai_names,regex_ord_df,regex_firm_df,classified_person_eng,classified_firm_eng = results.values()
        thai_names = results['thai_names']
        regex_ord_df = results['regex_ord_df']
        regex_firm_df = results['regex_firm_df']
        classified_person_eng = results['classified_person_eng']
        classified_firm_eng = results['classified_firm_eng']

        stm_wn.empty()
        stm_info.empty()
        stm_rows.empty()
        t1 = time.time()

    return thai_names,regex_ord_df,regex_firm_df,classified_person_eng,classified_firm_eng

#################################### Nat Classify ####################################
@st.cache_data
def request_nat_classify(target_df,holder_class_cn,holder_nat_cn,holder_name_cn):
    api_route = 'nat_classify'
    port = 5001
    
    post_data = {}
    post_data['target_df'] = target_df.copy().fillna(0).to_dict(orient= 'list')
    post_data['holder_class_cn'] = holder_class_cn
    post_data['holder_nat_cn'] = holder_nat_cn
    post_data['holder_name_cn'] = holder_name_cn

    res = requests.post(f'http://127.0.0.1:{port}/{api_route}', json = post_data)
    return pd.json_normalize(res.json()['result'])

if 'nat_classify_input' not in st.session_state:
    st.session_state['nat_classify_input'] = False
    st.session_state['nat_classify_output'] = False
    st.session_state['person_ava'] = None
    st.session_state['holder_class_cn'] = None
    st.session_state['holder_nat_cn'] = None
    st.session_state['holder_name_cn'] = None
    st.session_state['nat_classify_service'] = None
    st.session_state['data'] = None
    st.session_state['output_data'] = None

def submit_natclassify_input():
    st.session_state['holder_class_cn'] = 'Classified_Class'
    st.session_state['holder_nat_cn'] = st.session_state['input_holder_nat']
    st.session_state['holder_name_cn'] = st.session_state['input_holder_name']

    person_df = st.session_state['data'][st.session_state['person_ava']]
    target_df = person_df[person_df[st.session_state['holder_nat_cn']].isnull()]
    if len(target_df) > 0 :
        st.session_state['nat_classify_service'] = 'Success'
    else:
        st.session_state['nat_classify_service'] = 'Failed'

    st.session_state['nat_classify_input'] = True
    # send to params
    st.session_state['params_apply_nationality_classify'] = True


################## 0. Upload Dataset ##################
st.title('App 1. คัดแยกประเภทผู้ถือหุ้น')
st.write('การทำงานของโปรแกรมนี้จะใช้ทั้งหมด 2 วิธีในการคัดแยกประเภทของผู้ถือหุ้นว่าเป็น "บุคคลธรรมดา/บริษัท"')

image = Image.open('material/images/nameseerV2.jpg')
st.write(":blue[1.คัดแยกโดย Regex (Regular Expression)]")
st.code('Regex หรือก็คือ Keywords ในการเข้ามาจับ pattern ของแต่ละชื่อ \nเช่น "บริษัท,หจก.,จำกัด" หากมีคำดังกล่าวอยู่ในชื่อจะถูกคัดแยกเป็น -> "บริษัท" \nกรณีไม่สามารถคัดแยกได้ด้วย Regex จะถูกคัดแยกในขั้นตอนถัดไปคือ Nameseer')

with st.expander("คลิกเพื่อดูตัวอย่างการทำงานของ Regex"):
    st.write('ตัวอย่างการกำหนด Regex')
    st.code('''person_regex = ['นาย','นาง|นางสาว','^นาย'] # | หมายถึงหรือ,^ หมายถึงขึ้นต้นด้วย  \ncompany_regex = ['บริษัท','จำกัด','หจก.','มหาชน']''')
    first_text = 'นาย ปิติยาธร พิลาออน -> "บุคคลธรรมดา" \nปิติยาธร พิลาออน -> "Unknown" #เพราะไม่เจอใน person_regex'
    second_text = 'บริษัท ความอดทนมี จำกัด -> "บริษัท"\nเครือเจริญโภคภัณฑ์ -> "Unknown" #เพราะไม่เจอใน company_regex ' 
    st.caption(":orange[ตัวอย่าง ผลลัพธ์การคัดแยกประเภท]")
    st.code(f'{first_text}\n{second_text}')
    st.caption('หลังจากนั้นจะนำชื่อที่เป็น Unknown ไปคัดแยกต่อด้วย Nameseer')

st.write(":blue[2.คัดแยกโดย Nameseer]")
nameseer_v = 'Nameseer เป็นโมเดลสำหรับคัดแยกชื่อภาษาไทยว่าเป็น "บุคคลธรรมดา" หรือ "บริษัท" \
    \nโดยจะมี score ซึ่งหมายถึงความมั่นใจ(%) ของโมเดลในการคัดแยก \nคัดแยกโดยจะต้องตั้ง threshold เช่น person_score > 0.7 จะคัดแยกเป็น "บุคคลธรรมดา"\
    \nหรือ company_score > 0.6 จะคัดแยกเป็น "บริษัท" ซึ่งสามารถปรับแต่งได้ตามที่ต้องการ \n#โมเดล Nameseer จะให้ผลลัพธ์แต่ละชื่อมีได้แค่ Class เดียวว่าเป็น person หรือ company \n#ไม่สารถมีทั้ง person/company_score ได้พร้อมกัน ทำให้กฎการคัดแยกจะไม่ Overlap'
st.code(f'{nameseer_v}')

with st.expander("See More Explanation"):
    #st.write("ซึ่งมีประโยชน์สำหรับกรณีชื่อที่ไม่มีคำระบุประเภท (ตามตัวอย่างด้านล่าง) รวมถึงเมื่อใช้ร่วมกับ Regex จะทำให้การคัดแยกแม่นยำมากขึ้น")
    st.write('โดยจะใช้คัดแยกชื่อที่ไม่สามารถคัดแยกประเภทได้จาก Regex โดยผลของ Nameseer อาจมีความผิดพลาดได้เพราะเป็นโมเดลที่ใช้ความน่าจะเป็น \nตามตัวอย่างด้านล่าง')
    st.image(image)
    st.caption("หมายเหตุ: ชื่อจะมีได้แค่ Class เดียว เช่น หากมี person_score >= 0.5 ชื่อดังกล่าวจะไม่มีคะแนนในส่วนของ company_score ")


st.divider()
if st.session_state.app1_upload == False:    
    #st.header("Please Upload Your Dataset (.csv หรือ .xlsx)")
    st.header("กรุณาอัพโหลด Dataset เพื่อเริ่ม (.csv)")
    if st.session_state.app1_query_cache == False:
        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file is not None:
            st.session_state.app1_dataframe = read_upload_data(uploaded_file)
            st.session_state.app1_query_cache = True
        
    if st.session_state.app1_dataframe is not None:
        if (st.session_state.app1_dataframe.shape[0]) > 50000:
            st.write('สุ่มมาทั้งหมด 50,000 rows')
            st.write(st.session_state.app1_dataframe.sample(50000))
        else:
             st.write(st.session_state.app1_dataframe)
        st.write(f'{st.session_state.app1_dataframe.shape[0]} rows , {st.session_state.app1_dataframe.shape[1]} columns')

        buf = io.StringIO()
        st.session_state.app1_dataframe.info(buf=buf)
        s = buf.getvalue()
        lines = [line.split() for line in s.splitlines()[3:-2]]
        st.write('สรุปรายละเอียดของ Dataset')
        st.write(prepLines(lines))
        
        box_list = [None]
        box_list.extend(st.session_state.app1_dataframe.columns)

        upper_container = st.container()
        #optional_concat = st.checkbox('IF Your Names Column is Multiple')
        optional_concat = st.checkbox('หากต้องการรวมชื่อจากหลายคอลัมน์')
        with upper_container:
            if not optional_concat:
                st.write('โปรดเลือกคอลัมน์ชื่อที่ต้องการคัดแยกประเภท "บุคคลธรรมดา/ธุรกิจ"')
                option = st.selectbox('',box_list,key = 'selected_option',label_visibility='collapsed')
                #st.session_state.option = st.session_state.selected_option
            elif optional_concat:
                option = st.multiselect(label = '',options = st.session_state.app1_dataframe.columns.values,default = None,key = 'multiple_name_columns')
                submit_option = st.button('submit Name columns',on_click = click_concat_mult)
                if submit_option:
                    st.session_state.option = 'concated_name'
                    st.success("OK please start")
            if  st.session_state.selected_option is not None:
                start_name_classify =  st.button('คลิกเพื่อเริ่ม',on_click = submit_app1_input)
                            
                        
                    # if start_name_classify:
                    #     if st.session_state.app1_prep_mult_nmcol:
                    #         st.session_state.app1_query_df['concated_name'] = concat_name(st.session_state.app1_query_df.filter(st.session_state.multiple_name_columns))
                    #     st.session_state.app1_query_df = st.session_state.app1_query_df.dropna(subset = st.session_state.option).reset_index(drop = True)
                    #     st.session_state.app1_dataframe,st.session_state.app1_name_column = init_data_upload(dataframe,st.session_state.option)
                    #     print(st.session_state.app1_dataframe)
                    #     print(st.session_state.app1_name_column)
                    #     st.session_state.app1_regex = True
                    #     first_section.empty()

#print(dataframe)

if 'customize_upload_regex_indiv' not in st.session_state:
    st.session_state['customize_upload_regex_indiv'] = False
    st.session_state['indiv_uploaded_regex'] = None

def submit_uploaded_indiv():
    st.session_state['indiv_uploaded_regex'] = indiv_regex_df[indiv_regex_df.columns[0]].values.tolist()
    st.session_state['customize_upload_regex_indiv'] = True

if 'customize_upload_regex_company' not in st.session_state:
    st.session_state['customize_upload_regex_company'] = False
    st.session_state['company_uploaded_regex'] = None
    
def submit_uploaded_company():
    st.session_state['company_uploaded_regex'] = company_regex_df[company_regex_df.columns[0]].values.tolist()
    st.session_state['customize_upload_regex_company'] = True

################## 1. Classify by Regex ##################
if st.session_state.app1_regex:
    st.session_state.app1_upload = True
    ### 1.1 Individuals
    st.header("1. คัดแยกบุคคล/บริษัท ด้วย Regex")
    st.write('ใช้ keyword ในการคัดแยกว่าเป็น "บุคคล" หรือ "บริษัท"')
    st.subheader("1.1 คัดแยกบุคคลธรรมดา",divider = 'blue')
    
    user_indiv_regex_choices = st.radio(label = '',options = ['Suggested set of Keywords','Customize your own Keywords','Upload'],
                                        captions = ['Keywords ที่ Developer คัดสรรมาให้ซึ่งคิดว่าเหมาะสมกับ Dataset: CPFS_Shareholder','ปรับแต่ง Keywords เองทั้งหมด',''], 
                                        index = 0,key = 'user_indiv_regex_choices_',label_visibility= 'collapsed')

    if user_indiv_regex_choices == 'Customize your own Keywords':
        st.session_state.app1_possible_indiv_regex = st.session_state.app1_user_indiv_regex
        st.session_state.app1_possible_indiv_default = copy.deepcopy(st.session_state.app1_user_indiv_regex)
    elif user_indiv_regex_choices == 'Suggested set of Keywords':
        st.session_state.app1_possible_indiv_regex = st.session_state.app1_developer_indiv_regex
        st.session_state.app1_possible_indiv_default = copy.deepcopy(st.session_state.app1_developer_indiv_regex)
    elif user_indiv_regex_choices == 'Upload':
        if st.session_state['customize_upload_regex_indiv'] == False:
            indiv_regex_upload = st.file_uploader("Choose a file to upload",key = 'indiv_regex_upload')
            if indiv_regex_upload is not None:
                indiv_regex_df = read_upload_data(indiv_regex_upload)
                #st.session_state['indiv_uploaded_regex'] = indiv_regex_df[indiv_regex_df.columns[0]].values.tolist()
                st.write(indiv_regex_df)
                st.button('submit',on_click=submit_uploaded_indiv)

        if st.session_state['customize_upload_regex_indiv']:
            st.session_state.app1_possible_indiv_regex = copy.deepcopy(st.session_state['indiv_uploaded_regex'])
            st.session_state.app1_possible_indiv_default = copy.deepcopy(st.session_state['indiv_uploaded_regex'])

    t_indiv = st.text_input(label = 'เพิ่ม Keyword ตรงนี้',key = 'individuals_customize_input')
    if t_indiv != '':
        if t_indiv not in st.session_state.app1_possible_indiv_regex:
            st.session_state.app1_possible_indiv_regex.append(t_indiv)
            st.session_state.app1_possible_indiv_default.append(t_indiv)
    
    multi_indiv = st.multiselect(label = 'Keywords ทั้งหมดที่จะนำไปใช้คัดแยก "บุคคลธรรมดา"',
                    options = st.session_state.app1_possible_indiv_regex, default = st.session_state.app1_possible_indiv_default,
                    key='app1_selected_indiv',on_change = protect_indiv_key)
    ### 1.2 Company
    st.subheader("1.2 คัดแยกบริษัท",divider = 'blue')

    user_company_regex_choices = st.radio(label = '',options = ['Suggested set of Keywords','Customize your own Keywords','Upload'],
                                        captions = ['Keywords ที่ Developer คัดสรรมาให้ซึ่งคิดว่าเหมาะสมกับ Dataset: CPFS_Shareholder','ปรับแต่ง Keywords เองทั้งหมด',''], 
                                        index = 0,key = 'user_company_regex_choices_',label_visibility= 'collapsed')

    if user_company_regex_choices == 'Customize your own Keywords':
        st.session_state.app1_possible_company_regex = st.session_state.app1_user_company_regex
        st.session_state.app1_possible_company_default = copy.deepcopy(st.session_state.app1_user_company_regex)
    elif user_company_regex_choices == 'Suggested set of Keywords':
        st.session_state.app1_possible_company_regex = st.session_state.app1_developer_company_regex
        st.session_state.app1_possible_company_default = copy.deepcopy(st.session_state.app1_developer_company_regex)
    elif user_company_regex_choices == 'Upload':
        if st.session_state['customize_upload_regex_company'] == False:
            company_regex_upload = st.file_uploader("Choose a file to upload",key = 'company_regex_upload')
            if company_regex_upload is not None:
                company_regex_df = read_upload_data(company_regex_upload)
                #st.session_state['company_uploaded_regex'] = company_regex_df[company_regex_df.columns[0]].values.tolist()
                st.write(company_regex_df)
                st.button('submit',on_click=submit_uploaded_company)

        if st.session_state['customize_upload_regex_company']:
            st.session_state.app1_possible_company_regex = copy.deepcopy(st.session_state['company_uploaded_regex'])
            st.session_state.app1_possible_company_default = copy.deepcopy(st.session_state['company_uploaded_regex'])            

    t_company = st.text_input(label = 'เพิ่ม Keyword ตรงนี้',key = 'company_customize_input')
    if t_company != '':
        if t_company not in st.session_state.app1_possible_company_regex:
            st.session_state.app1_possible_company_regex.append(t_company)
            st.session_state.app1_possible_company_default.append(t_company)
    
    multi_company = st.multiselect(label = 'Keywords ทั้งหมดที่จะนำไปใช้คัดแยก "บริษัท"',
                    options = st.session_state.app1_possible_company_regex, default = st.session_state.app1_possible_company_default,
                    key='app1_selected_company',on_change = protect_company_key)

    ### submit to start classify process

    left,right = st.columns([10,1.5])
    with right:
        start_classify = st.button('Next',key = 'start_classify',on_click= click_startClassify)

    # <- get back 1
    def click_get_back1():
        st.session_state['app1_upload'] = False
        st.session_state['app1_regex'] = False

    if st.session_state.app1_regex:
        with left:
            st.button('Back',key = 'back1',on_click= click_get_back1)

################## 2. Preprocess Regex ###################
def is_firm_eng(x):
    eng_pat = ['STREET','CREDIT','J\.P\.','UBS','GLOBAL','CITI','GROUP','GOLDMAN SACHS','DATA','BEST',
               'INVEST','CEIC','HOLD','MEGA','UNIT','ASIA','CAP','CORP','INTER','EAST','WEST','FORTUNE',
              'HK ','PACIFIC','RESEARCH','TECH','INC','GPH','PTE','FINAN','CLIENT','ENGINE','LC','GOUR','PRECISION',
              'ELEC','DEVELOP','PLAN','HOTEL','RESID','RESORT','PRIME','MOTOR','ENERG','SYST','SOLU','PENANG','INTL',
              'NOMINESS','INVES','&','TERMINAL','MANAGE','FOOD','SCB','LAND','CHEMI','ASSET','INDUS','HONGKONG',
              'ENTERPR','WORLD','COPO','BATT?ERY','ADVER','ART','GROWTH','SOCIE','MORGAN STAN','JP MORGAN','CREAT','SERVICE',
              'LIFE','MEDIA','METAL','THE ','PRIVATE','INTELI','MODERN','MEDICAL','TRADE','NILSEN','TOKYO','ATLANTIC','CONTAIN',
              'LIMITED','MARKET','PAY ','CO\.','AUTO','FUND','LTD','MINING','PRODUCT','POWER','PROPE','TRAVEL','DOTCOM',
              'SATELLITE','COMMUNICATION','ACCOM','JAPAN','COMPANY','BANK','TRUST','COSMETI','MED','CARE','NOMINE',
              'GREAT','COMPU','STRAT','RESOUR','CARPET']
    eng_pat_re = '|'.join(eng_pat)
    
    try:
        out = True if re.search(eng_pat_re, x.strip().upper()) else False
    except:
        out = x
        
    return out

#@st.cache_data
def batch_request_PreproRegex(dataframe,name_colname,indiv_regex,company_regex,fold = 10):
    port = 5001
    api_route = 'prep_regex'
    
    total_names = pd.DataFrame()
    query_df_ = dataframe.copy()
    query_df_ = query_df_.drop_duplicates(name_colname).reset_index()
    query_df_.rename(columns = {'index':'query_index'},inplace = True)
    Whole_df = np.array_split(query_df_,fold)
    for samp_df in stqdm(Whole_df):

        post_data = {
            'dataframe' : samp_df.fillna(0).to_dict(orient= 'list'),
            'name_column' : name_colname,
            'indiv_regex' : indiv_regex,
            'company_regex' : company_regex
        }

        res = requests.post(f'http://127.0.0.1:{port}/{api_route}', json = post_data)
        if res.status_code == 201:
            result_df = pd.json_normalize(res.json()['total_names'])
            if len(result_df) > 0:
                total_names = pd.concat([total_names,result_df])
    return total_names.reset_index(drop = True)

@st.cache_data
def request_Nameseer(dataframe,name_colname):
    port = 5001
    api_route = 'prep_nameseer'
    post_data = {}
    post_data['dataframe'] = dataframe.to_dict(orient= 'list')
    post_data['name_column'] = name_colname
    
    res = requests.post(f'http://127.0.0.1:{port}/{api_route}', json = post_data)
    return pd.json_normalize(res.json()['thai_names'])


################## 2. Preprocess Regex ###################
if st.session_state.app1_prepro_regex:
    if 't_start' not in st.session_state:
        st.session_state['t_start'] = time.time()
    if 'first_clear' not in st.session_state:
        conditional_st_write_df.clear()
        load_in.clear()
        st.session_state['first_clear'] = True
        
    st.subheader('Preprocess Regex')
    prep_process = st.empty()
    prep_process.info('Classifiy by Regex : Please Wait')
    #st.info('Preprocess Regex')
    st.session_state['total_names'] = batch_request_PreproRegex(st.session_state.app1_dataframe,
                                            st.session_state.app1_name_column,
                                            st.session_state.app1_indiv_regex_output,
                                            st.session_state.app1_company_regex_output)
    eng_names = st.session_state['total_names'].query('is_eng == True')
    regex_firm_df = st.session_state['total_names'].query('is_firm == True')
    st.session_state['total_names'] = anti_join(st.session_state['total_names'],regex_firm_df.filter([st.session_state['app1_name_column']]))
    regex_ord_df = st.session_state['total_names'].query('is_ordinary == True')
    thai_names = anti_join(st.session_state['total_names'],regex_ord_df.filter([st.session_state['app1_name_column']]))

    eng_names['is_ordinary_eng'] = eng_names[st.session_state['app1_name_column']].progress_apply(lambda x : bool(re.search("MR\\.|MRS\\.|MISS|MS\\.",str(x).upper().strip())))
    person_eng = eng_names.query('is_ordinary_eng == True')
    eng_names = anti_join(eng_names,person_eng.filter([st.session_state['app1_name_column']]))

    eng_names['is_firm'] = eng_names[st.session_state['app1_name_column']].progress_apply(is_firm_eng)
    firm_eng = eng_names.query('is_firm == True')

    person_eng2 = anti_join(eng_names,firm_eng.filter([st.session_state['app1_name_column']]))

    ### classified eng
    classified_person_eng = pd.concat([person_eng.filter([st.session_state['app1_name_column']]),
                                person_eng2.filter([st.session_state['app1_name_column']])]).reset_index(drop = True)
    classified_person_eng['Classified_Class'] = 'person_eng'

    classified_firm_eng = firm_eng.filter([st.session_state['app1_name_column']]).reset_index(drop = True)
    classified_firm_eng['Classified_Class'] = 'firm_eng'

    #st.info('Preprocess Nameseer')
    if len(thai_names) > 0:
        thai_names = request_Nameseer(thai_names,st.session_state['app1_name_column'])
    else:
        thai_names = pd.DataFrame()

    st.session_state['thai_names'] = thai_names
    st.session_state['regex_ord_df'] = regex_ord_df 
    st.session_state['regex_firm_df'] = regex_firm_df
    st.session_state['classified_person_eng'] = classified_person_eng
    st.session_state['classified_firm_eng'] = classified_person_eng
    prep_process.empty()

    st.session_state['nameseer_buffer'] = True
    st.session_state.app1_nameseer = True
################## 2. Preprocess Regex ###################

if 'init_process_output' not in st.session_state:
    st.session_state['init_process_output'] = True
    st.session_state['process_output'] = True

def adjust_result():
    st.session_state['process_output'] = True

################## 2. Classify by Nameseer ##################
if st.session_state.app1_nameseer:
    st.session_state.app1_prepro_regex = False
        
    if st.session_state['nameseer_buffer'] and len(st.session_state['thai_names']) > 0:
        st.header("2. คัดแยกบุคคล/บริษัท ด้วย Nameseer",divider = 'blue')
    
    
    # if Regex cannot Perfectly Classfify 
    if len(st.session_state['thai_names']) > 0: 
        st.subheader("User สามารถปรับ Threshold Score ของบุคคล/บริษัท ได้ตามความเหมาะสม")
        slider_container = st.container()
        
        developer_choices_checkBox = st.checkbox("Suggested Threshold")
        st.caption("หมายเหตุ: จะเป็น Threshold ที่ Developer ลอง trial & error และมีการคำนวณใช้กฎเพิ่มเติมเพื่อให้ได้ผลที่คิดว่าดีที่สุด")
        if ('nameseer_person') and ('nameseer_company') not in st.session_state:
            st.session_state.nameseer_person = 0.5
            st.session_state.nameseer_company = 0.6
        if developer_choices_checkBox:
            st.session_state.nameseer_person = 0.8
            st.session_state.nameseer_company = 0.6

        with slider_container:
            nameseer_p = st.slider(label = 'คัดแยกเป็นบุคคลธรรมดาเมื่อ person_score >=',min_value = 0.5,max_value =  1.0,value =  st.session_state.nameseer_person, step = 0.01,key = 'nameseer_person')
            st.markdown("<div style='text-align: right;'><pre>ยิ่งมากยิ่งลด False Positive </pre>แต่มีความเสี่ยงที่ False Negative เพิ่มขึ้นหรือเกิด Unknown ขึ้น</div>", unsafe_allow_html=True)
            
            nameseer_c = st.slider(label = 'คัดแยกเป็นบริษัทเมื่อ company_score >=',min_value = 0.5,max_value =  1.0,value =  st.session_state.nameseer_company, step = 0.01,key = 'nameseer_company')
        
            if st.session_state['init_process_output'] == False:
                st.button('Adjust',key = 'adjust_nameseer_params',on_click = adjust_result)

        # button to adjust
        if st.session_state['process_output']:
            # IF USE SUGGESTED THRESHOLD
            if developer_choices_checkBox:
                thai_names_ = st.session_state['thai_names'].copy()
                #nameseer_ord_df = thai_names_.query('tag_person >= @st.session_state.nameseer_person')
                nameseer_ord_df = thai_names_.query('tag_person >= @nameseer_p')
                
                #nameseer_firm_df = thai_names_.query('tag_company >= @st.session_state.nameseer_company')
                nameseer_firm_df = thai_names_.query('tag_company >= @nameseer_c')
                
                nameseer_ord_df = anti_join(nameseer_ord_df,nameseer_firm_df.filter([st.session_state.app1_name_column]))
                nameseer_firm_df = anti_join(nameseer_firm_df,nameseer_ord_df.filter([st.session_state.app1_name_column]))
                ## unk names
                rest_name_th = anti_join(thai_names_,nameseer_ord_df.filter([st.session_state.app1_name_column]))
                rest_name_th = anti_join(rest_name_th,nameseer_firm_df.filter([st.session_state.app1_name_column]))
                ## suspect indiv
                suspect_ord_1 = nameseer_ord_df.query('tag_person >= 0.8')
                suspect_ord_2 = nameseer_firm_df.query('tag_company < 0.6')
                total_the_rest = pd.concat([suspect_ord_1.filter([st.session_state.app1_name_column]),suspect_ord_2.filter([st.session_state.app1_name_column]),
                                    rest_name_th.filter([st.session_state.app1_name_column])])

                nameseer_ord_df = anti_join(nameseer_ord_df,suspect_ord_1.filter([st.session_state.app1_name_column]))
                nameseer_firm_df = anti_join(nameseer_firm_df,suspect_ord_2.filter([st.session_state.app1_name_column]))

                bool_list = [bool(re.search('|'.join(firm_keywords),x.strip().upper())) for x in total_the_rest[st.session_state.app1_name_column]]
                if sum(bool_list) > 0:
                    ord_the_rest = total_the_rest[~np.array(bool_list)]
                    
                firm_the_rest = anti_join(total_the_rest,ord_the_rest.filter([st.session_state.app1_name_column]))
                ### gather output
                classified_person_th = pd.concat([nameseer_ord_df.filter([st.session_state.app1_name_column]),
                                                    ord_the_rest.filter([st.session_state.app1_name_column]),
                                                    st.session_state['regex_ord_df'].filter([st.session_state.app1_name_column]),
                                                    nameseer_ord_df.filter([st.session_state.app1_name_column])])
                classified_person_th['Classified_Class'] = 'person_th'


                classified_firm_th = pd.concat([nameseer_firm_df.filter([st.session_state.app1_name_column]),
                                                firm_the_rest.filter([st.session_state.app1_name_column]),
                                                st.session_state['regex_firm_df'].filter([st.session_state.app1_name_column]),
                                                nameseer_firm_df.filter([st.session_state.app1_name_column])])
                classified_firm_th['Classified_Class'] = 'firm_th'

                classified_result = pd.concat([
                                    classified_person_th.filter([st.session_state.app1_name_column,'Classified_Class']),
                                    classified_firm_th.filter([st.session_state.app1_name_column,'Classified_Class']),
                                    st.session_state['classified_person_eng'].filter([st.session_state.app1_name_column,'Classified_Class']),
                                    st.session_state['classified_firm_eng'].filter([st.session_state.app1_name_column,'Classified_Class'])
                                    ]).drop_duplicates(st.session_state.app1_name_column)
                output_classified = st.session_state.app1_dataframe.merge(classified_result.filter([st.session_state.app1_name_column,
                                                                                                'Classified_Class']),how = 'left')
                
                result_c = output_classified['Classified_Class'].value_counts(dropna = False).reset_index()
                result_c.columns = ['Classified_Class','Count']
                result_c['Count'] = result_c['Count'].astype(int)
                result_c = result_c.sort_values('Count',ascending = False).query('Count > 0').reset_index(drop = True)
                st.session_state['process_output'] = False
                # Finished
                st.session_state['app1_data'] = load_in(output_classified) 
                st.session_state['classified_result'] = load_in(classified_result)
                st.session_state['result_c'] = load_in(result_c)
            
            # NOT USE SUGGESTED THRESHOLD
            else:
                thai_names_ = st.session_state['thai_names'].copy()
                nameseer_ord_df = thai_names_.query('tag_person >= @nameseer_p')
                nameseer_firm_df = thai_names_.query('tag_company >= @nameseer_c')

                nameseer_ord_df = anti_join(nameseer_ord_df,nameseer_firm_df.filter([st.session_state.app1_name_column]))
                nameseer_firm_df = anti_join(nameseer_firm_df,nameseer_ord_df.filter([st.session_state.app1_name_column]))
                ## unk names
                rest_name_th = anti_join(thai_names_,nameseer_ord_df.filter([st.session_state.app1_name_column]))
                rest_name_th = anti_join(rest_name_th,nameseer_firm_df.filter([st.session_state.app1_name_column]))
                ## output session
                st.session_state['regex_ord_df']['Classified_By'] = 'regex'
                nameseer_ord_df['Classified_By'] = 'nameseer'
                classified_person_th = pd.concat([st.session_state['regex_ord_df'].filter([st.session_state.app1_name_column,'Classified_By']),
                                                nameseer_ord_df.filter([st.session_state.app1_name_column,'Classified_By'])])
                classified_person_th['Classified_Class'] = 'person_th'


                classified_firm_th = pd.concat([st.session_state['regex_firm_df'].filter([st.session_state.app1_name_column,'Classified_By']),
                                            nameseer_firm_df.filter([st.session_state.app1_name_column,'Classified_By'])])
                classified_firm_th['Classified_Class'] = 'firm_th'

                rest_name_th['Classified_Class'] = 'Unknown'
                rest_name_th['Classified_By'] = None

                classified_result = pd.concat([classified_person_th,
                                        classified_firm_th,
                                        st.session_state['classified_person_eng'],
                                        st.session_state['classified_firm_eng'],
                                        rest_name_th]).filter([st.session_state.app1_name_column,'Classified_Class','Classified_By']).reset_index(drop = True)
                output_classified = st.session_state.app1_dataframe.merge(classified_result.filter([st.session_state.app1_name_column,
                                                                                                'Classified_Class','Classified_By']),how = 'left')
                output_classified['Classified_Class'] = output_classified['Classified_Class'].fillna('Unknown') 
                
                result_c = output_classified['Classified_Class'].value_counts(dropna = False).reset_index()
                result_c.columns = ['Classified_Class','Count']
                result_c['Count'] = result_c['Count'].astype(int)
                result_c = result_c.sort_values('Count',ascending = False).query('Count > 0').reset_index(drop = True)

                # export to params
                st.session_state['params_nameseer_person_score'] = copy.deepcopy(nameseer_p)
                st.session_state['params_nameseer_company_score'] = copy.deepcopy(nameseer_c)
                st.session_state['params_nameseer_developer_option'] = copy.deepcopy(developer_choices_checkBox)
                st.session_state['process_output'] = False       
                # Finished
                st.session_state['app1_data'] = load_in(output_classified) 
                st.session_state['classified_result'] = load_in(classified_result)
                st.session_state['result_c'] = load_in(result_c)
    
    # IF Regex can perfectly Classified
    elif len(st.session_state['thai_names']) == 0:
        st.write("ไม่มีผลของ Nameseer เนื่องจากคัดแยกชื่อด้วย Regex ได้หมดแล้ว")
        st.session_state['nameseer_buffer'] = False
        
        classified_person_th = st.session_state['regex_ord_df'].filter([st.session_state.app1_name_column])
        classified_person_th['Classified_Class'] = 'person_th'

        classified_firm_th = st.session_state['regex_firm_df'].filter([st.session_state.app1_name_column])
        classified_firm_th['Classified_Class'] = 'firm_th'

        st.session_state['classified_person_eng']['Classified_Class'] = 'person_eng'
        st.session_state['classified_firm_eng']['Classified_Class'] = 'firm_eng'
        classified_result = pd.concat([classified_person_th,classified_firm_th,
                                       st.session_state['classified_person_eng'],st.session_state['classified_firm_eng']]).reset_index(drop = True)
        
        output_classified = st.session_state.app1_dataframe.merge(classified_result.filter([st.session_state.app1_name_column,
                                                                                           'Classified_Class']),how = 'left')

        result_c = output_classified['Classified_Class'].value_counts(dropna = False).reset_index()
        result_c.columns = ['Classified_Class','Count']
        result_c['Count'] = result_c['Count'].astype(int)
        result_c = result_c.sort_values('Count',ascending = False).query('Count > 0').reset_index(drop = True)
        st.session_state['process_output'] = False

        # Finished
        st.session_state['app1_data'] = load_in(output_classified)
        st.session_state['classified_result'] = load_in(classified_result)
        st.session_state['result_c'] = load_in(result_c)

    
#################################### Display Results ####################################
if st.session_state['nat_classify_input'] == False and st.session_state.app1_nameseer and st.session_state['app1_data'] is not None:
    st.session_state['init_process_output'] = False
    if 'second_clear' not in st.session_state:
        conditional_st_write_df.clear()
        load_in.clear()
        st.session_state['second_clear'] = True
    st.divider()
    st.header("3. Classifed Results",divider = 'green')
    st.subheader(f"คัดแยกได้ทั้งหมด {len(st.session_state['classified_result'])} ชื่อแยกเป็นประเภทดังนี้") 
    st.write(st.session_state['result_c'])
    st.subheader("Output ที่คัดแยกเสร็จแล้ว")
    conditional_st_write_df(dataframe_explorer(st.session_state['app1_data'],case = False))
    t_end = time.time()
    took_time = np.round((t_end - st.session_state['t_start'] )/60,2)
    st.write(f'ใช้เวลาในการรันทั้งหมด {took_time} นาที')

    params_data_dict = {
        'person_regex_list': [np.array(st.session_state['params_person_regex_list'],dtype = 'str')],
        'company_regex_list': [np.array(st.session_state['params_company_regex_list'],dtype = 'str')],
        'nameseer_person_score': [st.session_state['params_nameseer_person_score']],
        'nameseer_company_score': [st.session_state['params_nameseer_company_score']],
        'nameseer_developer_option': [st.session_state['params_nameseer_developer_option']],
        'apply_nationality_classify': [st.session_state['params_apply_nationality_classify']]
        }
    #params_df = pd.DataFrame(params_data_dict).transpose().reset_index()
    params_df = pd.DataFrame(params_data_dict)
    st.session_state['params_df'] = params_df.copy()
    ## Export Hyper Parameter for Nameseer
    #['dev_cleaning'] = True ?
    #['nameseer_person_score] = 
    #['nameseer_company_score] = 
#################################### Nat Classifier ####################################
if st.session_state['nat_classify_input'] == False and st.session_state.app1_nameseer:
    st.session_state['data'] = st.session_state['app1_data'].copy()
    st.session_state['person_ava'] = st.session_state['data']['Classified_Class'].str.upper().str.contains('PERSON|ORD',regex = True)
    if sum(st.session_state['person_ava']) > 0:
        apply_nat_classify_checkbox = st.checkbox('ต้องการใช้โมเดลคัดแยกสัญชาติบุคคลธรรมดา')
        st.caption('ใช้สำหรับการคัดแยกสัญชาติของผู้ถือหุ้นที่เป็นบุคคลธรรมดาที่ไม่มีสัญชาติ')
        if apply_nat_classify_checkbox:
            st.subheader("Please Select Necessary Columns")
            choices = [None]
            choices.extend(st.session_state['data'].columns.values)

            left,right,out = st.columns([10,10,10])
            left.subheader(f':gray[สัญชาติผู้ถือหุ้น :]')
            right.selectbox(label = '',options = choices,index = 0,key = 'input_holder_nat',label_visibility = 'collapsed')
            left.subheader(f':gray[ชื่อผู้ถือหุ้น :]')
            right.selectbox(label = '',options = choices,index = 0,key = 'input_holder_name',label_visibility = 'collapsed')

            submit_natclassify_input_bt = st.button('Submit',on_click = submit_natclassify_input)
            
            with st.expander('พารามิเตอร์ของ App1'):
                st.dataframe(st.session_state['params_df'])

if st.session_state['nat_classify_input'] and st.session_state['nat_classify_service'] == 'Success':
    person_df = st.session_state['data'][st.session_state['person_ava']]
    target_df = person_df[person_df[st.session_state['holder_nat_cn']].isnull()]
    
    
    result_df = request_nat_classify(target_df,
                                  st.session_state['holder_class_cn'],
                                  st.session_state['holder_nat_cn'],
                                  st.session_state['holder_name_cn'])
    
    st.session_state['data'] = st.session_state['data'].merge(result_df.filter([st.session_state['holder_name_cn'],st.session_state['holder_nat_cn']]),
                                                              on = st.session_state['holder_name_cn'],
                                                              how = 'left',suffixes= ['_left','_right'])
    st.session_state['data'][st.session_state['holder_nat_cn']] = st.session_state['data'][f"{st.session_state['holder_nat_cn']}_left"].fillna(st.session_state['data'][f"{st.session_state['holder_nat_cn']}_right"])
    st.session_state['data'] = st.session_state['data'].drop([f"{st.session_state['holder_nat_cn']}_left",f"{st.session_state['holder_nat_cn']}_right"],axis = 1)
    
    st.session_state['output_data'] = load_in(st.session_state['data'].copy())
    st.session_state['nat_classify_output'] = True
    st.session_state['nat_classify_service'] = None
    
elif st.session_state['nat_classify_input'] and st.session_state['nat_classify_service'] == 'Failed':
    st.subheader('Service : Failed')

if st.session_state['nat_classify_output'] == True:
    st.header("3. Classifed Results",divider = 'green')
    st.subheader(f"คัดแยกได้ทั้งหมด {len(st.session_state['classified_result'])} ชื่อแยกเป็นประเภทดังนี้") 
    st.write(st.session_state['result_c'])
    #st.subheader("Output ที่คัดแยกเสร็จแล้ว")
    st.subheader('Output หลังจาก Apply Nat Classifier')
    before_total_nan =  st.session_state['app1_data'][st.session_state['holder_nat_cn']].isnull().sum()
    after_total_nan = st.session_state['output_data'][st.session_state['holder_nat_cn']].isnull().sum()
    st.write(f'จำนวนสัญชาติที่เป็น NA ก่อนใช้โมเดลคัดแยกสัญชาติ {before_total_nan}')
    st.write(f'จำนวนสัญชาติที่เป็น NA หลังใช้โมเดลคัดแยกสัญชาติ {after_total_nan}')
    filtered_df = dataframe_explorer(st.session_state['output_data'], case=False)
    conditional_st_write_df(filtered_df)
    t_end = time.time()
    took_time = np.round((t_end - st.session_state['t_start'] )/60,2)
    st.write(f'ใช้เวลาในการรันทั้งหมด {took_time} นาที')
    
    with st.expander('พารามิเตอร์ของ App1'):
        st.dataframe(st.session_state['params_df'])
#################################### Nat Classifier ####################################
    

################## Download Results ##################
import streamlit.components.v1 as components
import base64
import json

def download_button(object_to_download, download_filename):
    """
    Generates a link to download the given object_to_download.
    Params:
    ------
    object_to_download:  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv,
    Returns:
    -------
    (str): the anchor tag to download object_to_download
    """
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # Try JSON encode for everything else
    else:
        object_to_download = json.dumps(object_to_download)

    try:
        # some strings <-> bytes conversions necessary here
        b64 = base64.b64encode(object_to_download.encode()).decode()

    except AttributeError as e:
        b64 = base64.b64encode(object_to_download).decode()

    dl_link = f'''
    <html>
    <head>
    <title>Start Auto Download file</title>
    <script src="http://code.jquery.com/jquery-3.2.1.min.js"></script>
    <script>
    $('<a href="data:text/csv;base64,{b64}" download="{download_filename}">')[0].click()
    </script>
    </head>
    </html>
    '''
    return dl_link

def download_df():
    df = st.session_state.export_data

    params_data_dict = {
    'person_regex_list': [st.session_state['params_person_regex_list']],
    'company_regex_list': [st.session_state['params_company_regex_list']],
    'nameseer_person_score': [st.session_state['params_nameseer_person_score']],
    'nameseer_company_score': [st.session_state['params_nameseer_company_score']],
    'nameseer_developer_option': [st.session_state['params_nameseer_developer_option']],
    'apply_nationality_classify': [st.session_state['params_apply_nationality_classify']]
    }
    params_df = pd.DataFrame(params_data_dict).transpose().reset_index()

    components.html(
        download_button(df, f'{st.session_state.filename}.csv'),
        height=0,
    )
    components.html(
        download_button(params_df, f'{st.session_state.filename}_params.csv'),
        height=0,
    )

if 'app1_download_file' not in st.session_state:
    st.session_state.app1_download_file  = False

if 'app1_download_params_file' not in st.session_state:
    st.session_state['app1_download_params_file'] = False

def click_download():
    st.session_state.app1_download_file = True

def click_fin_download():
    st.session_state.app1_download_file = False

def click_download_params():
    st.session_state.app1_download_params_file = True

def click_fin_download_params():
    st.session_state.app1_download_params_file = False


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

if st.session_state.app1_nameseer:
    #st.divider()
    if len(st.session_state['app1_data']) > 0:
        st.divider()
        download_but = st.button('Download',on_click = click_download)
        download_params_but = st.button('Download Params Data',on_click= click_download_params)

if st.session_state.app1_download_file:
    prompt = False
    submitted = False
    if st.session_state['nat_classify_output'] == True:
        st.write('this is output after Apply Nat Classifier')
        st.session_state.export_data = convert_df(st.session_state['output_data'])
    else:
        st.session_state.export_data = convert_df(st.session_state['app1_data'])

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
            
    # with st.form("my_download_form", clear_on_submit=True):
    #     st.text_input("กรุณาใส่ชื่อไฟล์", key="filename")
    #     submit = st.form_submit_button("Download Data & Params", on_click=download_df)

if st.session_state.app1_download_file:
    if prompt and submitted:
        #st.download_button(label="Download data as CSV",data = csv,file_name = f'{prompt}.csv',mime='text/csv',on_click = click_fin_download)
        st.download_button(label="Download data as CSV",data = st.session_state['export_data'],file_name = f'{prompt}.csv',mime='text/csv')
        
if st.session_state.app1_download_params_file:
    prompt2 = False
    submitted2 = False
    params_data_dict = {
    'person_regex_list': [st.session_state['params_person_regex_list']],
    'company_regex_list': [st.session_state['params_company_regex_list']],
    'nameseer_person_score': [st.session_state['params_nameseer_person_score']],
    'nameseer_company_score': [st.session_state['params_nameseer_company_score']],
    'nameseer_developer_option': [st.session_state['params_nameseer_developer_option']],
    'apply_nationality_classify': [st.session_state['params_apply_nationality_classify']]
    }
    params_df = pd.DataFrame(params_data_dict).transpose().reset_index()
    st.session_state['params_df'] = params_df.copy()

    with st.form('chat_input_form2'):
        # Create two columns; adjust the ratio to your liking
        col1_2, col2_2 = st.columns([3,1]) 
        # Use the first column for text input
        with col1_2:
            prompt2 = st.text_input(label = '',value='',placeholder='please write your file_name',label_visibility='collapsed')
        # Use the second column for the submit button
        with col2_2:
            submitted2 = st.form_submit_button('Submit')
        if prompt2 and submitted2:
            # Do something with the inputted text here
            st.write(f"Your file_name is: {prompt2}.csv")

if st.session_state.app1_download_params_file:
    if prompt2 and submitted2:
        st.download_button(label="Download Params data as CSV",data = st.session_state['params_df'].to_csv().encode('utf-8'),file_name = f'{prompt2}.csv',mime='text/csv',on_click = click_fin_download_params)

    
################## Back & Forward ##################
st.divider()
mult_cols = st.columns(9)
back_col = mult_cols[0]
next_col = mult_cols[-1]

def click_get_back2():
    st.session_state.app1_regex = True
    st.session_state.app1_nameseer = False
    st.session_state.app1_dev_CleanRestName = False
    st.session_state.app1_MockupEvaluation = False

# <- get back 2
with back_col:
    if (st.session_state.app1_regex == False) and (st.session_state.app1_upload == True):
        get_back = st.button('Back',key = 'get_back2',on_click = click_get_back2)
with next_col:
    if (st.session_state.app1_nameseer):
        get_next = st.button('Next')
        if get_next:
            if st.session_state['nat_classify_output']:
                st.session_state.app1_ExportOutput = Export_ToNext(st.session_state['output_data'])
            else:
                st.session_state.app1_ExportOutput = Export_ToNext(st.session_state['app1_data'])
            switch_page('name matching')
            
