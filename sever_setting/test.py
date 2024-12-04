import os
import time
import configparser
import subprocess
import pyautogui

# 关闭指定名称的进程
def close_process(process_name):
    os.system(f'taskkill /f /im {process_name}')

# 修改INI文件中的指定选项
def modify_ini_file(file_path, section, option, increment):
    config = configparser.ConfigParser()
    config.read(file_path, encoding='gbk')

    # 检查指定节是否存在
    if config.has_section(section):
        current_value = config.getint(section, option)  # 获取当前值
        new_value = current_value + increment  # 计算新值
        config.set(section, option, str(new_value))  # 设置新值

        # 将修改后的配置写回文件
        with open(file_path, 'w') as configfile:
            config.write(configfile)
        return new_value
    else:
        raise Exception(f'未找到节 {section}')  # 抛出异常

# 启动指定路径的进程
def start_process(process_path):
    pyautogui.hotkey("win", "r")  # 打开运行窗口
    time.sleep(2)
    pyautogui.typewrite(process_path)  # 输入进程路径
    pyautogui.press('enter')  # 按下回车键

if __name__ == '__main__':
    process_name = 'testclient.exe'  # 进程名称
    process_path = input("请输入进程路径: ")  # 用户输入进程路径
    ini_file_path = input("请输入INI文件路径: ")  # 用户输入INI文件路径
    section = 'ClientComm_Common'  # INI文件中的节
    option = 'deal_second'  # INI文件中的选项
    
    sleep_time = int(input("请输入睡眠时间（秒）: "))  # 用户输入睡眠时间
    increment = int(input("请输入增量值: "))  # 用户输入增量值
    
    loop_count = 0  # 初始化循环计数器

    while True:
        time.sleep(sleep_time)  # 睡眠指定时间
        close_process(process_name)  # 关闭进程
        new_value = modify_ini_file(ini_file_path, section, option, increment)  # 修改INI文件
        loop_count += 1  # 增加循环计数
        print(f"'{option}'的新值为: {new_value} (循环次数: {loop_count})")  # 显示新值和循环次数
        time.sleep(10)  # 再次睡眠
        start_process(process_path)  # 启动进程
