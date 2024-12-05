import os, time, configparser, logging, subprocess, re
from logging.handlers import TimedRotatingFileHandler


class StressTesting:

    def __init__(self):
        # 初始化配置
        self.SECTIONS = ['Login', 'Search', 'Entrust', 'Mix']
        self.config = configparser.ConfigParser()
        self.config.read(r'D:\test_project\stress_testing\V11.0\PushTest\cof.ini', encoding='gbk')
        self.process_name = 'testclient.exe'  # 进程名称
        self.process_path = r'D:\testclient\testclient.exe'  # 进程路径
        self.ini_file_path = r'D:\testclient\client.ini'  # INI文件路径
        self.funcid_path = r'D:\testclient\funcid.txt'  # 功能ID文件路径
        self.section = 'ClientComm_Common'  # 配置节
        self.option1 = 'deal_second'  # 选项1
        self.option2 = 'test_case'  # 选项2
        self.option3 = 'iswithdrawal'  # 选项3
        self.option4 = 'account_cnt'  #选项4
        self.setup_logging()  # 设置日志

    def setup_logging(self):
        # 设置日志记录
        os.makedirs('.\stresslog', exist_ok=True)  # 创建日志目录
        log_filename = os.path.join('.\stresslog', f'stress_test_{time.strftime("%Y-%m-%d")}.log')
        handler = TimedRotatingFileHandler(log_filename, when="midnight", interval=1, backupCount=7)  # 定时轮转日志
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))  # 设置日志格式
        logging.getLogger().addHandler(handler)  # 添加日志处理器
        logging.getLogger().setLevel(logging.INFO)  # 设置日志级别

    def modify_ini_file(self, section, option, value):
        # 修改INI文件中的指定选项并清理空格
        config = configparser.ConfigParser()
        config.read(self.ini_file_path, encoding='gbk')
        config.set(section, option, str(value).strip())  # 设置选项值
        with open(self.ini_file_path, 'w', encoding='gbk') as configfile:
            config.write(configfile)  # 写入INI文件
        # 清理INI文件中的空格
        with open(self.ini_file_path, 'r', encoding='gbk') as configfile:
            content = re.sub(r'\s*=\s*', '=', configfile.read())  # 去除等号两边的空格
        with open(self.ini_file_path, 'w', encoding='gbk') as configfile:
            configfile.write(content)  # 写入清理后的内容
        return value

    def handle_section(self, section_name):
        # 处理指定节的配置
        start_value = self.config.getint(section_name, 'start')  # 获取起始值
        finish_value = self.config.getint(section_name, 'finish')  # 获取结束值
        running_time = self.config.getint(section_name, 'running_time')  # 获取运行时间
        increment = self.config.getint(section_name, 'increment')  # 获取增量
        test_case = self.config.getint(section_name, 'test_case')  # 获取测试用例
        iswithdrawal = self.config.getint(section_name, 'iswithdrawal')  # 获取是否撤回标志
        function_number = self.config.get(section_name, 'function_number')  # 获取功能编号
        sleep = self.config.getint(section_name, 'sleep')  # 获取休眠时间
        with open(self.funcid_path, 'w') as f:
            f.write(str(function_number).replace(',', '\n'))  # 写入功能编号到文件
        current_value = self.modify_ini_file(self.section, self.option1, start_value)  # 修改INI文件中的当前值
        self.modify_ini_file(self.section, self.option2, test_case)  # 修改测试用例
        self.modify_ini_file(self.section, self.option3, iswithdrawal)  # 修改撤回标志
        return current_value, finish_value, running_time, increment, sleep  # 返回当前值、结束值、运行时间和增量

    def run(self):
        # 运行压力测试
        section_name = input("请输入节的名字 (Login/Search/Entrust/Mix): ").strip().lower()  # 输入节的名字并去除空格
        section_map = {'l': 'Login', 's': 'Search', 'e': 'Entrust', 'm': 'Mix'}  # 首字母映射
        if section_name in section_map:
            section_name = section_map[section_name]  # 根据首字母获取节名字
        if section_name not in self.SECTIONS:
            raise ValueError("无效的节名字，请输入 Login、Search、Entrust 或 Mix。")  # 验证节名字
        current_value, finish_value, running_time, increment, sleep = self.handle_section(section_name)  # 处理节配置
        loop_count = 1

        # 新增变量来存储开始和结束时间
        start_times = []
        end_times = []

        logging.info(
            f'{section_name}计划开始了，初始线程数：{current_value}，自增值:{increment}，运行时间：{running_time}秒，线程数阈值{finish_value}。')
        while True:
            logging.info('Info Begin')  # 日志记录开始信息
            subprocess.Popen(self.process_path, cwd=os.path.dirname(self.process_path))  # 启动进程
            start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())  # 记录开始时间
            start_times.append(start_time)  # 存储开始时间
            logging.info(f"开始时间: {start_time}")  # 记录开始时间
            logging.info(
                f"压力测试正式开始！'{self.option1}'的当前值为: {current_value} (压测运行次数: {loop_count})")  # 记录压力测试信息
            time.sleep(running_time)  # 等待运行时间
            os.system(f'taskkill /f /im {self.process_name}')  # 强制结束进程
            time.sleep(sleep)
            end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())  # 记录结束时间
            end_times.append(end_time)  # 存储结束时间
            logging.info(f"结束时间: {end_time}")  # 记录结束时间
            logging.info('Info End')  # 日志记录结束信息

            # 根据当前时间生成唯一的节名
            timestamp = time.strftime('%Y%m%d_%H%M%S')  # 获取当前时间戳
            section_to_write = f'{section_name}_{current_value}_{start_times[-1]}_{end_times[-1]}'  # 生成包含时间戳的节名

            # 写入数据到 data_time.ini 文件
            data_file_path = os.path.join('..', 'Data_Time', 'data_time.ini')  # 数据文件路径
            os.makedirs(os.path.dirname(data_file_path), exist_ok=True)  # 创建目录
            config = configparser.ConfigParser()
            config.read(data_file_path, encoding='utf-8')

            # 确保节存在
            if not config.has_section(section_to_write):
                config.add_section(section_to_write)  # 新建节

                # 写入当前值和时间到节
            config.set(section_to_write, 'T', f"{current_value}")
            config.set(section_to_write, 'st', f"{start_times[-1]}")
            config.set(section_to_write, 'ed', f"{end_times[-1]}")

            with open(data_file_path, 'w', encoding='utf-8') as datafile:
                config.write(datafile)  # 写入INI文件

            current_value += increment  # 更新当前值
            new_value = self.modify_ini_file(self.section, self.option1, current_value)  # 修改INI文件中的当前值
            loop_count += 1  # 增加循环计数
            if new_value > finish_value:
                logging.info(f'{section_name}计划结束了！')
                break


if __name__ == '__main__':
    manager = StressTesting()  # 创建压力测试管理器
    manager.run()  # 运行压力测试
    input("程序结束...")  # 等待用户输入以结束程序
