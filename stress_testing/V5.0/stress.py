import os
import time
import configparser
import logging
import subprocess
import re


class StressTesting:
    """
    StressTesting类用于执行压力测试，主要功能包括读取配置文件、修改INI文件、启动和关闭测试客户端进程，以及记录测试过程中的日志信息。
    属性:
        SECTIONS (list): 支持的测试节名称，包括 'Login', 'Search', 'Entrust', 'Mix'。
        config (ConfigParser): 配置解析器，用于读取和修改配置文件。
        process_name (str): 测试客户端进程名称。
        process_path (str): 测试客户端进程的完整路径。
        ini_file_path (str): INI文件的路径。
        section (str): 要修改的节名称。
        option1 (str): 要修改的选项1。
        option2 (str): 要修改的选项2。
        option3 (str): 要修改的选项3。
    方法:
        setup_logging(): 设置日志记录，创建日志目录并配置日志文件。
        close_process(): 强制关闭测试客户端进程。
        modify_ini_file(section, option, value): 修改指定INI文件节中的选项值，并去掉等于号两边的空格。
        start_process(): 启动测试客户端进程。
        handle_section(section_name): 处理指定节的配置，获取相关参数并修改INI文件。
        run(): 运行压力测试，循环启动测试客户端并记录测试信息，直到达到结束值。
    """

    SECTIONS = ['Login', 'Search', 'Entrust','Mix']  # 支持的测试节名称

    def __init__(self, cof_path):
        self.config = configparser.ConfigParser(strict=False)  # 创建配置解析器
        self.config.read(cof_path, encoding='gbk')  # 读取配置文件
        self.process_name = 'testclient.exe'  # 测试客户端进程名称
        self.process_path = r'.\testclient.exe'  # 测试客户端进程路径
        self.ini_file_path = r'.\client.ini'  # INI文件路径
        self.section = 'ClientComm_Common'  # 要修改的节
        self.option1 = 'deal_second'  # 要修改的选项1
        self.option2 = 'test_case'  # 要修改的选项2
        self.option3 = 'iswithdrawal'  # 要修改的选项3
        self.setup_logging()  # 设置日志记录

    def setup_logging(self):
        if not os.path.exists('stresslog'):  # 检查日志目录是否存在
            os.makedirs('stresslog')  # 创建日志目录
        log_filename = time.strftime('stresslog/stress_test_%Y%m%d_%H%M%S.log')  # 日志文件名
        logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')  # 配置日志记录


    def close_process(self):
        os.system(f'taskkill /f /im {self.process_name}')  # 强制关闭测试客户端进程

    def modify_ini_file(self, section, option, value):
        config = configparser.ConfigParser(strict=False)  # 创建新的配置解析器
        config.read(self.ini_file_path, encoding='gbk')  # 读取INI文件
        if config.has_section(section):  # 检查节是否存在
            config.set(section, option, str(value).strip())  # 修改指定选项的值
            with open(self.ini_file_path, 'w', encoding='gbk') as configfile:  # 打开INI文件以写入
                config.write(configfile)  # 写入配置
            
            # 使用正则表达式去掉等于号两边的空格
            with open(self.ini_file_path, 'r', encoding='gbk') as configfile:
                content = configfile.read()
                content = re.sub(r'\s*=\s*', '=', content)  # 去掉等于号两边的空格
    
            # 将处理后的内容写回文件
            with open(self.ini_file_path, 'w', encoding='gbk') as configfile:
                configfile.write(content)
            
            return value  # 返回修改后的值
        raise Exception(f'未找到节 {section}')  # 抛出异常

    def start_process(self):
        subprocess.Popen(self.process_path)  # 启动测试客户端进程

    def handle_section(self, section_name):
        start_value = self.config.getint(section_name, 'start')  # 获取起始值
        finish_value = self.config.getint(section_name, 'finish')  # 获取结束值
        running_time = self.config.getint(section_name, 'running_time')  # 获取运行时间
        increment = self.config.getint(section_name, 'increment')  # 获取增量
        test_case = self.config.getint(section_name, 'test_case')  # 获取测试用例
        iswithdrawal = self.config.getint(section_name, 'iswithdrawal')  # 获取是否撤回

        # 检查并写入 function_number
        if self.config.has_option(section_name, 'function_number'):
            function_number = self.config.get(section_name, 'function_number')  # 获取功能编号
            with open('funcid.txt', 'w') as f:  # 打开文件以写入
                f.write(str(function_number).replace(',', '\n'))  # 写入功能编号

        current_value = self.modify_ini_file(self.section, self.option1, start_value)  # 修改INI文件中的值
        self.modify_ini_file(self.section, self.option2, test_case)  # 修改测试用例
        self.modify_ini_file(self.section, self.option3, iswithdrawal)  # 修改是否撤回
        return current_value, finish_value, running_time, increment  # 返回相关参数

    def run(self):
        section_name = input("请输入节的名字 (Login/Search/Entrust/Mix): ")  # 输入节的名字
        if section_name not in self.SECTIONS:  # 检查节的名字是否有效
            raise ValueError("无效的节名字，请输入 Login、Search、Entrust 或 Mix。")  # 抛出异常

        current_value, finish_value, running_time, increment = self.handle_section(section_name)  # 处理节的配置
        loop_count = 1  # 初始化循环计数

        while True:
            logging.info('Info Begin')  # 记录开始信息
            self.start_process()  # 启动测试客户端进程
            logging.info(f"开始时间: {time.strftime('%Y年%m月%d日 %H时%M分%S秒', time.localtime())}")  # 记录开始时间
            logging.info(f"压力测试正式开始！'{self.option1}'的当前值为: {current_value} (压测运行次数: {loop_count})")  # 记录压力测试信息
            time.sleep(running_time)  # 等待指定的运行时间
            self.close_process()  # 关闭测试客户端进程
            logging.info(f"结束时间: {time.strftime('%Y年%m月%d日 %H时%M分%S秒', time.localtime())}")  # 记录结束时间
            logging.info('Info End')  # 记录结束信息

            current_value += increment  # 更新当前值
            new_value = self.modify_ini_file(self.section, self.option1, current_value)  # 修改INI文件中的值
            loop_count += 1  # 增加循环计数

            if new_value > finish_value:  # 检查是否超过结束值
                logging.info(f"finish值：{finish_value}，停止程序。")  # 记录结束信息
                break  # 退出循环

if __name__ == '__main__':
    cof_path = r'.\cof.ini'  # 配置文件路径
    manager = StressTesting(cof_path)  # 创建StressTesting实例
    manager.run()  # 运行压力测试
    input("程序结束...")  # 等待用户输入
