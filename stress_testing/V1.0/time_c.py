import os
import time
import configparser
import subprocess
import pyautogui

#解决原有方法会存在空格的问题
def write_config_without_spaces(config, fp):
    for section in config.sections():
        fp.write(f"[{section}]\n")
        for key, value in config.items(section):
            fp.write(f"{key}={value}\n")
    # 处理DEFAULT section（如果有的话）
    if config.has_section('DEFAULT'):  # 或者使用 config.defaults() 检查是否有默认选项
        fp.write("[DEFAULT]\n")
        for key, value in config['DEFAULT'].items():
            fp.write(f"{key}={value}\n")

# 关闭指定名称的进程
def close_process(process_name):
    os.system(f'taskkill /f /im {process_name}')

# 修改INI文件中的指定选项
def modify_ini_file(file_path, section, option, increment):
    config = configparser.ConfigParser(strict=False)
    config.read(file_path, encoding='gbk')
    if config.has_section(section):
        current_value = config.getint(section, option)
        new_value = current_value + increment
        config.set(section, option, str(new_value).strip())  # 去掉option和value之间的空格
        with open(file_path, 'w') as configfile:
            write_config_without_spaces(config,configfile)
        return new_value
    else:
        raise Exception(f'未找到节 {section}')

# 启动指定路径的进程
def start_process(process_path):
    pyautogui.hotkey("win", "r")
    time.sleep(1)
    pyautogui.typewrite(process_path, interval=0.1)
    time.sleep(1)
    pyautogui.press("enter")

if __name__ == '__main__':
    cof_path = r'D:\testclient\cof.ini'
    config = configparser.ConfigParser(strict=False)
    config.read(cof_path, encoding='gbk')

    process_name = 'testclient.exe'  # 进程名称
    process_path = config.get('Paths', 'process_path')  # 从INI文件获取进程路径
    ini_file_path = config.get('Paths', 'ini_file_path')  # 从INI文件获取INI文件路径
    section = 'ClientComm_Common'  # INI文件中的节
    option = 'deal_second'  # INI文件中的选项
    finish_value = config.getint('Settings', 'finish')  # 从INI文件获取finish值
    
    sleep_time = config.getint('Settings', 'sleep_time')  # 从INI文件获取睡眠时间
    increment = config.getint('Settings', 'increment')  # 从INI文件获取增量值
    loop_count = 0  # 初始化循环计数器

    while True:
        time.sleep(sleep_time)  # 睡眠指定时间
        close_process(process_name)  # 关闭进程
        new_value = modify_ini_file(ini_file_path, section, option, increment)  # 修改INI文件
        loop_count += 1  # 增加循环计数
        print(f"'{option}'的新值为: {new_value} (循环次数: {loop_count})")  # 显示新值和循环次数
        start_process(process_path)  # 启动进程
        
        # 检查new_value是否与finish值相等
        if new_value == finish_value:
            print("新值与finish值相等，停止程序。")
            break
    print(f"'{option}'的新值为: {new_value} (循环次数: {loop_count})")  # 显示新值和循环次数

    input("程序结束...")  # 添加此行以防止对话框自动关闭
