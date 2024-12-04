import csv
import os
import time
import configparser
import logging
import subprocess
import re
from mysql.connector import Error
import mysql.connector

class StressTesting:
    SECTIONS = ['Login', 'Search', 'Entrust', 'Mix']

    def __init__(self, cof_path):
        self.config = configparser.ConfigParser(strict=False)
        self.config.read(cof_path, encoding='gbk')
        self.process_name = 'testclient.exe'
        self.process_path = r'.\testclient.exe'
        self.ini_file_path = r'.\client.ini'
        self.section = 'ClientComm_Common'
        self.option1 = 'deal_second'
        self.option2 = 'test_case'
        self.option3 = 'iswithdrawal'
        self.setup_logging()

    def setup_logging(self):
        os.makedirs('stresslog', exist_ok=True)
        log_filename = time.strftime('stresslog/stress_test_%Y%m%d_%H%M%S.log')
        logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def close_process(self):
        os.system(f'taskkill /f /im {self.process_name}')

    def modify_ini_file(self, section, option, value):
        config = configparser.ConfigParser(strict=False)
        config.read(self.ini_file_path, encoding='gbk')
        if config.has_section(section):
            config.set(section, option, str(value).strip())
            with open(self.ini_file_path, 'w', encoding='gbk') as configfile:
                config.write(configfile)
            self.clean_ini_file()
            return value
        raise Exception(f'未找到节 {section}')

    def clean_ini_file(self):
        with open(self.ini_file_path, 'r', encoding='gbk') as configfile:
            content = configfile.read()
        content = re.sub(r'\s*=\s*', '=', content)
        with open(self.ini_file_path, 'w', encoding='gbk') as configfile:
            configfile.write(content)

    def start_process(self):
        subprocess.Popen(self.process_path)

    def handle_section(self, section_name):
        start_value = self.config.getint(section_name, 'start')
        finish_value = self.config.getint(section_name, 'finish')
        running_time = self.config.getint(section_name, 'running_time')
        increment = self.config.getint(section_name, 'increment')
        test_case = self.config.getint(section_name, 'test_case')
        iswithdrawal = self.config.getint(section_name, 'iswithdrawal')

        if self.config.has_option(section_name, 'function_number'):
            function_number = self.config.get(section_name, 'function_number')
            with open('funcid.txt', 'w') as f:
                f.write(str(function_number).replace(',', '\n'))

        current_value = self.modify_ini_file(self.section, self.option1, start_value)
        self.modify_ini_file(self.section, self.option2, test_case)
        self.modify_ini_file(self.section, self.option3, iswithdrawal)
        return current_value, finish_value, running_time, increment

    def create_connection(self, host_name, user_name, user_password, db_name):
        try:
            connection = mysql.connector.connect(
                host=host_name,
                user=user_name,
                password=user_password,
                database=db_name
            )
            logging.info("成功连接到MySQL数据库")
            return connection
        except Error as e:
            logging.error(f"发生错误: '{e}'")
            return None

    def run(self):
        section_name = input("请输入节的名字 (Login/Search/Entrust/Mix): ")
        if section_name not in self.SECTIONS:
            raise ValueError("无效的节名字，请输入 Login、Search、Entrust 或 Mix。")

        current_value, finish_value, running_time, increment = self.handle_section(section_name)
        loop_count = 1
        self.start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        while True:
            logging.info('Info Begin')
            self.start_process()
            logging.info(f"开始时间: {time.strftime('%Y年%m月%d日 %H时%M分%S秒', time.localtime())}")
            logging.info(f"压力测试正式开始！'{self.option1}'的当前值为: {current_value} (压测运行次数: {loop_count})")
            time.sleep(running_time)
            self.close_process()
            logging.info(f"结束时间: {time.strftime('%Y年%m月%d日 %H时%M分%S秒', time.localtime())}")
            logging.info('Info End')

            current_value += increment
            new_value = self.modify_ini_file(self.section, self.option1, current_value)
            loop_count += 1

            if new_value > finish_value:
                logging.info(f"finish值：{finish_value}，停止程序。")
                self.end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                break

    def export_to_csv(self, csv_filename):
        connection = self.create_connection('localhost', 'your_username', 'your_password', 'your_database')
        if connection is None:
            return

        cursor = connection.cursor()
        sql1 = '''
        SELECT
            CONCAT("'", time) AS '时间|time',
            cpu AS 'CPU|cpu',
            memory AS '内存|memory',
            disks_readbytes AS '磁盘IO读取|disks_readbytes',
            disks_writebytes AS '磁盘IO写入|disks_writebytes',
            network_bytesrecv AS '网络接收字节|network_bytesrecv',
            network_bytessent AS '网络发送字节|network_bytessent'
        FROM
            loganalyze.metric_info
        WHERE
            ip = '172.190.121.106' AND time BETWEEN %s AND %s
        ORDER BY
            time;
        '''
        sql2 = '''
        SELECT
            CONCAT("'", clientcomm_common_time) AS '时间|clientcomm_common_time',
            total_dequeue_speed AS '持续吞吐率|total_dequeue_speed',
            max_deal_speed AS '峰值吞吐率|max_deal_speed',
            avg_deal_time AS '平均时延ms|avg_deal_time',
            total_enqueue AS '总请求|total_enqueue',
            failed_cnt AS '失败数|failed_cnt'
        FROM
            loganalyze.test_client
        WHERE
            ip = '192.168.8.20'
            AND clientcomm_common_time BETWEEN %s AND %s
        ORDER BY
            clientcomm_common_time;
        '''
        
        # Export sql1 results
        cursor.execute(sql1, (self.start_time, self.end_time))
        results1 = cursor.fetchall()
        os.makedirs('CSV/M', exist_ok=True)
        csv_filename1 = f'CSV/M/{csv_filename}_metric_info_{time.strftime("%Y%m%d_%H%M%S")}.csv'
        with open(csv_filename1, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([i[0] for i in cursor.description])
            writer.writerows(results1)

        # Export sql2 results
        cursor.execute(sql2, (self.start_time, self.end_time))
        results2 = cursor.fetchall()
        os.makedirs('CSV/T', exist_ok=True)
        csv_filename2 = f'CSV/T/{csv_filename}_test_client_{time.strftime("%Y%m%d_%H%M%S")}.csv'
        with open(csv_filename2, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([i[0] for i in cursor.description])
            writer.writerows(results2)

        cursor.close()
        connection.close()
        logging.info(f"数据已导出到 {csv_filename1} 和 {csv_filename2}")

if __name__ == '__main__':
    cof_path = r'.\cof.ini'
    manager = StressTesting(cof_path)
    manager.run()
    manager.export_to_csv('stress_test_results')  # Specify the desired CSV filename
    input("程序结束...")
