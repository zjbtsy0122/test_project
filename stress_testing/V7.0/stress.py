import os
import time
import configparser
import logging
from logging.handlers import TimedRotatingFileHandler
import subprocess
import re


class StressTesting:
    

    def __init__(self):
        # 初始化配置
        self.SECTIONS = ['Login', 'Search', 'Entrust', 'Mix']
        self.cof_path = r'.\StressTesting\cof.ini'
        self.config = configparser.ConfigParser(strict=False)
        self.config.read(self.cof_path, encoding='gbk')
        self.process_name = 'testclient.exe'  # 进程名称
        self.process_path = r'.\testclient.exe'  # 进程路径
        self.ini_file_path = r'.\client.ini'  # INI文件路径
        self.funcid_path = r'.\funcid.txt'
        self.data_path = r'.\StressTesting\data.ini'
        self.section = 'ClientComm_Common'  # 配置节
        self.option1 = 'deal_second'  # 选项1
        self.option2 = 'test_case'  # 选项2
        self.option3 = 'iswithdrawal'  # 选项3
        self.setup_logging()  # 设置日志

    def setup_logging(self):
    # 设置日志记录
        os.makedirs('.\StressTesting\stresslog', exist_ok=True)
        log_filename = os.path.join('.\StressTesting\stresslog', f'stress_test_{time.strftime("%Y-%m-%d")}.log')
        handler = TimedRotatingFileHandler(log_filename, when="midnight", interval=1, backupCount=7)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)


    def modify_ini_file(self, section, option, value):
        # 修改INI文件中的指定选项
        config = configparser.ConfigParser(strict=False)
        config.read(self.ini_file_path, encoding='gbk')
        if config.has_section(section):
            config.set(section, option, str(value).strip())
            with open(self.ini_file_path, 'w', encoding='gbk') as configfile:
                config.write(configfile)
            self.clean_ini_file()  # 清理INI文件
            return value
        raise Exception(f'未找到节 {section}')

    def clean_ini_file(self):
        # 清理INI文件中的空格
        with open(self.ini_file_path, 'r', encoding='gbk') as configfile:
            content = configfile.read()
        content = re.sub(r'\s*=\s*', '=', content)
        with open(self.ini_file_path, 'w', encoding='gbk') as configfile:
            configfile.write(content)

    def handle_section(self, section_name):
        # 处理指定节的配置
        start_value = self.config.getint(section_name, 'start')
        finish_value = self.config.getint(section_name, 'finish')
        running_time = self.config.getint(section_name, 'running_time')
        increment = self.config.getint(section_name, 'increment')
        test_case = self.config.getint(section_name, 'test_case')
        iswithdrawal = self.config.getint(section_name, 'iswithdrawal')

        if self.config.has_option(section_name, 'function_number'):
            function_number = self.config.get(section_name, 'function_number')
            with open(self.funcid_path, 'w') as f:
                f.write(str(function_number).replace(',', '\n'))

        current_value = self.modify_ini_file(self.section, self.option1, start_value)
        self.modify_ini_file(self.section, self.option2, test_case)
        self.modify_ini_file(self.section, self.option3, iswithdrawal)
        return current_value, finish_value, running_time, increment
    
    def write_time_to_ini(self, section, option, value):
        # 写入时间到INI文件
        config = configparser.ConfigParser(strict=False)
        config.read(self.data_path, encoding='gbk')
        if not config.has_section(section):
            config.add_section(section)
        config.set(section, option, value)
        with open(self.data_path, 'w', encoding='gbk') as configfile:
            config.write(configfile)

    def run(self):
        # 运行压力测试
        section_name = input("请输入节的名字 (Login/Search/Entrust/Mix): ")
        if section_name not in self.SECTIONS:
            raise ValueError("无效的节名字，请输入 Login、Search、Entrust 或 Mix。")

        current_value, finish_value, running_time, increment = self.handle_section(section_name)
        loop_count = 1
        self.start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        
        # 写入开始时间到data.ini
        self.write_time_to_ini('Search', 'start_time', self.start_time)

        while True:
            logging.info('Info Begin')
            subprocess.Popen(self.process_path)
            logging.info(f"开始时间: {time.strftime('%Y年%m月%d日 %H时%M分%S秒', time.localtime())}")
            logging.info(f"压力测试正式开始！'{self.option1}'的当前值为: {current_value} (压测运行次数: {loop_count})")
            time.sleep(running_time)
            os.system(f'taskkill /f /im {self.process_name}')
            logging.info(f"结束时间: {time.strftime('%Y年%m月%d日 %H时%M分%S秒', time.localtime())}")
            logging.info('Info End')

            current_value += increment
            new_value = self.modify_ini_file(self.section, self.option1, current_value)
            loop_count += 1

            if new_value > finish_value:
                self.end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                # 写入结束时间到data.ini
                self.write_time_to_ini('Search', 'end_time', self.end_time)
                logging.info(f"finish值：{finish_value}，停止程序。")
                break

if __name__ == '__main__':
    manager = StressTesting()
    manager.run()
    input("程序结束...")
