#!/usr/bin/env python3

import os
import subprocess
import string
import re 
import time

import sys

for arg in sys.argv:
    print(arg)

start_time = time.time()

hostname="BBDSK0566"
#hostname="BBDSK1023"

#cmd='''
#echo "?"
#echo "$(cat /sys/class/dmi/id/product_serial 2>/dev/null)?"  
#echo "$(cat /sys/class/drm/*/edid 2>/dev/null)?" | tr -d "\n\r " 
#echo "$(lsusb && cat /proc/bus/input/devices)"'''

#out = subprocess.run(["sudo", "salt", hostname, "cmd.run",cmd, "--out=json"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#res = str(out.stdout).encode('ascii',errors='ignore').decode('ascii').split("?")

#print("Running this {0}".format(out.args))

full_string=""

text = "VKD44792"
pattern = "^VKD44792"

text = "Lenovo Lenovo Calliope USB"

text = "USB Optical Mouse"

#text = "^Logitech USB Optical Mouse$"

#text  ="^\s*logitech(,?\s+inc\.?)?\s+usb\s+optical\s+mouse\s*$"

#text = r"logitech.*mouse"

#hostname=res[0].replace("\\n", '\n').replace("\\","")
#serial=res[1].replace("\\n", '\n').replace("\\","")
#mon_serial=res[2].replace("\\n", '\n').replace("\\","")
#usb=res[3].replace("\\n", '\n').replace("\\","").splitlines()

#for line in res:
#    if len(line)>0:
        #print((line.replace("\\n", '\n').replace("\\","") + "\n hello"))
#        full_string+=line.replace("\\n", '\n').replace("\\","") + "\n hello"


#print("Hostname:{0}\n,serial:{1}\n,mon_serial:{2}\n,usb:{3}\n".format(hostname,serial,mon_serial,usb))

#it's simple and it's works for product serial and monitor serial matching, doesn't work well for usb stuff
def custom_match(source_str,to_match):
    index = source_str.find(to_match)
    sub_str = source_str[index:index + len(to_match)]
    if to_match.lower() == sub_str.lower():
        return True

    return False 


def custom_line_full_match(source_str, to_match):
    #index = to_match.find(text)
    start_str_usb = "Bus"
    start_str_ps2 = 'N: Name="'
    #bool_res = False
    
    to_match = to_match.split("?")
    for line in source_str:
        #print(line)
        if line.startswith(start_str_usb):
            #only for Bus aka usb info, need to add ps2 support
            array_str = line.split(" ")[6:]
            final_str = " ".join(array_str).strip()
            #print(final_str)
            for string in to_match:#TODO: fix this is slow??
                #print("final_str: {0}, string: {1}".format(final_str.lower(),string.lower().strip()))
                #print(string)
                if final_str.lower() == string.lower().strip(): #hack for deteca and vtalk 
                    #print("[USB]final_str: {0}, string: {1}".format(final_str.lower(),string.lower().strip()))
                    return True

        elif line.startswith(start_str_ps2):
            #for extracting ps2 info
            final_str = line[9:-1]
            #print(final_str)
            for string in to_match:
                if final_str.lower().strip() == string.lower().strip():
                    #print("[PS2]final_str: {0}, string: {1}".format(final_str.lower(),string.lower().strip()))
                    return True
    return False 

#print(custom_line_full_match(usb,text)) 

#TODO add dict mapping to vendor name and usb name. maybe read from a file?

#print(custom_match(text,usb))

#print(repr(text))


class Colors:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RESET = '\033[0m'


def print_color(string, color_str):
    pass
    #print("{0} {1} {2}".format(color_str,string.replace("\n",""),Colors.RESET))


from collections import OrderedDict as od
mouse=od()
keyboard=od()
headset=od()

def process_usb_data(ip_list, mouse: dict, keyboard: dict, headset: dict):
    #mouse,keyboard,headset
    key_mouse = ip_list[0].strip()
    value_mouse = ip_list[1].strip()

    key_keyboard = ip_list[2].strip()
    value_keyboard = ip_list[3].strip()

    key_headset = ip_list[4].strip()
    value_headset = ip_list[5].strip()

    if key_mouse:
        mouse[key_mouse]=value_mouse

    if key_keyboard:
       keyboard[key_keyboard]=value_keyboard

    if key_headset:
        headset[key_headset]=value_headset

    return


def readcsv(csv_filename: str): 
    ret_list = []
    with open(csv_filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            ret_list.append(row)
    return ret_list 


import csv

csv_filename="csvfiles/all_prod_info.csv"

csv_header=['mouse', 'mouse_output', 'keyboard', 'keyboard_output', 'headset', 'headset_output']

usb_data = readcsv(csv_filename)
for row in usb_data:
    if row == csv_header:
        flag = True
    elif flag:
        process_usb_data(row,mouse,keyboard,headset) 
    else:
        print("Error header row is changed: {0}".format(row))
        break

flag = False
'''
print_color(mouse,Colors.RED)
print("\n")

print(Colors.GREEN + str(keyboard) + Colors.RESET)
print("\n")

print( Colors.GREEN + str(headset) + Colors.RESET)
print("\n")
'''
    

#RKH32516APRU
#'BBDSK1086' : ['BB3W470', 'BBDSK1086', 'Assembled', 'BBMON0464', 'CN-0RKH32-72872-516-APRU-A00', 'Logitech', 'Lenovo', 'Voix']

def clean_data(csv_data: list, batch_size: int, cleaned_data: dict, batches: list):
    csv_header=['Bay Number', 'Hostname', 'SERIAL NA', 'Monitor Asset NA', 'Monitor S.NA', 'Keyboard Make', 'Mouse Make', 'Headset Make']

    flag = False
    hostname_str = ""
    i = 0

    for row in csv_data:
        if row == csv_header:
            flag = True
        elif flag:
            #MONITOR Section
            mon_serial=row[4]
            if mon_serial.startswith("CN"):#dell monitor preprocessing
                #can't use straightforward char substring like this (mon_serial[4:9:16]). because the substrings vary in length
                split_str = mon_serial.split("-") 
                if len(split_str) > 1:
                    full_str = ""
                    full_str += split_str[1][1:]
                    full_str += split_str[3]
                    #print(split_str)
                    print(row)
                    full_str += split_str[4]
                    mon_serial = full_str
                    #print(full_str)
                    row[4] = mon_serial
            elif mon_serial.startswith("AOC"): #AOC monitor preprocessing
                mon_serial = mon_serial[3:]
                row[4] = mon_serial
           
            hostname = row[1]
            #print(i,row)
            hostname_str = hostname_str + hostname + ","
            if i == batch_size:
                batches.append(hostname_str)
                hostname_str = ""
                i=0
            
            #write dictionary
            cleaned_data[hostname] = row
            
        else:
            print("From process_hosts Error header row is changed: {0}".format(row))
            break
        i+=1

    flag = False
    #flush out the final batch
    batches.append(hostname_str)
    
csv_filename_asset="my_floor_asset.csv"
data = readcsv(csv_filename_asset)
batch_size = 200
from collections import OrderedDict as od
cleaned_data = od() 
batches = []

#python cannot return multiple values. so just writing to the vars is best
clean_data(data, batch_size, cleaned_data, batches)


cmd='''
echo "?"
lsusb && cat /proc/bus/input/devices
echo "?"
echo "$(cat /sys/class/dmi/id/product_serial 2>/dev/null)?"  
echo "$(cat /sys/class/drm/*/edid 2>/dev/null)?" | tr -cd '\11\12\15\40-\176' 
#echo "$(lsusb && cat /proc/bus/input/devices)" strange bug only one machine had issue running this. possible explanation something to do with /dev/null
#lsusb && cat /proc/bus/input/devices
'''
#TODO: Add matching logic

def match_all(data_from_salt, data_from_sheet):
  
    hostname  = data_from_sheet[1]
    #print(len(data_from_salt))
    #if len(data_from_salt) < 4 :
    #    return f"something went wrong in this hostname {hostname}"     

    #print(data_from_salt)
    '''
    serial    = data_from_salt[1].strip()
    mon_serial= data_from_salt[2].strip()
    usb       = data_from_salt[3].strip()
    '''
   #recent change 
    serial    = data_from_salt[2].strip()
    mon_serial= data_from_salt[3].strip()
    usb       = data_from_salt[1].strip()
    ''' 
    print(serial)
    print(mon_serial)
    print(usb)
    '''
    bay_number= data_from_sheet[0]

    mouse_sheet    = data_from_sheet[6].lower().strip()
    keyboard_sheet = data_from_sheet[5].lower().strip()
    headset_sheet  = data_from_sheet[7].lower().strip()
    
    match_info = ""
    temp = "-------------------------------------------------------START-------------------------------------------------------------\n"
    match_info += temp
    print_color(temp,Colors.CYAN)
    #Product serial matching #DONE
    if data_from_sheet[2].strip().lower() == "assembled":
        temp = "[SKIP   ] Product Serial Check Assembled Hostname: {0}, BayNumber: {1}\n".format(data_from_sheet[1],data_from_sheet[0])
        print_color(temp, Colors.YELLOW)
        match_info += temp
        temp = ""
    elif serial.lower() == data_from_sheet[2].strip().lower():
        temp = "[MATCHED] Product Serial: {0} Hostname: {1}, BayNumber: {2}\n".format(str(serial),data_from_sheet[1],data_from_sheet[0])
        print_color(temp, Colors.GREEN)
        match_info += temp
        temp = ""
    else:
        temp = "[FAILED ] Product Serial Output: {0},From sheet: {1}, Hostname: {2}, BayNumber: {3}\n".format(str(serial),data_from_sheet[2]
,data_from_sheet[1],data_from_sheet[0])
        print_color(temp, Colors.RED)
        match_info += temp
        temp ="" 
    
    #monitor serial matching
    if custom_match(mon_serial,data_from_sheet[4]):
        temp = "[MATCHED] Monitor Serial: {0} Hostname: {1}, BayNumber: {2}\n".format(data_from_sheet[4],data_from_sheet[1],data_from_sheet[0])
        print_color(temp, Colors.GREEN)
        match_info += temp
        temp ="" 
    else:
        temp = "[FAILED ] Monitor Serial Output: {0},From sheet: {1}, Hostname: {2}, BayNumber: {3}\n".format(str(mon_serial),data_from_sheet[4]
,data_from_sheet[1],data_from_sheet[0])
        print_color(temp, Colors.RED)
        match_info += temp
        temp ="" 
 
    #TODO  finish rest of the matching
    #def custom_line_full_match(source_str, to_match):
    
    mouse_flag = False
    keyboard_flag = False 
    headset_flag = False 
    #mouse section
    for key in mouse:
        #print("Key: {0}, Value: {1}".format(key,mouse[key]))
        if custom_line_full_match(usb.splitlines(),mouse[key]):
            mouse_flag = True
            if key.lower().strip()== mouse_sheet:
                temp = "[MATCHED] Mouse {0} in Baynumber: {1}, Hostname: {2}\n".format(key,bay_number,hostname)
                print_color(temp,Colors.GREEN)
                match_info += temp
                temp = ""
            else:
                temp = "[FAILED ] Mouse from machine: {0}, mouse from sheet: {1} in Baynumber: {2}, Hostname: {3}\n".format(key,mouse_sheet,bay_number,hostname)
                print_color(temp, Colors.RED)
                match_info += temp
                temp = ""
 
    for key in keyboard:
        if custom_line_full_match(usb.splitlines(),keyboard[key]):
            keyboard_flag = True
            if str(key).lower().strip() == keyboard_sheet:
                temp = "[MATCHED] keyboard {0} in Baynumber: {1}, Hostname: {2}\n".format(key,bay_number,hostname)
                print_color(temp, Colors.GREEN)
                match_info += temp
                temp = ""
            else:
                temp = "[FAILED ] keyboard from machine: {0}, Keyboard from sheet: {1} in Baynumber: {2}, Hostname: {3}\n".format(key,keyboard_sheet,bay_number,hostname)
                print_color(temp, Colors.RED)
                match_info += temp
                temp = ""
 
    for key in headset:
        if custom_line_full_match(usb.splitlines(),headset[key]):
            if key.lower().strip() == headset_sheet and not headset_flag:
                temp = "[MATCHED] headset {0} in Baynumber: {1}, Hostname: {2}\n".format(key,bay_number,hostname)
                print_color(temp, Colors.GREEN)
                match_info += temp
                temp = ""
            else:
                temp = "[FAILED ] headset from machine: {0}, headset from sheet: {1} in Baynumber: {2}, Hostname: {3}\n".format(key,headset_sheet,bay_number,hostname)
                print_color(temp, Colors.RED)
                match_info += temp
                temp = ""
            headset_flag = True #hack for detecta and vtalk separation
            break
    
    if not mouse_flag:
        temp = "[UNKOWN manufacturer] mouse data from machine: {0}, mouse from sheet: {1} in Baynumber: {2}, Hostname: {3}\n".format(usb,mouse_sheet,bay_number,hostname)
        print_color(temp, Colors.YELLOW)
        match_info += temp
        temp = ""
        mouse_flag = False
    if not keyboard_flag:
        temp = "[UNKOWN manufacturer] keyboard data from machine: {0}, keyboard from sheet: {1} in Baynumber: {2}, Hostname: {3}\n".format(usb,keyboard_sheet,bay_number,hostname)
        print_color(temp, Colors.YELLOW)
        match_info += temp
        temp = ""
        keyboard_flag = False
    if not headset_flag:
        temp = "[UNKOWN manufacturer] headset data from machine: {0}, headset from sheet: {1} in Baynumber: {2}, Hostname: {3}\n".format(usb,headset_sheet,bay_number,hostname)
        print_color(temp, Colors.YELLOW)
        match_info += temp
        temp = ""
        headset_flag = False
     
     #print_color(mon_serial, Colors.BLUE)
    #print_color(usb, Colors.MAGENTA)
    
    temp = "-------------------------------------------------------END---------------------------------------------------------------\n"
    print_color(temp,Colors.CYAN)
    match_info += temp
    temp = ""
    return match_info

def process_hosts(cleaned_data: dict, batches: list, cmd_to_run: str):
   
    connected = 0
    not_connected =0
       #print("Running this {0}".format(out.args))

    #hostname=res[0].replace("\\n", '\n').replace("\\","")
    #serial=res[1].replace("\\n", '\n').replace("\\","")
    #mon_serial=res[2].replace("\\n", '\n').replace("\\","")
    #usb=res[3].replace("\\n", '\n').replace("\\","").splitip_lists()

    for batch in batches:
        out = subprocess.run(["sudo", "salt", "-L",batch,"cmd.run",cmd_to_run, "--out=json"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        #out = subprocess.run(["strings",out.stdout], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        res = str(out.stdout).encode('ascii',errors='ignore').decode('ascii').replace("\\n", '\n').replace("\\","")[2:-2].split("}")
        host_data = [result.replace("{","").replace("}","").split("?") for result in res] 
        
        #print_color(host_data, Colors.CYAN)

        for host in host_data:
            if len(host) > 1:
                hostname = host[0].replace('"',"")[:-2].strip().replace(" ","")
                #print(f"HOSTNAME: {hostname}")
                if hostname:
                    match_info = match_all(host,cleaned_data[hostname])
                    cleaned_data[hostname] = match_info
                    connected +=1
            else:
                #not connected minions
                not_conn = host[0].strip().split(":")[0].replace('"',"")
                temp = "" 
                temp += "-------------------------------------------------------START-------------------------------------------------------------\n"
                if len(not_conn):
                    data_from_sheet = cleaned_data[not_conn]
                    #print_color(cleaned_data[not_conn],Colors.CYAN)
                    temp += "[FAILED ] Not Connected Hostname: {0}, BayNumber: {1} \n".format(data_from_sheet[1],data_from_sheet[0])
                    print_color(temp, Colors.RED)
                    
                    temp += "-------------------------------------------------------END---------------------------------------------------------------\n"
                    cleaned_data[not_conn] = temp
                    not_connected +=1
                    temp = ""
        #break

    return connected,not_connected


import threading 
import time 
import math 
class Term_anim: 
    def __init__(self): 
        self.frames = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏'] 
        self.bool_ = False 
        self.thread = None 
        self.start_time = time.time()
        self.YELLOW = '\033[33m'
        self.CYAN = '\033[36m'
        self.RESET = '\033[0m'
    def spinner(self): 
        while self.bool_: 
            for char in self.frames: 
                if not self.bool_: 
                    break 
                print(f"\r {self.YELLOW} {char} {self.RESET} Elapsed time in Secs since start: {self.CYAN} {math.floor(time.time() - start_time)} {self.RESET}", end="", flush=True) 
                time.sleep(0.1) 
 
    def start(self): 
        if not self.bool_: 
            self.bool_ = True 
            self.thread = threading.Thread(target=self.spinner) 
            self.thread.start() 
 
    def stop(self): 
        self.bool_ = False 
        if self.thread: 
            self.thread.join() 
        print("\r ", end="", flush=True)  # clear spinner 
 

anim = Term_anim()

anim.start()
connected,not_connected = process_hosts(cleaned_data, batches, cmd)
anim.stop()

def print_color_based_on_str(string):
    if string.startswith("[MATCHED]"):
        print("{0} {1} {2}".format(Colors.GREEN,string,Colors.RESET))
    elif string.startswith("[FAILED ]"):
        print("{0} {1} {2}".format(Colors.RED,string,Colors.RESET))
    elif string.startswith("[SKIP   ]"):
        print("{0} {1} {2}".format(Colors.YELLOW,string,Colors.RESET))
    else:
        print("{0} {1} {2}".format(Colors.CYAN,string,Colors.RESET))

import io
data_buffer = io.StringIO()

def dump_string(str_to_write: str, filename: str): 
    with open(filename,"w") as file: 
        file.write(str_to_write) 

for host in cleaned_data:
    data = cleaned_data[host]
    
    data_buffer.write(data)
    for str_ in data.splitlines():
        print_color_based_on_str(str_)

dump_string(data_buffer.getvalue(), "floor_asset_check.log")

import math
end_time = time.time()
elapsed_time = math.floor(end_time - start_time)

#print_color(f"Connected: {connected}, Not Connected: {not_connected}", Colors.CYAN)
print(f"Connected: {connected}, Not Connected: {not_connected}")
if elapsed_time >= 60:
    minutes = math.floor(elapsed_time / 60) #if I remember correctly. it can be written as minutes = (elapsed_time // 60)
    secs = (elapsed_time % 60) 
    print_color_based_on_str(f"Script ran for {minutes} minutes and {secs} seconds.")
else:
    print_color_based_on_str(f"Script ran for {elapsed_time} seconds.")
