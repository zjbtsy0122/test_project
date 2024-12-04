import mysql.connector,configparser,os
import pandas as pd
from datetime import datetime

class DataAnalysis:
    def __init__(self):
        # 初始化配置文件路径
        self.metric_info_path = r'./metric_info.sql'
        self.test_client_path = r'./test_client.sql'
        
        # 读取配置文件
        config = configparser.ConfigParser()
        config.read(r'./data.ini')
        self.host_name = config['Login']['host_name']
        self.user_name = config['Login']['user_name']
        self.user_password = config['Login']['user_password']
        self.db_name = config['Login']['db_name']
        self.start_time = config['Search']['start_time']
        self.end_time = config['Search']['end_time']

    def create_connection(self):
        # 创建MySQL数据库连接
        connection = mysql.connector.connect(host=self.host_name, user=self.user_name, password=self.user_password, database=self.db_name)
        return connection
       
    def fetch_data(self, sql, params):
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute(sql, params)
        results = cursor.fetchall()
        columns = [i[0] for i in cursor.description]  # 列名
        cursor.close()
        connection.close()
        return results, columns

    def export_to_csv(self):
        # 导出数据到Excel文件
        # 读取SQL查询语句
        with open(self.metric_info_path, 'r', encoding='utf-8') as file:
            sql1 = file.read()

        with open(self.test_client_path, 'r', encoding='utf-8') as file:
            sql2 = file.read()
        
        # 转换时间格式
        starttime = datetime.strptime(self.start_time, '%Y-%m-%d %H:%M:%S').strftime('%Y%m%d_%H%M%S')
        endtime = datetime.strptime(self.end_time, '%Y-%m-%d %H:%M:%S').strftime('%H%M%S')       

        # 导出sql1结果
        results1, columns1 = self.fetch_data(sql1, (self.start_time, self.end_time))

        # 导出sql2结果
        results2, columns2 = self.fetch_data(sql2, (self.start_time, self.end_time))

        # 创建DataFrame并写入Excel文件
        os.makedirs('./Result', exist_ok=True)
        with pd.ExcelWriter(f'./Result/{starttime}_{endtime}.xlsx') as writer:
            df1 = pd.DataFrame(results1, columns=columns1)
            df1.to_excel(writer, sheet_name='Metric Info', index=False)

            df2 = pd.DataFrame(results2, columns=columns2)
            df2.to_excel(writer, sheet_name='Test Client', index=False)


if __name__ == '__main__':
    db_manager = DataAnalysis()
    db_manager.export_to_csv()