from mysql.connector import Error
import mysql.connector
import logging
import csv
import configparser
import os
import time
from datetime import datetime

class DataAnalysis:

    def __init__(self):
        self.data_path=r'./StressTesting/data.ini'
        self.metric_info_path=r'./StressTesting/metric_info.sql'
        self.test_client_path=r'./StressTesting/test_client.sql'
        config = configparser.ConfigParser()
        config.read(self.data_path)
        self.host_name = config['Login']['host_name']
        self.user_name = config['Login']['user_name']
        self.user_password = config['Login']['user_password']
        self.db_name = config['Login']['db_name']
        self.start_time = config['Search']['start_time']
        self.end_time = config['Search']['end_time']

    def create_connection(self):
        # 创建MySQL数据库连接
        try:
            connection = mysql.connector.connect(
                host=self.host_name,
                user=self.user_name,
                password=self.user_password,
                database=self.db_name
            )
            logging.info("成功连接到MySQL数据库")
            return connection
        except Error as e:
            logging.error(f"发生错误: '{e}'")
            return None

    def export_to_csv(self, csv_filename):
        # 导出数据到CSV文件
        connection = self.create_connection()
        if connection is None:
            return

        cursor = connection.cursor()

        with open(self.metric_info_path, 'r', encoding='utf-8') as file:
            sql1 = file.read()

        with open(self.test_client_path, 'r', encoding='utf-8') as file:
            sql2 = file.read()

        #转换时间格式
        starttime = datetime.strptime(self.start_time, "%Y-%m-%d %H:%M:%S").strftime("%Y%m%d_%H%M%S")
        endtime = datetime.strptime(self.end_time, "%Y-%m-%d %H:%M:%S").strftime("%H%M%S")

        # 导出sql1结果
        cursor.execute(sql1, (self.start_time, self.end_time))
        results1 = cursor.fetchall()
        os.makedirs('./StressTesting/CSV/Metric_Info', exist_ok=True)
        csv_filename1 = f'./StressTesting/CSV/Metric_Info/{csv_filename}_metric_info_{starttime}_{endtime}.csv'
        with open(csv_filename1, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([i[0] for i in cursor.description])
            #写入列名
            # column_names=[]
            # for i in cursor.description:
            #     column_names.append(i[0])
            # writer.writerow(column_names)
            writer.writerows(results1)

        # 导出sql2结果
        cursor.execute(sql2, (self.start_time, self.end_time))
        results2 = cursor.fetchall()
        os.makedirs('./StressTesting/CSV/Test_Client', exist_ok=True)
        csv_filename2 = f'./StressTesting/CSV/Test_Client/{csv_filename}_test_client_{starttime}_{endtime}.csv'
        with open(csv_filename2, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([i[0] for i in cursor.description])
            writer.writerows(results2)

        cursor.close()
        connection.close()
        # logging.info(f"数据已导出到 {csv_filename1} 和 {csv_filename2}")



if __name__ == '__main__':

    db_manager = DataAnalysis()
    db_manager.export_to_csv('Results')