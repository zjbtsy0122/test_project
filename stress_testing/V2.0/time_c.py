import os
import time
import configparser
import pyautogui

# 写入配置文件，去除空格
def write_config_without_spaces(config, fp):
    for section in config.sections():
        fp.write(f"[{section}]\n")
        for key, value in config.items(section):
            fp.write(f"{key}={value}\n")
    if config.has_section('DEFAULT'):
        fp.write("[DEFAULT]\n")
        for key, value in config['DEFAULT'].items():
            fp.write(f"{key}={value}\n")

# 关闭指定进程
def close_process(process_name):
    os.system(f'taskkill /f /im {process_name}')

# 修改INI文件中的指定选项
def modify_ini_file(file_path, section, option, value):
    config = configparser.ConfigParser(strict=False)
    config.read(file_path, encoding='gbk')
    if config.has_section(section):
        config.set(section, option, str(value).strip())
        with open(file_path, 'w', encoding='gbk') as configfile:
            write_config_without_spaces(config, configfile)
        return value
    else:
        raise Exception(f'未找到节 {section}')

# 启动指定进程
def start_process(process_path):
    pyautogui.hotkey("win", "r")  # 打开运行窗口
    time.sleep(1)
    pyautogui.typewrite(process_path, interval=0.1)  # 输入进程路径
    time.sleep(1)
    pyautogui.press("enter")  # 按下回车键

if __name__ == '__main__':
    cof_path = r'D:\testclient\cof.ini'  # 配置文件路径
    config = configparser.ConfigParser(strict=False)
    config.read(cof_path, encoding='gbk')

    process_name = 'testclient.exe'  # 进程名称
    process_path = config.get('Paths', 'process_path')  # 进程路径
    ini_file_path = config.get('Paths', 'ini_file_path')  # INI文件路径
    section = 'ClientComm_Common'  # 要修改的节
    option = 'deal_second'  # 要修改的选项
    
    # 获取配置中的参数
    start_value = config.getint('Settings', 'start')
    finish_value = config.getint('Settings', 'finish')
    running_time = config.getint('Settings', 'running_time')
    increment = config.getint('Settings', 'increment')
    
    current_value = modify_ini_file(ini_file_path, section, option, start_value)  # 修改INI文件
    loop_count = 1  # 循环计数

    while True:
        print('-' * 30 + 'Info Begin' + '-' * 30)
        start_process(process_path)  # 启动进程
        current_time = time.strftime('%Y年%m月%d日 %H时%M分%S秒', time.localtime())
        print(f"开始时间: {current_time}")
        print(f"压力测试正式开始！'{option}'的当前值为: {current_value} (压测运行次数: {loop_count})")
        time.sleep(running_time)  # 等待运行时间
        close_process(process_name)  # 关闭进程
        current_time = time.strftime('%Y年%m月%d日 %H时%M分%S秒', time.localtime())
        print(f"结束时间: {current_time}")
        print('-' * 30 + 'Info End' + '-' * 32)
        
        current_value += increment  # 增加当前值
        new_value = modify_ini_file(ini_file_path, section, option, current_value)  # 修改INI文件
        loop_count += 1  # 循环计数增加
        
        if new_value > finish_value:  # 检查是否超过结束值
            print(f"新值{new_value}大于finish值：{finish_value}，停止程序。")
            break

    input("程序结束...")
