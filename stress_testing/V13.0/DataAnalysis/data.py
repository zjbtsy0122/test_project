


import mysql.connector
import configparser
import os
import pandas as pd
from datetime import datetime

class DataAnalysis:
    def __init__(self):
        self.metric_info_path = r'./metric_info.sql'  # 指标信息SQL文件路径
        self.test_client_path = r'./test_client.sql'  # 测试客户端SQL文件路径
        config = configparser.ConfigParser()
        config.read(r'./data.ini')  # 读取配置文件
        self.host_name = config['data']['host_name']  # 数据库主机名
        self.user_name = config['data']['user_name']  # 数据库用户名
        self.user_password = config['data']['user_password']  # 数据库密码
        self.db_name = config['data']['db_name']  # 数据库名称

    def create_connection(self):
        # 创建数据库连接
        connection = mysql.connector.connect(host=self.host_name, user=self.user_name, password=self.user_password, database=self.db_name)
        return connection

    def fetch_data(self, sql, params):
        # 执行SQL查询并获取结果
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute(sql, params)
        results = cursor.fetchall()  # 获取所有结果
        columns = [i[0] for i in cursor.description]  # 获取列名
        cursor.close()
        connection.close()
        return results, columns

    def get_section_data(self, section):
        # 获取指定节的数据
        config = configparser.ConfigParser()
        config.read(r'./data.ini')  # 读取配置文件
        return dict(config[section])  # 返回节的数据字典

    def export_to_excel(self):
        # 从SQL文件读取查询语句
        with open(self.metric_info_path, 'r', encoding='utf-8') as file:
            sql1 = file.read()

        with open(self.test_client_path, 'r', encoding='utf-8') as file:
            sql2 = file.read()

        # 创建结果文件夹
        os.makedirs('./Result', exist_ok=True)

        # 遍历指定的节名称
        for section_name in ['time_L', 'time_S', 'time_E', 'time_M']:
            section_data = self.get_section_data(section_name)
            self.start_time = section_data.get('start_time')  # 获取开始时间
            self.end_time = section_data.get('end_time')  # 获取结束时间

            # 处理start_time和end_time为空的情况
            if not self.start_time or not self.end_time:
                print(f"Skipping section {section_name} due to missing time range.")
                continue  # 如果start_time或end_time为空，跳过该节

            # 格式化开始和结束时间
            starttime = datetime.strptime(self.start_time, '%Y-%m-%d %H:%M:%S').strftime('%Y%m%d_%H%M%S')
            endtime = datetime.strptime(self.end_time, '%Y-%m-%d %H:%M:%S').strftime('%H%M%S')

            # 获取查询结果
            results1, columns1 = self.fetch_data(sql1, (self.start_time, self.end_time))
            results2, columns2 = self.fetch_data(sql2, (self.start_time, self.end_time))

            excel_path = f'./Result/{section_name}_{starttime}_{endtime}.xlsx'  # Excel文件路径

            with pd.ExcelWriter(excel_path) as writer:
                df1 = pd.DataFrame(results1, columns=columns1)  # 创建指标信息DataFrame
                df2 = pd.DataFrame(results2, columns=columns2)

                # 将数据写入Excel文件
                df1.to_excel(writer, sheet_name='Metric Info', index=False)
                df2.to_excel(writer, sheet_name='Test Client', index=False)

            # 重新读取Excel文件以添加新列
            df1 = pd.read_excel(excel_path, sheet_name='Metric Info')
            df2 = pd.read_excel(excel_path, sheet_name='Test Client')

            # 创建配置解析器
            config = configparser.ConfigParser()
            config.read(r'./data.ini')

            # 根据首字母匹配节名称
            matching_sections = []  # 存储匹配的节名称
            for section in config.sections():
                if section.startswith(section_name[5]):  # 检查节名称是否以指定字母开头
                    matching_sections.append(section)  # 添加匹配的节名称

            # 收集所有匹配节的数据
            section_data_list = []  # 存储所有匹配节的数据
            for section in matching_sections:
                section_data = self.get_section_data(section)  # 获取节的数据
                section_data_list.append(section_data)  # 添加到列表中

            # 更新新列
            df1['Threads'] = None
            df2['Threads'] = None
            for section_data in section_data_list:
                # 根据时间范围添加新列
                df1['Threads'] = df1['Threads'].combine_first(df1['Time'].apply(lambda x: section_data['t'] if section_data['st'] <= x[1:] <= section_data['ed'] else None))
                df2['Threads'] = df2['Threads'].combine_first(df2['Time'].apply(lambda x: section_data['t'] if section_data['st'] <= x[1:] <= section_data['ed'] else None))

            # 将更新后的数据写回Excel文件
            with pd.ExcelWriter(excel_path) as writer:
                df1.to_excel(writer, sheet_name='Metric Info', index=False)
                df2.to_excel(writer, sheet_name='Test Client', index=False)

if __name__ == '__main__':
    db_manager = DataAnalysis()
    db_manager.export_to_excel()  # 执行数据导出
