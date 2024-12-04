# -*- coding: gbk -*-  # 设置文件编码为GBK
from socket import *  # 从socket模块中导入所有内容
import configparser  # 导入配置解析器模块

class Server_pq():  # 定义服务器类
    def __init__(self):  # 初始化方法
        cfg = configparser.ConfigParser()  # 创建配置解析器对象
        cfg.read('s_cfg.ini')  # 读取服务器配置文件
        host = cfg.get('server', 'host')  # 获取服务器主机地址
        port = cfg.get('server', 'port')  # 获取服务器端口
        self.bufsiz = int(cfg.get('server', 'bufsiz'))  # 获取缓冲区大小
        self.ADDR = (host, int(port))  # 设置服务器地址
        self.section = cfg.get('server', 'section').split(',')  # 获取配置节名称列表
        # self.section = ['jsdspxa_common', 'jsdspxa_credit', 'jsdspxgoldexch_common']
        self.item = ['网关地址', '网关端口']  # 配置项名称列表

    def get_data(self, path, section, item, file='TradeTrans_private.ini'):  # 从具体文件中取数据
        conf = configparser.ConfigParser()  # 创建配置解析器对象
        conf.read(path + file)  # 读取指定路径下的配置文件
        geted_data = []  # 初始化获取的数据列表
        for i in range(len(section)):  # 遍历配置节
            value = []  # 初始化值列表
            for j in range(len(item)):  # 遍历配置项
                value.append(conf.get(section[i], item[j]))  # 获取配置值
            geted_data.append([section[i], value])  # 添加节和值到数据列表
        return geted_data  # 返回获取的数据

    def change_aryy(self, data):  # 数组转字符串
        for i in range(len(data)):  # 遍历数据
            data[i][1] = '-'.join(data[i][1])  # 将值列表转换为字符串
            data[i] = '-'.join(data[i])  # 将节和值转换为字符串
        data = ','.join(data)  # 将所有数据连接成一个字符串
        return data  # 返回字符串

    def start_server(self):  # 启动服务器方法
        udpSerSock = socket(AF_INET, SOCK_DGRAM)  # 创建UDP套接字
        print(self.ADDR)  # 打印服务器地址
        udpSerSock.bind(self.ADDR)  # 绑定服务器地址
        while True:
            print('waiting for message...')  # 等待消息
            data, addr = udpSerSock.recvfrom(self.bufsiz)  # 接收数据
            result = data.decode('utf-8')  # 解码数据
            print(result)  # 打印接收到的数据
            result = self.select_action(result)  # 选择操作
            udpSerSock.sendto(result.encode(), addr)  # 发送响应
            print('...received from and returned to:', addr)  # 打印客户端地址

    def select_action(self, data):  # 操作选择方法
        if data[0:5] == 'Find-':  # 如果操作为查找
            result = self.get_data(data[5:], self.section, self.item)  # 获取数据
            result = self.change_aryy(result)  # 转换数据格式
            # print(result)
            return result  # 返回结果
        else:
            print("NO!!!")  # 操作无效

if __name__ == '__main__':  # 主程序入口
    main = Server_pq()  # 创建服务器实例
    main.start_server()  # 启动服务器
