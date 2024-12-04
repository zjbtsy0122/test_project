# -*- coding: utf-8 -*-
from socket import *
import configparser
import os

class Server_pq:
    def __init__(self):
        self.cfg = configparser.ConfigParser()
        self.cfg.read('s_cfg.ini', encoding='utf-8')  # 使用 utf-8 编码读取配置文件
        host = self.cfg.get('server', 'host')
        port = self.cfg.get('server', 'port')
        self.bufsiz = int(self.cfg.get('server', 'bufsiz'))
        self.ADDR = (host, int(port))
        self.section = self.cfg.get('find', 'section').split(',')
        self.item =['网关地址', '网关端口']

    def start_server(self):           #通信过程
        udpSerSock = socket(AF_INET, SOCK_DGRAM)
        print(f"Server listening on {self.ADDR}")
        udpSerSock.bind(self.ADDR)  #绑定地址和端口号
        while True:
            print('waiting for message...')
            data, addr = udpSerSock.recvfrom(self.bufsiz) #1024表示最大接收的数据量
            result = data.decode('utf-8')
            print(f"Received from client: {result} at {self.ADDR}")
            result = self.select_action(result)
            if result:
                udpSerSock.sendto(result.encode(), addr)
                print(f"Sent to client: {result}")
            else:
                print("No data to send")
        # udpSerSock.close()  # 关闭套接字

    def select_action(self, data):   #操作选择
        data = data.split('-')
        if data[0] == 'Find':
            result = self.f_get_data(data[1], self.section, self.item)
            result = self.f_change_aryy(result)
            if result:
                return result

            else:
                print("No data found")
        else:
            print("NO!!!")

    def f_get_data(self, path, section, item, file='TradeTrans_private.ini'): #从具体文件中取数据
        conf = configparser.ConfigParser()
        full_path = os.path.join(path, file)
        print(f"Reading from: {full_path}")
        try:
            conf.read(full_path, encoding='gbk')  # 使用 GBK 编码读取文件
        except Exception as e:
            print(f"Error reading file: {e}")
            return []

        geted_data = []
        for sec in section:
            try:
                value = []
                for itm in item:
                    value.append(conf.get(sec, itm))
                geted_data.append([sec, value])
            except configparser.NoSectionError:
                print(f"No section: {sec}")
                continue
            except configparser.NoOptionError as e:
                print(f"Missing option: {e}")
                continue
        print(f"Retrieved data: {geted_data}")
        return geted_data

    def f_change_aryy(self, data): #数组转字符串
        for i in range(len(data)):
            data[i][1] = '-'.join(data[i][1])
            data[i] = '-'.join(data[i])
        if data:
            data = ','.join(data)
            return data
        else:
            return None

if __name__ == '__main__':
    main = Server_pq()
    main.start_server()
