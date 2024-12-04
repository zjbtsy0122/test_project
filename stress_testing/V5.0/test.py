# -*- coding: gbk -*-  #
from mysql.connector import Error
import mysql.connector
import logging
import csv
import os
# import pymysql

class StressTesting:
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


    def export_to_csv(self, csv_filename):
        connection = self.create_connection('172.192.85.79', 'root', 'csglb#2023', 'loganalyze')
        if connection is None:
            return

        cursor = connection.cursor()
        sql = '''
            select * from test_client where id =1;
            '''
        cursor.execute(sql)
        results = cursor.fetchall()

        os.makedirs('CSV', exist_ok=True)
        with open(f'CSV/{csv_filename}.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([i[0] for i in cursor.description])
            writer.writerows(results)

        cursor.close()
        connection.close()
        logging.info(f"数据已导出到 CSV/{csv_filename}.csv")


if __name__ == '__main__':
    manager = StressTesting()

    manager.export_to_csv('stress_test_results')
