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
from PIL import Image
#from utils.nm_utils import *
from streamlit_extras.switch_page_button import switch_page
import requests

default_regex_list = ['\\s','\\.','\\(.*\\)','-',',','[',']']

soft_simp_words = ['CO', 'COMPANY', 'CORPORATION', 'CO\\.', 'CO\\s', 'ENTERPRISE',
    'ENTERPRISES', 'INC', 'INTERNATIONAL', 'LIMITED', 'LLC', 'LTD',
    'NOMINEE', 'NOMINEES', 'PLC', 'PTE', 'PUBLIC', 'THAILAND', 'THE',
    '^.?บจ\\.?', '^.?หส\\.?', '^บ', '^บ\\s', '^บจ', '^หจ', '^หส',
    'กิจการ', 'กิจการร่วมค้า', 'คอร์ปอร์เรชั่น', 'คอร์ปอเรชั่น',
    'คอร์ปอเรชั้น', 'คอร์ปอเรท', 'คอร์เปอร์เรชั่น', 'คอร์เปอเรชั่น',
    'คัมปะนี', 'คัมพะนี', 'คัมพานี', 'จำกัด', 'จีเอ็มบีเอช', 'ทีม',
    'นอมินี', 'บ\\.', 'บจก', 'บมจ', 'บริษัท', 'บริษํท', 'บลจ',
    'ประเทศไทย', 'พีทีวาย', 'พีทีอี', 'พีแอลซี', 'มหาชน', 'ลิมิเด็ด',
    'ลิมิเต็ด', 'ศูนย์บริหาร', 'หจ\\.?', 'หจก', 'หจก\\.?', 'หส\\.',
    'หุ้น', 'ห้างหุ้นส่วนสามัญ', 'อิงค์', 'อิงส์', 'อินเตอร์เนชันแนล',
    'อินเตอร์เนชั่นแนล', 'อุตสาหกรรม', 'เทศบาล', 'เอ็นเตอร์ไพรส์',
    'เอ็นเตอร์ไพรส์เซส', 'เอ็นเตอร์ไพร์ส', 'แอลซี', 'แอลทีดี',
    'แอลเอซี', 'แอลแอลซี', 'โฮลดิง', 'โฮลดิ้ง']

hard_simp_words = ['(กรุงเทพ)', '(ประเทศไทย)', '(มหาชน)', '(เอเชีย)', '(ไทย)',
    '(ไทยแลนด์)', 'BANK', 'BHD', 'CO.', 'COPO', 'CORP', 'CO\\.','FUND', 'GLOBAL', 'GPH', 'LC', 'LIMITED',
    'LLC', 'LTD', 'NOMINEES','PTE', 'SDN', 'SECURITIES', 'SINGAPORE', 'กฎหมาย', 'กราฟฟิค','กรีน', 'กรุ๊ป', 
    'กลาส', 'กลุ่ม', 'กอ.*ท.?น', 'กองทุน', 'กอล์ฟ','การก่อสร้าง', 'การค้า', 'การช่าง', 'การบัญชี', 'การพิมพ์',
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
    'ซิสเท็ม', 'ซิสเท็มส์', 'ซีฟู้ด', 'ซีวิล', 'ซีสเต็ม','ซีเคียวริตี้', 'ซึ่งจดทะเบียนแล้ว', 'ซุปเปอร์', 'ซุปเปอร์โปร',
    'ดอท', 'ดาต้า', 'ดิจิตอล', 'ดิจิทัล', 'ดิสทริบิวชั่น','ดิสทริบิวเตอร์', 'ดิเวลลอปเม้นท์', 'ดีซายน์', 'ดีเวลลอป',
    'ดีเวลลอปเมนท์', 'ดีเวลลอปเม้นท์', 'ดีเวลล็อปเม้นท์','ดีเวลอปเมนท์', 'ดีเวลอปเม้นท์', 'ดีไซน์', 'ทนายความ', 'ทรัพย์ทวี',
    'ทรานสปอ', 'ทรานสปอร์ต', 'ทรานสปอร์ท', 'ทรานส์', 'ทราฟฟิค','ทราเวล', 'ทราเวิล', 'ทะเบียน', 'ทัวร์', 'ทาวเวอร์', 'ทิสโก้',
    'ทีม', 'ทูลลิ่ง', 'ทูลส', 'ทูลส์', 'ธุรกิจ', 'นอมีนี','นำคนต่างด้าวมาทำงานในประเทศ', 'นิตติ้ง', 'นิปปอน', 'บจ',
    'บจ\\.บริษัท', 'บจก', 'บมจ', 'บมจ\\.บริษัท', 'บรรจุภัณฑ์','บริการ', 'บริษัท', 'บริษํท', 'บลจ', 'บางกอก', 'บาร์', 'บิซิเนส',
    'บิลดิ้ง', 'บิลเดอร์', 'บิวดิ้ง', 'บิวตี้', 'บิวเดอร์', 'บิสซิเนส','บิสสิเนส', 'บิสิเนส', 'บี.วี', 'บี\\.วี', 'บี\\.วีกลุ่ม', 'บีช',
    'บีเอชดี', 'บ้าน', 'ปักกิ่ง', 'ปาร์ค', 'ปาล์ม', 'ปิโตรเลียม','ปิโตรเลี่ยม', 'พรอพเพอร์ตี้', 'พริ้นติ้ง', 'พริ้นท์', 'พรีซิชั่น',
    'พร็อพ', 'พร็อพเพอร์ตี้', 'พร็อพเพอร์ตี้ส์', 'พร๊อพเพอร์ตี้','พลัส', 'พลาซ่า', 'พลาสติก', 'พัฒนา', 'พัฒนาอิสลาม', 'พับลิชชิ่ง',
    'พาณิชย์', 'พาราวู้ด', 'พาราไดซ์', 'พาร์ค', 'พาร์ท', 'พาร์ทเนอ','พาร์ทเนอร์', 'พาร์ทเนอร์ส', 'พาวเวอร์', 'พีทีวาย', 'พีทีอี',
    'พีแอลซี', 'ฟรุ๊ต', 'ฟอร์เวิร์ด', 'ฟาร์ม', 'ฟาร์มา', 'ฟิตเนส','ฟิล์ม', 'ฟูดส์', 'ฟู้ด', 'ฟู้ดส์', 'ฟู๊ด', 'ฟู๊ดส์', 'มอเตอ',
    'มอเตอร์', 'มันนี่', 'มัลติมีเดีย', 'มา.*เกต', 'มาร์ท', 'มาร์เก็ต','มาร์เก็ตติ้ง', 'มาสเตอร์', 'มิวสิค', 'มิสเตอร์', 'มีเดีย',
    'มุลนิธิ', 'มุลนิธิจีเอ็มบีเอช', 'มูลนิธิ', 'ยูนิเวอร์แซล','ยูเนี่ยน', 'ยูไนเต็ด', 'รักษาความปลอดภัย', 'รับเบอร์',
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
    'อิเลคทริค', 'อิเล็กทรอนิกส์', 'อิเล็คทริค', 'อิ้งค์','อีควิปเมนท์', 'อีควิปเม้นท์', 'อีสเทิร์น', 'อีเนอจี้',
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
    'ไฟแนน', 'ไมนิ่ง', 'ไลท์ติ้ง', 'ไลฟ์สไตล์', 'ไอที', 'ไฮดรอลิค','ไฮเทค']

def anti_join(df1,df2):
    outer = df1.merge(df2, how='outer', indicator=True)
    return outer[(outer._merge=='left_only')].drop('_merge', axis=1)

st.title('App 2. การทำ Name Matching')
st.write('เชื่อมข้อมูลที่เกี่ยวข้องกันระหว่าง 2 Dataset เพื่อเอาข้อมูลที่ต้องการโดยใช้ "ชื่อ" เป็นตัวเชื่อม')
st.write('การทำงานของโปรแกรมนี้จะใช้ Score จากหลากหลาย Algorithm เพื่อช่วยให้ Name Matching แม่นยำมากขึ้น')


st.write("***:orange[1.Name Matching Algorithm]***")
st.code('Name Matching Algorithm ที่ใช้จะมีอยู่ดังนี้ \n1."TF-IDF Score"  2."Fuzzy Score"  3."Fuzzy Partial Score" \nโดยใช้ Score ดังกล่าวเข้ามาช่วย Confirm ว่าชื่อดังกล่าว Matching ได้ถูกต้อง')

with st.expander("คลิกเพื่อดูตัวอย่างการทำงานของ Name Matching"):
    st.code('''name1 = 'บริษัท เจริญโภคภัณฑ์อาหาร จำกัด (มหาชน)' \nname2 = 'เครือเจริญโภคภัณฑ์' ''')
    st.write("***:red[1. TF-IDF (3-Gram TF-IDF + Cosine Similarity)]***")
    st.write('ตัวอย่างการทำ 3-Gram Tokenization')
    st.code(''' Tokenize(name1)''')
    st.caption("'บริ|ริษ|ิษั|ษัท|ัท |ท เ| เจ|เจร|จริ|ริญ|ิญโ|ญโภ|โภค|ภคภ|คภั|ภัณ|ัณฑ|ณฑ์|ฑ์อ|์อา|อาห|าหา|หาร|าร |ร จ| จำ|จำก|ำกั|กัด|ัด |ด (| (ม|(มห|มหา|หาช|าชน|ชน)'")
    st.code('''Tokenize(name2)''')
    st.caption("เคร|ครื|รือ|ือเ|อเจ|เจร|จริ|ริญ|ิญโ|ญโภ|โภค|ภคภ|คภั|ภัณ|ัณฑ|ณฑ์")
    st.write("ตัวอย่างผลการหา Similarity ระหว่าง **name1** และ **name2** โดย **TF-IDF Cosine Similarity**")
    st.code('''consine_similarity(TfidfVectorize(Tokenize(name1)),TfidfVectorize(Tokenize(name2)))''')
    st.caption('TF-IDF Cosine Similarity : :green[48.9]')
    #st.divider()
    st.write('***:red[2. Fuzzy Ratio]***')
    st.write('see more information [link](https://github.com/maxbachmann/RapidFuzz)')
    st.write("ตัวอย่างผลการหา Similarity ระหว่าง **name1** และ **name2** โดย **Fuzzy Score**")
    st.code('''FuzzyRatio(name1,name2)''')
    st.caption("Fuzzy Ratio : :green[49.1]")
    st.write('***:red[3. Fuzzy Partial Ratio]***')
    st.write(':grey[หลักการเหมือนเหมือนกันกับ Fuzzy Score แต่จะให้น้ำหนักกับ "คำที่เหมือนกัน" มากกว่า ความยาวของคำ,การเรียงของคำ]')
    st.write("ตัวอย่างผลการหา Similarity ระหว่าง **name1** และ **name2** โดย **Fuzzy Partial Score**")
    st.code('''FuzzyPartialRatio(name1,name2) ''')
    st.caption("Fuzzy Partial Ratio : :green[72.2]")

st.write("***:orange[2.Matching Rules + Text Preprocess]***")
text_prep_descrip = 'กำหนด "Matching Rules" ว่า Score เท่าใดถึงจะ Confirm การ Matching และ \nการทำ Text Preprocess สามารถจะสามารถช่วยทำให้สามารถทำ Matching ได้ถูกต้องง่ายมากขึ้น'
st.code(f'{text_prep_descrip}')

image = Image.open('material/images/app2.jpg')
with st.expander("See More Explanation"):
    #st.write("ซึ่งมีประโยชน์สำหรับกรณีชื่อที่ไม่มีคำระบุประเภท (ตามตัวอย่างด้านล่าง) รวมถึงเมื่อใช้ร่วมกับ Regex จะทำให้การคัดแยกแม่นยำมากขึ้น")
    st.write('ในตัวอย่างจะกำหนดทุก TF-IDF >= 70 ขึ้นไปถึงจะ Confirm Matching')
    st.image(image)
    st.caption("ซึ่งตัว Matching Rules สามารถมีกี่อันก็ได้โดยจะเป็นเงื่อนไข OR")

st.divider()

if 't_zero' not in st.session_state:
    st.session_state.t_zero = time.time()

#@st.cache_data
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

def click_to_NM():
    st.session_state.app2_input = True

if 'order' not in st.session_state:
    st.session_state.order = {'corpus1':False,'corpus2':False,'corpus3':False}

if 'app1_ExportOutput' not in st.session_state:
    st.session_state.app1_ExportOutput = None

if 'app2_input' not in st.session_state:
    st.session_state.app2_input = False
    st.session_state.app2_output = None
    st.session_state['app2_finalize_output'] = None

# if 'app2_textprocess' not in st.session_state:
#     st.session_state.app2_textprocess = False
#     st.session_state.app2_textprocess_regex_list = False
#     st.session_state.app2_default_regex_list = copy.deepcopy(default_regex_list)
#     st.session_state.app2_developer_regex_list = copy.deepcopy(soft_simp_words)
#     st.session_state.app2_developer_regex_listV2 = copy.deepcopy(hard_simp_words)
#     st.session_state.app2_regex_listV1 = None
#     st.session_state.app2_regex_listV2 = None

if 'app2_preprocessNM' not in st.session_state:
    st.session_state.app2_preprocessNM = False

if 'possible_threshold_list' not in st.session_state:
    st.session_state.possible_threshold_list = ["tfidf_score >= 60 & fuzzy_ratio >= 90 & fuzzy_partialratio >= 90",
                           "tfidf_score >= 66.7 & fuzzy_partialratio >= 97","tfidf_score >= 70"]
    st.session_state.app2_possible_threshold_list = ["tfidf_score >= 60 & fuzzy_ratio >= 90 & fuzzy_partialratio >= 90",
                           "tfidf_score >= 66.7 & fuzzy_partialratio >= 97","tfidf_score >= 70"]

def submit_input_query():
    st.session_state.query_namecolname = st.session_state.namecol_select_box
    st.session_state.query_df = load_in(st.session_state.query_df.filter(st.session_state.query_keep_col))
    #st.session_state.query_df = st.session_state.query_df.drop_duplicates(st.session_state['query_namecolname']).reset_index(drop = True).reset_index().rename(columns = {'index':'query_index'})
    st.session_state.query_input = True

if 'query_input' not in st.session_state:
    st.session_state.query_input = False
    st.session_state.query_cache  = False
    st.session_state.query_df = None
    st.session_state.query_namecolname = None
#################################################################################################### 1 Query Input ####################################################################################################
if  st.session_state.query_input == False:
    st.header("Step 1: Input Dataset",divider= 'blue')
    
    def checkbox_check():
        st.session_state['query_df'] = None
        st.session_state['query_cache'] = False
        st.rerun()

    ### check query input
    if st.session_state.app1_ExportOutput is not None:
        check_box = st.checkbox('Use App1 Input',on_change = checkbox_check )
    else:
        check_box = False
  
    if st.session_state.query_cache == False:
        if check_box == False:
            query_upload = st.file_uploader("Choose a file to upload",key = 'query_upload')
            if query_upload is not None:
                st.session_state.query_df = read_upload_data(query_upload)
                st.session_state.query_cache = True
        elif check_box:
            if st.session_state.app1_ExportOutput is not None and check_box:
                st.session_state.query_df = load_in(st.session_state.app1_ExportOutput)
                st.session_state.query_cache = True
    # after have input
    if st.session_state.query_df is not None:
        #st.subheader('This is Your Query Dataset')
        #conditional_st_write_df(st.session_state.query_df)
        if (st.session_state.query_df.shape[0]) > 50000:
            st.write('สุ่มมาทั้งหมด 50,000 rows')
            st.write(st.session_state.query_df.sample(50000))
        else:
             st.write(st.session_state.query_df)
        st.write(f'{st.session_state.query_df.shape[0]} rows , {st.session_state.query_df.shape[1]} columns')
        # select Name Column
        query_namecol_box = [None]
        query_namecol_box.extend(st.session_state.query_df.columns)
        query_namecol_option = st.selectbox('โปรดเลือกคอลัมน์ "ชื่อ" ที่ต้องการจะ Name Matching',query_namecol_box,key = 'namecol_select_box')
        # select Column to keep
        query_keep_col_list = st.session_state.query_df.columns.values.tolist()
        st.multiselect(label = 'โปรดเลือกคอลัมน์ ที่ต้องการจะเก็บไว้',options = query_keep_col_list,default = query_keep_col_list,key = 'query_keep_col')
        # submit query_input
        if st.session_state['namecol_select_box'] is not None:
            submit_input_query = st.button('Submit',on_click = submit_input_query)

if st.session_state.app2_input == False:
    if st.session_state.query_input == True:
        st.header('Step 1: Input Dataset',divider = 'blue')
        #conditional_st_write_df(st.session_state.query_df)
        if (st.session_state.query_df.shape[0]) > 50000:
            st.write('สุ่มมาทั้งหมด 50,000 rows')
            st.write(st.session_state.query_df.sample(50000))
        else:
             st.write(st.session_state.query_df)        
        st.write(f'{st.session_state.query_df.shape[0]} rows , {st.session_state.query_df.shape[1]} columns')
#################################################################################################### 1 Query Input ####################################################################################################
from rapidfuzz import fuzz

# correct name with fuzzy
soft_simp_words = ['CO', 'COMPANY', 'CORPORATION', 'CO\\.', 'CO\\s', 'ENTERPRISE',
    'ENTERPRISES', 'INC', 'INTERNATIONAL', 'LIMITED', 'LLC', 'LTD',
    'NOMINEE', 'NOMINEES', 'PLC', 'PTE', 'PUBLIC', 'THAILAND', 'THE',
    '^.?บจ\\.?', '^.?หส\\.?', '^บ\\s', '^บจ', '^หจ', '^หส',
    'กิจการ', 'กิจการร่วมค้า', 'คอร์ปอร์เรชั่น', 'คอร์ปอเรชั่น',
    'คอร์ปอเรชั้น', 'คอร์ปอเรท', 'คอร์เปอร์เรชั่น', 'คอร์เปอเรชั่น',
    'คัมปะนี', 'คัมพะนี', 'คัมพานี', 'จำกัด', 'จีเอ็มบีเอช', 'ทีม',
    'นอมินี', 'บ\\.', 'บจก', 'บมจ', 'บริษัท', 'บริษํท', 'บลจ',
    'ประเทศไทย', 'พีทีวาย', 'พีทีอี', 'พีแอลซี', 'มหาชน', 'ลิมิเด็ด',
    'ลิมิเต็ด', 'ศูนย์บริหาร', 'หจ\\.?', 'หจก', 'หจก\\.?', 'หส\\.',
    'หุ้น', 'ห้างหุ้นส่วนสามัญ', 'อิงค์', 'อิงส์', 'อินเตอร์เนชันแนล',
    'อินเตอร์เนชั่นแนล', 'อุตสาหกรรม', 'เทศบาล', 'เอ็นเตอร์ไพรส์',
    'เอ็นเตอร์ไพรส์เซส', 'เอ็นเตอร์ไพร์ส', 'แอลซี', 'แอลทีดี',
    'แอลเอซี', 'แอลแอลซี', 'โฮลดิง', 'โฮลดิ้ง']

def simplify_name(x,regex_list):
    x = str(x)
    regex_list_re = '|'.join(regex_list)
    x1 = str(x).strip().upper()
    x2 = re.sub(regex_list_re,'',x1)
    return x2 if len(x2)>0 else x1


if 'ipi_df' not in st.session_state:
    st.session_state['ipi_df'] = pd.read_csv('fake_dataset/fake_ipi.csv')
    st.session_state['ipi_df']['SRC_UNQ_ID'] = st.session_state['ipi_df']['SRC_UNQ_ID'].astype(str).str.zfill(13)

if 'corpus1_input' not in st.session_state:
    st.session_state.corpus1_input = False
    st.session_state.corpus1_cache  = False
    st.session_state['uploaded_corpus1'] = False
    st.session_state['corpus1_use_ipi'] = False
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
    # add corpus
    st.session_state.add_corpus2 = False

def corpus1_SelectCol_click():
    st.session_state.corpus1_namecolname = load_in(st.session_state.corpus1_namecol_select_box)

def corpus1_SelectCol_list_click():
    st.session_state.corpus1_selected_col_list = load_in(st.session_state.corpus1_col_list_select_box)
    st.session_state.corpus1_df = load_in(st.session_state.corpus1_df.filter(st.session_state.corpus1_selected_col_list))

def corpus1_click_use_ipi():
    st.session_state['corpus1_df'] = st.session_state['ipi_df'].copy()
    st.session_state['uploaded_corpus1'] = True
    st.session_state['corpus1_use_ipi'] = True

def corpus1_submit():
    st.session_state.corpus1_partial_nm  = load_in(corpus1_partialnm_box)
    
    # adjust query
    st.session_state.query1_filter_option_out = load_in(st.session_state.query1_filter_option)
    if st.session_state.query1_filter_choices is not None:
        st.session_state.query1_filter_choices_out = load_in(st.session_state.query1_filter_choices)
    elif st.session_state.query1_filter_range is not None:
        st.session_state.query1_filter_range_out = load_in(st.session_state.query1_filter_range)
    
    if st.session_state.query1_filter_option_out is not None:
        st.session_state.adjust_query1 = load_in(True)
        if bool(re.search('num|float|int',query1_type_string)):
            st.session_state.query1_filter_option_dtype = load_in('numeric')
        else:
            st.session_state.query1_filter_option_dtype = load_in('object')
    
    if st.session_state.query1_filter_choices_out is not None:
        st.session_state.query1_filter_condition = load_in(st.session_state.query1_filter_choices_out)
    elif st.session_state.query1_filter_range_out is not None:
        st.session_state.query1_filter_condition = load_in(st.session_state.query1_filter_range_out)
    
    # input file_name
    st.session_state.corpus1_file_name = 'data1'
    # if not st.session_state['corpus1_use_ipi']:
    #     st.session_state.corpus1_file_name = load_in(re.sub('\\.csv','',corpus1_upload.name))
    # else:
    #     st.session_state.corpus1_file_name = load_in('IPI_DATASET')
    st.session_state.corpus1_df = st.session_state.corpus1_df.reset_index(drop = True).reset_index()
    st.session_state.corpus1_df = load_in(st.session_state.corpus1_df.rename(columns = {'index':'corpus_index'}))

    # Merge IPI Session
    if not st.session_state['corpus1_use_ipi']:
        if corpus1_merge_ipi_box:
            st.session_state['corpus1_RID_CN']
            st.session_state['corpus1_Name_CN']
            st.session_state['corpus1_df'][st.session_state['corpus1_RID_CN']] = st.session_state['corpus1_df'][st.session_state['corpus1_RID_CN']].astype(str).str.zfill(13)
            r_df = st.session_state['corpus1_df'].merge(st.session_state['ipi_df'].rename(columns = {'SRC_UNQ_ID':st.session_state['corpus1_RID_CN']}),
                                                        on = st.session_state['corpus1_RID_CN'],
                                                        how = 'left')
            r_df['SCORE'] = r_df.apply(lambda row: fuzz.ratio(row[st.session_state['corpus1_Name_CN']],row['RGST_BSN_NM_THAI']),axis = 1)
            r_df['SIMP_SCORE'] = r_df.apply(lambda row : fuzz.ratio(simplify_name(row[st.session_state['corpus1_Name_CN']],soft_simp_words),
                                                    simplify_name(row['RGST_BSN_NM_THAI'],soft_simp_words)),axis = 1)
            r_keep_col = [st.session_state['corpus1_RID_CN'],'RGST_BSN_NM_THAI','SNA 2008']
            st.session_state['corpus1_df'] = st.session_state['corpus1_df'].merge(r_df.query('SIMP_SCORE >= 60.1 & SCORE >= 26').filter(r_keep_col),how = 'left')

    st.session_state.corpus1_input = True

def click_add_corpus2():
    st.session_state.add_corpus2 = True

#################################################################################################### 2.1 Corpus Input ####################################################################################################
if st.session_state.query_input == True and st.session_state.corpus1_input == False and st.session_state.app2_input == False:
    st.divider()
    st.header('Step 2.1: Dataset ที่ต้องการจะ Matching ด้วย',divider= 'orange')
    
    if st.session_state['uploaded_corpus1'] == False:
        corpus1_upload = st.file_uploader("Choose a file to upload",key = 'corpus1_upload')
        if corpus1_upload is not None:
            if st.session_state.corpus1_cache == False:
                st.session_state.corpus1_df = read_upload_data(corpus1_upload)
                st.session_state.corpus1_cache = True
                st.session_state['uploaded_corpus1'] = True

    if not st.session_state['corpus1_use_ipi']:
        corpus1_use_ipi_checkbox = st.checkbox('Use IPI Dataset')
        if corpus1_use_ipi_checkbox:
            st.button('Name Matching with IPI Dataset',key = 'corpus1_use_nm_ipi',on_click = corpus1_click_use_ipi)
    
    if st.session_state.corpus1_df is not None:
        #st.subheader('This is Your Corpus Dataset')
        conditional_st_write_df(st.session_state.corpus1_df)
        st.write(f'{st.session_state.corpus1_df.shape[0]} rows , {st.session_state.corpus1_df.shape[1]} columns')
        
        if st.session_state.corpus1_namecolname is None:
            #select Name Column
            corpus1_namecol_box = [None]
            corpus1_namecol_box.extend(st.session_state.corpus1_df.columns)
            corpus1_namecol_option = st.selectbox('โปรดเลือกคอลัมน์ "ชื่อ" ที่ต้องการจะ Name Matching',corpus1_namecol_box,key = 'corpus1_namecol_select_box')
            if st.session_state['corpus1_namecol_select_box'] is not None:
                corpus1_selected_namecol = st.button('Next',on_click = corpus1_SelectCol_click)
        
        if st.session_state.corpus1_namecolname is not None and st.session_state.corpus1_selected_col_list is None:
            #select Name Column
            corpus1_columnsFromDf = st.session_state['corpus1_df'].columns.values
            st.multiselect(label = 'โปรดเลือกคอลัมน์ ที่ต้องการจะเก็บไว้',options = corpus1_columnsFromDf,default = corpus1_columnsFromDf,key = 'corpus1_col_list_select_box')
            corpus1_selected_col_list_button = st.button('Next',on_click = corpus1_SelectCol_list_click,key = 's_col_button')

        if st.session_state.corpus1_namecolname is not None and st.session_state.corpus1_selected_col_list is not None:
            pm_images = Image.open('material/images/app2_pm.jpg')
            with st.expander("คำอธิบายเพิ่มเติมสำหรับ Partial Name Matching"):
                st.write('การทำ Partial Name Matching จะหมายถึงเลือกทำเพียงแค่บางส่วน')
                st.write('เช่น ต้องการเลือกทำ Name Matching บน Class == "firm_th" เท่านั้น')
                st.image(pm_images)

            corpus1_partialnm_box = st.checkbox('ต้องการทำ Partial Name Matching')
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
            # Merge IPI?
            if not st.session_state['corpus1_use_ipi']:
                corpus1_merge_ipi_box = st.checkbox('ต้องการทำ Merge IPI?')
                if corpus1_merge_ipi_box:
                    corpus1_ColName_box_list = [None]
                    corpus1_ColName_box_list.extend(st.session_state.corpus1_df.columns)
                    l_corpus1,right_corpus1 = st.columns(2)
                    with l_corpus1:
                        st.subheader('Please Select Necessary Column')
                        st.selectbox('RID Columns',options = corpus1_ColName_box_list,key = 'corpus1_RID_CN')
                        st.selectbox('NAME',options = corpus1_ColName_box_list,key = 'corpus1_Name_CN')

            submit_button1 = st.button('Submit',key = 'submit_c1',on_click = corpus1_submit)

if st.session_state.corpus1_input == True and st.session_state.app2_input == False:
    st.divider()
    st.header('Step 2.1: Dataset ที่ต้องการจะ Matching ด้วย',divider= 'orange')
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
        
    if st.session_state.add_corpus2 == False:
        col1,col2 = st.columns([1,0.2])
        with col1:
            corpus2_add = st.button('Add More to be Matched Dataset?',on_click = click_add_corpus2,key = 'corpus2_add')
        with col2:
            next_button1 = st.button('Next',on_click = click_to_NM,key = 'next_button1')

#################################################################################################### 2.1 Corpus Input ####################################################################################################

if 'corpus2_input' not in st.session_state:
    st.session_state.corpus2_input = False
    st.session_state.corpus2_cache  = False
    st.session_state['uploaded_corpus2'] = False
    st.session_state['corpus2_use_ipi'] = False
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
    # add corpus
    st.session_state.add_corpus3 = False

def corpus2_SelectCol_click():
    st.session_state.corpus2_namecolname = load_in(st.session_state.corpus2_namecol_select_box)

def corpus2_SelectCol_list_click():
    st.session_state.corpus2_selected_col_list = load_in(st.session_state.corpus2_col_list_select_box)
    st.session_state.corpus2_df = load_in(st.session_state.corpus2_df.filter(st.session_state.corpus2_selected_col_list))

def corpus2_click_use_ipi():
    st.session_state['corpus2_df'] = st.session_state['ipi_df'].copy()
    st.session_state['uploaded_corpus2'] = True
    st.session_state['corpus2_use_ipi'] = True

def corpus2_submit():
    st.session_state.corpus2_partial_nm  = load_in(corpus2_partialnm_box)
    
    # adjust query
    st.session_state.query2_filter_option_out = load_in(st.session_state.query2_filter_option)
    if st.session_state.query2_filter_choices is not None:
        st.session_state.query2_filter_choices_out = load_in(st.session_state.query2_filter_choices)
    elif st.session_state.query2_filter_range is not None:
        st.session_state.query2_filter_range_out = load_in(st.session_state.query2_filter_range)
    
    if st.session_state.query2_filter_option_out is not None:
        st.session_state.adjust_query2 = load_in(True)
        if bool(re.search('num|float|int',query2_type_string)):
            st.session_state.query2_filter_option_dtype = load_in('numeric')
        else:
            st.session_state.query2_filter_option_dtype = load_in('object')
    
    if st.session_state.query2_filter_choices_out is not None:
        st.session_state.query2_filter_condition = load_in(st.session_state.query2_filter_choices_out)
    elif st.session_state.query2_filter_range_out is not None:
        st.session_state.query2_filter_condition = load_in(st.session_state.query2_filter_range_out)
    
    # input file_name
    st.session_state.corpus2_file_name = 'data2'
    # if not st.session_state['corpus2_use_ipi']:
    #     st.session_state.corpus2_file_name = load_in(re.sub('\\.csv','',corpus2_upload.name))
    # else:
    #     st.session_state.corpus2_file_name = load_in('IPI_DATASET')
    st.session_state.corpus2_df = st.session_state.corpus2_df.reset_index(drop = True).reset_index()
    st.session_state.corpus2_df = load_in(st.session_state.corpus2_df.rename(columns = {'index':'corpus_index'}))

    # Merge IPI Session
    if not st.session_state['corpus2_use_ipi']:
        if corpus2_merge_ipi_box:
            st.session_state['corpus2_RID_CN']
            st.session_state['corpus2_Name_CN']
            st.session_state['corpus2_df'][st.session_state['corpus2_RID_CN']] = st.session_state['corpus2_df'][st.session_state['corpus2_RID_CN']].astype(str).str.zfill(13)
            r_df = st.session_state['corpus2_df'].merge(st.session_state['ipi_df'].rename(columns = {'SRC_UNQ_ID':st.session_state['corpus2_RID_CN']}),
                                                        on = st.session_state['corpus2_RID_CN'],
                                                        how = 'left')
            r_df['SCORE'] = r_df.apply(lambda row: fuzz.ratio(row[st.session_state['corpus2_Name_CN']],row['RGST_BSN_NM_THAI']),axis = 1)
            r_df['SIMP_SCORE'] = r_df.apply(lambda row : fuzz.ratio(simplify_name(row[st.session_state['corpus2_Name_CN']],soft_simp_words),
                                                    simplify_name(row['RGST_BSN_NM_THAI'],soft_simp_words)),axis = 1)
            r_keep_col = [st.session_state['corpus2_RID_CN'],'RGST_BSN_NM_THAI','SNA 2008']
            st.session_state['corpus2_df'] = st.session_state['corpus2_df'].merge(r_df.query('SIMP_SCORE >= 60.1 & SCORE >= 26').filter(r_keep_col),how = 'left')

    st.session_state.corpus2_input = True
    print(st.session_state.corpus2_input)

def click_add_corpus3():
    st.session_state.add_corpus3 = True


#################################################################################################### 2.2 Corpus Input ####################################################################################################
if st.session_state.query_input == True and st.session_state.corpus2_input == False and st.session_state.add_corpus2 and st.session_state.app2_input == False:
    st.divider()
    st.header('Step 2.2: เพิ่ม Dataset ที่ต้องการจะ Matching',divider= 'orange')
    
    if st.session_state['uploaded_corpus2'] == False:
        corpus2_upload = st.file_uploader("Choose a file to upload",key = 'corpus2_upload')
        if corpus2_upload is not None:
            if st.session_state.corpus2_cache == False:
                st.session_state.corpus2_df = read_upload_data(corpus2_upload)
                st.session_state.corpus2_cache = True
                st.session_state['uploaded_corpus2'] = True

    if not st.session_state['corpus2_use_ipi']:
        corpus2_use_ipi_checkbox = st.checkbox('Use IPI Dataset')
        if corpus2_use_ipi_checkbox:
            st.button('Name Matching with IPI Dataset',key = 'corpus2_use_nm_ipi',on_click = corpus2_click_use_ipi)
    
    if st.session_state.corpus2_df is not None:
        #st.subheader('This is Your Corpus Dataset')
        conditional_st_write_df(st.session_state.corpus2_df)
        st.write(f'{st.session_state.corpus2_df.shape[0]} rows , {st.session_state.corpus2_df.shape[1]} columns')

        if st.session_state.corpus2_namecolname is None:
            #select Name Column
            corpus2_namecol_box = [None]
            corpus2_namecol_box.extend(st.session_state.corpus2_df.columns)
            corpus2_namecol_option = st.selectbox('Which is Names Column ?',corpus2_namecol_box,key = 'corpus2_namecol_select_box')
            if st.session_state['corpus2_namecol_select_box'] is not None:
                corpus2_selected_namecol = st.button('Next',on_click = corpus2_SelectCol_click)
        
        if st.session_state.corpus2_namecolname is not None and st.session_state.corpus2_selected_col_list is None:
            #select Name Column
            corpus2_columnsFromDf = st.session_state['corpus2_df'].columns.values
            st.multiselect(label = 'Please Select Column to Keep',options = corpus2_columnsFromDf,default = corpus2_columnsFromDf,key = 'corpus2_col_list_select_box')
            #st_tags(value = corpus2_columnsFromDf ,suggestions = corpus2_columnsFromDf ,label = '', text = '',key = 'corpus2_col_list_select_box')
            corpus2_selected_col_list_button = st.button('Next',on_click = corpus2_SelectCol_list_click,key = 's_col_button')

        if st.session_state.corpus2_namecolname is not None and st.session_state.corpus2_selected_col_list is not None:
            pm_images = Image.open('material/images/app2_pm.jpg')
            with st.expander("คำอธิบายเพิ่มเติมสำหรับ Partial Name Matching"):
                st.write('การทำ Partial Name Matching จะหมายถึงเลือกทำเพียงแค่บางส่วน')
                st.write('เช่น ต้องการเลือกทำ Name Matching บน Class == "firm_th" เท่านั้น')
                st.image(pm_images)

            corpus2_partialnm_box = st.checkbox('ต้องการทำ Partial Name Matching')
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
            
            # Merge IPI?
            if not st.session_state['corpus2_use_ipi']:
                corpus2_merge_ipi_box = st.checkbox('ต้องการทำ Merge IPI?')
                if corpus2_merge_ipi_box:
                    corpus2_ColName_box_list = [None]
                    corpus2_ColName_box_list.extend(st.session_state.corpus2_df.columns)
                    l_corpus2,right_corpus2 = st.columns(2)
                    with l_corpus2:
                        st.subheader('Please Select Necessary Column')
                        st.selectbox('RID Columns',options = corpus2_ColName_box_list,key = 'corpus2_RID_CN')
                        st.selectbox('NAME',options = corpus2_ColName_box_list,key = 'corpus2_Name_CN')
            
            submit_button2 = st.button('Submit',key = 'submit_c2',on_click = corpus2_submit)

if st.session_state.corpus2_input == True and st.session_state.app2_input == False:
    st.divider()
    st.header('Step 2.2: เพิ่ม Dataset ที่ต้องการจะ Matching')
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

    if st.session_state.add_corpus3 == False:
        col1,col2 = st.columns([1,0.2])
        with col1:
            corpus2_add = st.button('Add More to be Matched Dataset?',on_click = click_add_corpus3,key = 'corpus2_add')
        with col2:
            next_button2 = st.button('Next',on_click = click_to_NM,key = 'next_button2')
#################################################################################################### 2.2 Corpus Input ####################################################################################################

if 'corpus3_input' not in st.session_state:
    st.session_state.corpus3_input = False
    st.session_state.corpus3_cache  = False
    st.session_state['uploaded_corpus3'] = False
    st.session_state['corpus3_use_ipi'] = False
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

def corpus3_SelectCol_click():
    st.session_state.corpus3_namecolname = load_in(st.session_state.corpus3_namecol_select_box)

def corpus3_SelectCol_list_click():
    st.session_state.corpus3_selected_col_list = load_in(st.session_state.corpus3_col_list_select_box)
    st.session_state.corpus3_df = load_in(st.session_state.corpus3_df.filter(st.session_state.corpus3_selected_col_list))

def corpus3_click_use_ipi():
    st.session_state['corpus3_df'] = st.session_state['ipi_df'].copy()
    st.session_state['uploaded_corpus3'] = True
    st.session_state['corpus3_use_ipi'] = True

def corpus3_submit():
    st.session_state.corpus3_partial_nm  = load_in(corpus3_partialnm_box)
    
    # adjust query
    st.session_state.query3_filter_option_out = load_in(st.session_state.query3_filter_option)
    if st.session_state.query3_filter_choices is not None:
        st.session_state.query3_filter_choices_out = load_in(st.session_state.query3_filter_choices)
    elif st.session_state.query3_filter_range is not None:
        st.session_state.query3_filter_range_out = load_in(st.session_state.query3_filter_range)
    
    if st.session_state.query3_filter_option_out is not None:
        st.session_state.adjust_query3 = load_in(True)
        if bool(re.search('num|float|int',query3_type_string)):
            st.session_state.query3_filter_option_dtype = load_in('numeric')
        else:
            st.session_state.query3_filter_option_dtype = load_in('object')
    
    if st.session_state.query3_filter_choices_out is not None:
        st.session_state.query3_filter_condition = load_in(st.session_state.query3_filter_choices_out)
    elif st.session_state.query3_filter_range_out is not None:
        st.session_state.query3_filter_condition = load_in(st.session_state.query3_filter_range_out)
    
    # input file_name
    st.session_state.corpus3_file_name = 'data3'
    # if not st.session_state['corpus3_use_ipi']:
    #     st.session_state.corpus3_file_name = load_in(re.sub('\\.csv','',corpus3_upload.name))
    # else:
    #     st.session_state.corpus3_file_name = load_in('IPI_DATASET')
    st.session_state.corpus3_df = st.session_state.corpus3_df.reset_index(drop = True).reset_index()
    st.session_state.corpus3_df = load_in(st.session_state.corpus3_df.rename(columns = {'index':'corpus_index'}))

    # Merge IPI Session
    if not st.session_state['corpus3_use_ipi']:
        if corpus3_merge_ipi_box:
            st.session_state['corpus3_RID_CN']
            st.session_state['corpus3_Name_CN']
            st.session_state['corpus3_df'][st.session_state['corpus3_RID_CN']] = st.session_state['corpus3_df'][st.session_state['corpus3_RID_CN']].astype(str).str.zfill(13)
            r_df = st.session_state['corpus3_df'].merge(st.session_state['ipi_df'].rename(columns = {'SRC_UNQ_ID':st.session_state['corpus3_RID_CN']}),
                                                        on = st.session_state['corpus3_RID_CN'],
                                                        how = 'left')
            r_df['SCORE'] = r_df.apply(lambda row: fuzz.ratio(row[st.session_state['corpus3_Name_CN']],row['RGST_BSN_NM_THAI']),axis = 1)
            r_df['SIMP_SCORE'] = r_df.apply(lambda row : fuzz.ratio(simplify_name(row[st.session_state['corpus3_Name_CN']],soft_simp_words),
                                                    simplify_name(row['RGST_BSN_NM_THAI'],soft_simp_words)),axis = 1)
            r_keep_col = [st.session_state['corpus3_RID_CN'],'RGST_BSN_NM_THAI','SNA 2008']
            st.session_state['corpus3_df'] = st.session_state['corpus3_df'].merge(r_df.query('SIMP_SCORE >= 60.1 & SCORE >= 26').filter(r_keep_col),how = 'left')

    st.session_state.corpus3_input = True
    print(st.session_state.corpus3_input)

#################################################################################################### 2.3 Corpus Input ####################################################################################################
if st.session_state.query_input == True and st.session_state.corpus3_input == False and st.session_state.add_corpus3 and st.session_state.app2_input == False:
    st.divider()
    st.header('Step 2.3: เพิ่ม Dataset ที่ต้องการจะ Matching',divider= 'orange')
    
    if st.session_state['uploaded_corpus3'] == False:
        corpus3_upload = st.file_uploader("Choose a file to upload",key = 'corpus3_upload')
        if corpus3_upload is not None:
            if st.session_state.corpus3_cache == False:
                st.session_state.corpus3_df = read_upload_data(corpus3_upload)
                st.session_state.corpus3_cache = True
                st.session_state['uploaded_corpus3'] = True

    if not st.session_state['corpus3_use_ipi']:
        corpus3_use_ipi_checkbox = st.checkbox('Use IPI Dataset')
        if corpus3_use_ipi_checkbox:
            st.button('Name Matching with IPI Dataset',key = 'corpus3_use_nm_ipi',on_click = corpus3_click_use_ipi)
    
    if st.session_state.corpus3_df is not None:
        #st.subheader('This is Your Corpus Dataset')
        conditional_st_write_df(st.session_state.corpus3_df)
        st.write(f'{st.session_state.corpus3_df.shape[0]} rows , {st.session_state.corpus3_df.shape[1]} columns')

        if st.session_state.corpus3_namecolname is None:
            #select Name Column
            corpus3_namecol_box = [None]
            corpus3_namecol_box.extend(st.session_state.corpus3_df.columns)
            corpus3_namecol_option = st.selectbox('Which is Names Column ?',corpus3_namecol_box,key = 'corpus3_namecol_select_box')
            if st.session_state['corpus3_namecol_select_box'] is not None:
                corpus3_selected_namecol = st.button('next',on_click = corpus3_SelectCol_click)
        
        if st.session_state.corpus3_namecolname is not None and st.session_state.corpus3_selected_col_list is None:
            #select Name Column
            corpus3_columnsFromDf = st.session_state['corpus3_df'].columns.values
            st.multiselect(label = 'Please Select Column to Keep',options = corpus3_columnsFromDf,default = corpus3_columnsFromDf,key = 'corpus3_col_list_select_box')
            #st_tags(value = corpus3_columnsFromDf ,suggestions = corpus3_columnsFromDf ,label = '', text = '',key = 'corpus3_col_list_select_box')
            corpus3_selected_col_list_button = st.button('next',on_click = corpus3_SelectCol_list_click,key = 's_col_button')

        if st.session_state.corpus3_namecolname is not None and st.session_state.corpus3_selected_col_list is not None:
            pm_images = Image.open('material/images/app2_pm.jpg')
            with st.expander("คำอธิบายเพิ่มเติมสำหรับ Partial Name Matching"):
                st.write('การทำ Partial Name Matching จะหมายถึงเลือกทำเพียงแค่บางส่วน')
                st.write('เช่น ต้องการเลือกทำ Name Matching บน Class == "firm_th" เท่านั้น')
                st.image(pm_images)

            corpus3_partialnm_box = st.checkbox('ต้องการทำ Partial Name Matching')
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
            
            # Merge IPI?
            if not st.session_state['corpus3_use_ipi']:
                corpus3_merge_ipi_box = st.checkbox('ต้องการทำ Merge IPI?')
                if corpus3_merge_ipi_box:
                    corpus3_ColName_box_list = [None]
                    corpus3_ColName_box_list.extend(st.session_state.corpus3_df.columns)
                    l_corpus3,right_corpus3 = st.columns(2)
                    with l_corpus3:
                        st.subheader('Please Select Necessary Column')
                        st.selectbox('RID Columns',options = corpus3_ColName_box_list,key = 'corpus3_RID_CN')
                        st.selectbox('NAME',options = corpus3_ColName_box_list,key = 'corpus3_Name_CN')
            
            submit_button3 = st.button('Submit',key = 'submit_c3',on_click = corpus3_submit)

if st.session_state.corpus3_input == True and st.session_state.app2_input == False:
    st.divider()
    st.header('Step 2.3: เพิ่ม Dataset ที่ต้องการจะ Matching')
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

    # Next
    col1,col2 = st.columns([1,0.2])
    with col2:
        next_button2 = st.button('Next',on_click = click_to_NM,key = 'next_button2')

#################################################################################################### 2.3 Corpus Input ####################################################################################################



#################################################################################################### 3. Text-Preprocess ####################################################################################################
if 'params_text_preprocess_regex' not in st.session_state:
    st.session_state['params_text_preprocess_regex'] = None
    st.session_state['params_upload_regex'] = False
    st.session_state['params_matching_rules'] = None

if 'app2_double_prep' not in st.session_state:
    st.session_state['app2_double_prep'] = False

if 'app2_textprocess' not in st.session_state:
    st.session_state.app2_textprocess = False
    st.session_state.app2_textprocess_regex_list = False
    st.session_state.app2_default_regex_list = copy.deepcopy(default_regex_list)
    st.session_state.app2_developer_regex_list = copy.deepcopy(soft_simp_words)
    st.session_state.app2_developer_regex_listV2 = copy.deepcopy(hard_simp_words)
    st.session_state.app2_regex_listV1 = None
    st.session_state.app2_regex_listV2 = None
    st.session_state['uploaded_regex'] = None

def submit_textpreprocess_regex():
    st.session_state.app2_textprocess_regex_list = load_in(regex_tags)
    st.session_state.app2_textprocess  = True


if (st.session_state.app2_input == True) and (st.session_state.app2_textprocess == False) :
    st.header("1. Text Preprocess",divider= 'blue')
    st.write('ขั้นตอนการทำ Text Preprocess จะทำการลบ Keywords (Regex) ดังกล่าวออกจากชื่อผู้ถือหุ้นทั้งหมด')
    st.code('name = "บริษัท เคอรี่โลจิสติกส์ จำกัด" \nRegex = ["บริษัท","จำกัด","มหาชน"]')
    st.write('จุดประสงค์หลักคือ :orange[ต้องการลบพวก common words ออกจากชื่อบริษัท] เพื่อทำให้ Name Matching เจอได้ง่ายขึ้น')
    st.code('TextPreprocess(name) -> "เคอรี่โลจิสติกส์"')
    st.divider()
    st.subheader('กรุณากำหนด Text Preprocess Regex')
    regex_section = st.empty()
    with regex_section.container():
        container = st.container()
        container2 = st.container()
        st.radio(label = '',options = ['Suggested set of Keywords',
                                    'Suggested set of Keywords (II.)',
                                    'Customize your own Keywords',
                                    'Upload'],
                            captions = ['เป็นคำ Common Words ของบริษัททำให้สามารถ Name Matching เจอง่ายขึ้น',
                                        "เป็นคำ Common Words ของบริษัทที่จะ More Specific Business ทำให้สามารถ Name Matching เจอง่ายขึ้น",
                                        'ปรับแต่ง Keywords เองทั้งหมด',
                                        ''], 
                                        index = 0,key = 'user_textprep_regex_choices',label_visibility= 'collapsed')
        
        if st.session_state['user_textprep_regex_choices'] == "Suggested set of Keywords":
            regex_tags = st_tags(label = '',value = st.session_state.app2_developer_regex_list,text = 'soft_simplify',maxtags= -1)
        elif st.session_state['user_textprep_regex_choices'] == "Suggested set of Keywords (II.)":
            regex_tags = st_tags(label = 'Text Preprocess II.',value = st.session_state.app2_developer_regex_listV2,text = 'hard_simplify',maxtags= -1)
        elif st.session_state['user_textprep_regex_choices'] == "Customize your own Keywords":
            regex_tags = st_tags(label = '',value = st.session_state.app2_default_regex_list,text = 'customize',maxtags = -1)
        elif st.session_state['user_textprep_regex_choices'] == "Upload":
            regex_upload = st.file_uploader("Choose a file to upload",key = 'corpus3_upload')
            if regex_upload is not None:
                regex_df = read_upload_data(regex_upload)
                st.session_state['uploaded_regex'] = regex_df[regex_df.columns[0]].values.tolist()
            
            if st.session_state['uploaded_regex'] is not None:
                regex_tags = st_tags(label = '',value = st.session_state['uploaded_regex'],text = 'customize',maxtags = -1)


    ### submit to next-step        
    l1,r1 = st.columns([12,5])       
    r1.button("กดเพื่อเริ่ม Name Matching",key = 'regex_customize_submit_button',on_click=submit_textpreprocess_regex)


#################################################################################################### 3. Text-Preprocess ####################################################################################################

#################################################################################################### 4. Name Matching ####################################################################################################

@st.cache_data
def adjust_dataset(query_df,corpus_df,
                   adjust_query,query_filter,query_filter_dtype,query_filter_condition):
    final_query_df = query_df.copy()
    final_corpus_df = corpus_df.copy()
    # if adjust query dataset
    if adjust_query:
        if query_filter_dtype == 'object':
            final_query_df = final_query_df[final_query_df[query_filter].isin(query_filter_condition)]
        elif query_filter_dtype == 'numeric':
            final_query_df = final_query_df[final_query_df[query_filter] >= query_filter_condition[0]]
            final_query_df = final_query_df[final_query_df[query_filter] <= query_filter_condition[1]]

    # return processed dataset
    return final_query_df,final_corpus_df

# @st.cache_data
# def name_matching(df_query,query_colname,df_corpus,corpus_colname,regex_list):
#     # preprocess-by Regex
#     query_names,corpus_names = text_preprocess_byRegex(df_query,query_colname,
#                                                 df_corpus,corpus_colname,
#                                                 regex_list = regex_list)
#     # prepro data for NM
#     syn_df_query,syn_df_corpus = wrap_up_material(df_query,df_corpus,
#                                           query_names,corpus_names)
#     # NM 
#     matched_df = extract_NM(syn_df_query,syn_df_query.query_name,query_colname,
#                             syn_df_corpus,syn_df_corpus.corpus_name,corpus_colname)
    
#     return matched_df

@st.cache_data
def batch_request_NameMatching(query_df,query_name_colname,corpus_df,corpus_nmame_colname,regex_list,fold = 10):
    port = 5002
    api_route = 'name_matching'
    
    total_matched_df = pd.DataFrame()
    query_df_ = query_df.copy()
    query_df_ = query_df_.drop_duplicates(query_name_colname).reset_index()
    query_df_.rename(columns = {'index':'query_index'},inplace = True)
    Whole_df = np.array_split(query_df_,fold)
    for samp_df in stqdm(Whole_df):
        post_data = {
            'query_df' : samp_df.fillna(0).to_dict(orient= 'list'),
            'query_name_colname' : query_name_colname,
            'corpus_df' : corpus_df.fillna(0).to_dict(orient= 'list'),
            'corpus_name_colname' : corpus_nmame_colname,
            'textprocess_regex_list': regex_list
        }

        res = requests.post(f'http://127.0.0.1:{port}/{api_route}', json = post_data)
        if res.status_code == 201:
            result_df = pd.json_normalize(res.json()['matched_df'])
            print(result_df)
            sorted_col = ['query_name','corpus_name','tfidf_score','fuzzy_ratio','fuzzy_partialratio',query_name_colname,corpus_nmame_colname]
            result_df = result_df.filter(sorted_col)
            if len(result_df) > 0:
                total_matched_df = pd.concat([total_matched_df,result_df])
                print(total_matched_df)
    return total_matched_df.reset_index(drop = True)


if st.session_state.app2_textprocess and st.session_state.app2_preprocessNM == False:
    if 't_start' not in st.session_state:
        st.session_state['t_start'] = time.time()
        
    st.header("2. Name Matching",divider = 'blue')
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
                            st.session_state[f'query{c}_filter_option_dtype'],st.session_state[f'query{c}_filter_condition'])

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

            # st.write(st.session_state['final_query_df']) #query df
            # st.write(st.session_state['final_query_colname']) # name
            # st.write(st.session_state['final_corpus_df'])# corpus df
            # st.write(st.session_state['final_corpus_colname']) # name_data1
            # st.write(st.session_state.app2_textprocess_regex_list)
            # Process Name Matching
            # matched_df = name_matching(st.session_state['final_query_df'],st.session_state['final_query_colname'],
            #                     st.session_state['final_corpus_df'],st.session_state['final_corpus_colname'],
            #                     regex_list = st.session_state.app2_textprocess_regex_list)
            
            m_info = st.empty()
            m_info.info("Process : Name Matching ")
            matched_df = batch_request_NameMatching(st.session_state['final_query_df'],st.session_state['final_query_colname'],
                                                    st.session_state['final_corpus_df'],st.session_state['final_corpus_colname'],
                                                    regex_list = st.session_state.app2_textprocess_regex_list)
            m_info.empty()                            
            
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
if st.session_state.app2_preprocessNM and st.session_state['app2_output'] is None:
    ## Interactive session
    st.header('2. Name Matching',divider = 'blue')
    st.subheader("2.1 กรุณากำหนด :orange[Matching Rules]")
    st.caption("สามารถปรับแต่ง Score ต่างๆ และเพิ่ม Rule ด้านล่างเพื่อ Match ชื่อ")

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
        agree2 = st.checkbox('adjust Fuzzy Score')
    with col4:
        if agree2:
            st.session_state.fuzzy_checkbox = False
        else:
            st.session_state.fuzzy_checkbox = True

        st.slider(label = 'fuzzy_score >= ',min_value = 0,max_value =  100,value =  70, step = 1,
                    key = 'Fuzzy_Ratio',disabled = st.session_state.fuzzy_checkbox)
        print(st.write(st.session_state.Fuzzy_Ratio))

    col5,col6 = st.columns(2)
    with col5:
        agree3 = st.checkbox('adjust Fuzzy Partial Score')
    with col6:
        if agree3:
            st.session_state.fuzzy_partial_checkbox = False
        else:
            st.session_state.fuzzy_partial_checkbox = True

        st.slider(label = 'fuzzy_partial_score >= ',min_value = 0,max_value =  100,value =  70, step = 1,
                    key = 'Fuzzy_Partial_Ratio',disabled = st.session_state.fuzzy_partial_checkbox)
        print(st.write(st.session_state.Fuzzy_Partial_Ratio))

    if st.session_state.app2_double_prep:
        agree4 = st.checkbox('only text_process 1')
        agree5 = st.checkbox('only text_process 2')

    index = np.where([agree,agree2,agree3])[0]
    display = np.array(['tfidf_score','fuzzy_ratio','fuzzy_partialratio']) # ค่อยมาเปลี่ยนเป็น score เดี๋ยวมันจะพังเอา
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
                
    Thresh_List = st_tags(label = '',value = st.session_state.app2_possible_threshold_list,text = '')
    st.caption("*หมายเหตุ: เป็น OR Condition ซึ่งจะ Apply ใช้ทุก Rules เพื่อใช้ Confirm ว่าสองชื่อดังกล่าว Matched")
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
    st.subheader("ตรวจเช็ค  :orange[ชื่อที่มีความเป็นไปได้ว่าจะ Matched]")
    with st.expander('Candidate Matched Name'):
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
                st.write('ผลลัพธ์ของแต่ละ Dataset ที่ต้องการ Matching')
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
                st.write('ผลลัพธ์ของแต่ละ Dataset ที่ต้องการ Matching')
            with col2:
                st.button('1',on_click = click_read_df1,key = 'read1')
            with col3:
                st.button('2',on_click= click_read_df2,key = 'read2')
        

    if st.session_state.processThreshold and st.session_state['app2_output'] is None:
        #st.info('Processing NM')
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

            c += 1
        # duplicate each corpus (sort by number) to get total matched
        query_matched_results = st.session_state['query_df'].merge(query_mat.drop_duplicates(st.session_state['query_namecolname']),\
                                        on = st.session_state['query_namecolname'],how = 'left')#.drop('query_index',axis = 1)
        st.session_state['query_matched_results'] = query_matched_results
        st.session_state.processThreshold = False
    
    
    # show results
    if st.session_state['query_matched_results'] is not None and st.session_state['app2_output'] is None:
        st.header("3. Matched Results",divider = 'green')
        #total_matched_len = len(nm_matched)
        print(len(st.session_state.query_df))
        total_matched_len = len(st.session_state['query_matched_results'].dropna(subset = 'MATCHED_NAME'))
        matched_percent = np.round(total_matched_len/len(st.session_state.query_df)* 100,1)
        st.success(f'สามารถ Match ได้ :green[{matched_percent}%] จากทั้งหมด', icon="✅")
        st.write(f'เป็นจำนวน {total_matched_len} ชื่อ จากทั้งหมด {len(st.session_state.query_df)}')
        st.caption('หมายเหตุ: ผลสามารถเป็นได้ทั้ง False Positive/Negative ไม่ใช่เป็นการ Confirm Matched')
        #st.write(st.session_state['query_matched_results'])
        conditional_st_write_df(st.session_state['query_matched_results'])
        # Took Time
        t_end = time.time()
        took_time = np.round((t_end - st.session_state['t_start'] )/60,2)
        st.write(f'ใช้เวลาในการรันทั้งหมด {took_time} นาที')
    # if 't_end' not in st.session_state:
    #     st.session_state.t_end = time.time()
    #     st.write(st.session_state.t_end - st.session_state.t_zero)
    #     print(st.session_state.t_end - st.session_state.t_zero)

#################################################################### Tidy Results ####################################################################

def export_to_Extension():
    st.session_state['app2_output'] = load_in(st.session_state['query_matched_results'])
    # send params
    st.session_state['params_matching_rules'] = copy.deepcopy(Thresh_List)
    st.session_state['params_text_preprocess_regex'] = copy.deepcopy(st.session_state['app2_textprocess_regex_list'])
    if st.session_state['uploaded_regex'] is not  None:
        st.session_state['params_upload_regex'] = True

if st.session_state.app2_preprocessNM and st.session_state['app2_output'] is None:
    st.divider()
    mult_cols = st.columns(4)
    back_col = mult_cols[0]
    next_col = mult_cols[-1]

    with next_col:
        st.button('Go to Assign SNA',on_click = export_to_Extension)

    # <- back button 7
    def back_7():
        st.session_state['app2_input'] = True
        st.session_state['app2_textprocess'] = False
        st.session_state['app2_preprocessNM']  = False
    with back_col:
        st.button('Back',key = 'back_7',on_click = back_7)
        
    
if st.session_state['app2_output'] is not None:
    st.header("4.Final Results",divider = 'green')
    def combinder(candidate,dataframe):
        df = dataframe.copy()
        candidate_verify = np.array(candidate)[np.isin(candidate,df.columns.values)]
        if len(candidate_verify) > 0:
            if len(candidate_verify) == 1:
                result_values = df[candidate_verify[0]].values.tolist()
            else:
                c = 0
                for cand in candidate_verify:
                    if c == 0:
                        result_values = df[cand].values
                        c += 1
                    else:
                        result_values = [y if pd.isna(x) else x for x,y in list(zip(result_values,df[cand].values))]
        return result_values

    if 'app2_finalize_adjust_column' not in st.session_state:
        st.session_state.app2_finalize_adjust_column = True #init
        st.session_state.app2_finalize_column = False
        st.session_state['app2_finalize_output'] = None

    ##### Add Section
    if 'add_section' not in st.session_state:
        st.session_state.add_section = False
        st.session_state.section_df = pd.DataFrame()
        st.session_state['temporary_df'] = None
        st.session_state['submit_coltoKeep'] = False

    def save_extracolumn(add):
        fake_df = pd.DataFrame({'Name':[add],'Columns':[st.session_state.candidate_col]})
        st.session_state.section_df = pd.concat([st.session_state.section_df,fake_df])

    def submit_section():
        st.session_state['temporary_df'] = st.session_state.app2_output.copy()
        for idx,row in st.session_state['section_df'].iterrows():
            st.session_state['temporary_df'].loc[:,row.Name] = combinder(row.Columns,st.session_state['app2_output'])
        st.session_state.app2_finalize_adjust_column = False
        st.session_state.app2_finalize_column = True
    
    def skip_section():
        st.session_state['temporary_df'] = st.session_state.app2_output.copy()
        st.session_state.app2_finalize_adjust_column = False
        st.session_state.app2_finalize_column = True

    def finalize_column():
        st.session_state['temporary_df'] = load_in(st.session_state['temporary_df'].filter(st.session_state.col_list_select_box))
        st.session_state['submit_coltoKeep'] = True
        st.session_state['app2_finalize_output'] = load_in(st.session_state['temporary_df'])

    def start_finalize():
        st.session_state['app2_finalize_adjust_column'] = True

    if st.session_state.app2_finalize_adjust_column:
        st.write(st.session_state.app2_output)
        st.write(st.session_state.app2_output.shape)
        if st.session_state.add_section == False: 
            with st.container():
                st.subheader('เพิ่ม Column ที่ต้องการรวม')
                add = st.text_input(label = '', placeholder= 'พิมพ์ชื่อคอลัมน์ใหม่และ Enter หลังจากนั้นเลือก Column และกด Add',label_visibility='collapsed')
                comb = st.multiselect(label = '',options = st.session_state.app2_output.columns.values,key = 'candidate_col')
                bt = st.button(label = 'Add',on_click = save_extracolumn, args = ([add]))

        if len(st.session_state.section_df) > 0 :
            st.write(st.session_state.section_df)
            process_button = st.button('Submit',on_click = submit_section)
        else:
            skip_button = st.button('Skip',on_click = skip_section)

        # <- back button 8
        if st.session_state['app2_finalize_output'] is None:
            def back_8():
                st.session_state['app2_output'] = None
                st.session_state['app2_finalize_adjust_column']  = False
            st.button('Back',key = 'back_8',on_click = back_8)

    if st.session_state.app2_finalize_column and st.session_state['app2_finalize_output'] is None:
        
        if st.session_state['temporary_df'] is not None:
            st.write(st.session_state['temporary_df'])
        
        if st.session_state['submit_coltoKeep'] == False:
            columnsFromDf = st.session_state['temporary_df'].columns.values
            st.multiselect(label = 'Please Select Column to Keep',options = columnsFromDf,default = columnsFromDf,key = 'col_list_select_box')
            l9,r9 = st.columns([11,2])
            r9.button('Submit',on_click = finalize_column,key = 's_col_button')
        
        # <- back button 9
        if st.session_state['app2_finalize_output'] is None:
            def back_9():
                st.session_state['app2_finalize_adjust_column'] = True
                st.session_state['add_section'] = False
                st.session_state['app2_finalize_column']  = False
            l9.button('Back',key = 'back_9',on_click = back_9)
    
    # Show Results
    if st.session_state['app2_finalize_output'] is not None:
        st.write(st.session_state['app2_finalize_output'])


######################## Download Final Output ########################
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
    df = st.session_state['app2_finalize_output'].copy()

    params_data_dict = {
    'text_preprocess_regex': [st.session_state['params_text_preprocess_regex']],
    'pupload_regex': [st.session_state['params_upload_regex']],
    'matching_rules': [st.session_state['params_matching_rules']],
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

if st.session_state['app2_finalize_output'] is not None:
    if 'app2_download_file' not in st.session_state:
        st.session_state.app2_download_file  = False

    def click_download():
        st.session_state.app2_download_file = True

    def click_fin_download():
        st.session_state.app2_download_file = False
        st.write('clicked please wait')

    @st.cache_data
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')

    if st.session_state['app2_finalize_output'] is not None:
        #st.divider()
        if len(st.session_state['query_matched_results']) > 0:
            download_but = st.button('Download',on_click = click_download)

    if st.session_state.app2_download_file:
        prompt = False
        submitted = False
        csv = convert_df(st.session_state['app2_finalize_output'])
        # with st.form("my_download_form", clear_on_submit=True):
        #     st.text_input("กรุณาใส่ชื่อไฟล์", key="filename")
        #     submit = st.form_submit_button("Download Data & Params", on_click = download_df)
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
    
# <- back button 10
if st.session_state['app2_finalize_output'] is not None:
    def back_10():
        st.session_state['app2_finalize_output'] = None
        st.session_state['submit_coltoKeep'] = False
    
    def export_app2_output():
        st.session_state['app2_ExportOutput'] = load_in(st.session_state['app2_finalize_output'])

    @st.cache_data
    def Export_ToNext(input_):
        output = copy.deepcopy(input_)
        return output
    
    l_col_10,r_col_10 = st.columns([10,3])
    with l_col_10:
        st.button('Back',key = 'back_10',on_click = back_10)
    with r_col_10:
        to_app3_bt = st.button('To Assign SNA',key = 'to_app3')
        if to_app3_bt:
            st.session_state['app2_ExportOutput'] = Export_ToNext(st.session_state['app2_finalize_output'])
            switch_page('assign sna')
