import os
import time
import configparser
import subprocess

def close_process(process_name):
    os.system(f'taskkill /f /im {process_name}')

def modify_ini_file(file_path,section,option,increment):
    config = configparser.ConfigParser()
    config.read(file_path,encoding='gbk')

    if config.has_section(section):
        current_value =config.getint(section,option)
        new_value = current_value+increment
        config.set(section,option,str(new_value))


        with open(file_path,'w') as configfile:
            config.write(configfile)
        return new_value
    else:
        raise  Exception(f'Section{section}not found')

def start_process(process_path):
    subprocess.Popen(process_path)

if __name__ == '__main__':
    process_name = 'testclient.exe'
    process_path = r"D:\testclient\testclient.exe"
    ini_file_path ='D:\client.ini'
    section = 'ClientComm_Common'
    option = 'deal_second'
    increment = 100
    while True:
        time.sleep(500)
        close_process(process_name)
        new_value = modify_ini_file(ini_file_path,section,option,increment)
        print(f"New value for'{option}'is:{new_value}")
        start_process(process_path)
        print("testclient.exe has been restarted.")