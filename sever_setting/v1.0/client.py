# -*- coding: gbk -*-  # 设置文件编码为GBK
from socket import *  # 从socket模块中导入所有内容
import configparser  # 导入配置解析器模块

class Client_pq():  # 定义客户端类
    def __init__(self):  # 初始化方法
        while True:  # 无限循环
            self.flag_f = 0  # 标志位初始化为0
            do = input('请输入指令（Find）：')  # 提示用户输入指令
            self.select_action(do)  # 调用操作选择方法

    def select_action(self, data):  # 操作选择方法
        if data == 'Find':  # 如果输入为'Find'
            print(self.Find())  # 执行Find方法并打印结果
        elif data[0:5] == 'Find_':  # 如果输入以'Find_'开头
            self.flag_f = 1  # 设置标志位为1
            print(self.Find(data[5:]))  # 执行Find方法并打印结果
        else:
            print('无法识别')  # 打印无法识别的提示

    def Find(self, section=[]):  # 查找方法
        sections = []  # 初始化节列表
        cfg = configparser.ConfigParser()  # 创建配置解析器对象
        cfg.read('c_cfg.ini')  # 读取客户端配置文件
        self.res = configparser.ConfigParser()  # 创建结果配置解析器对象
        self.res.read('result.ini')  # 读取结果配置文件
        if section == []:  # 如果没有指定节
            sections = cfg.sections()  # 获取所有节名称
        else:
            if not cfg.has_section(section):  # 如果指定节不存在
                return('No this server or port!')  # 返回错误信息
            else:
                sections.append(section)  # 将指定节添加到列表
        for s in sections:  # 遍历所有节
            host = cfg.get(s, 'host')  # 获取主机地址
            port = cfg.get(s, 'port')  # 获取端口号
            bufsiz = int(cfg.get(s, 'bufsiz'))  # 获取缓冲区大小
            ADDR = (host, int(port))  # 创建服务器地址
            # print(ADDR)
            path = cfg.get(s, 'path')  # 获取路径
            # section = cfg.get(s, 'section').split(',')
            result = self.start_server(ADDR, bufsiz, path)  # 启动服务器并获取结果
            self.write_in(s, result)  # 将结果写入配置文件
        self.res.write(open('result.ini', 'w'))  # 保存结果配置文件
        return('Complete!!!')  # 返回完成信息

    def start_server(self, ADDR, bufsiz, path):  # 启动服务器方法
        result = []  # 初始化结果列表
        udpCliSock = socket(AF_INET, SOCK_DGRAM)  # 创建UDP套接字
        while True:
            path = 'Find-' + path  # 构造请求路径
            udpCliSock.sendto(path.encode(), ADDR)  # 发送请求到服务器
            data, ADDR = udpCliSock.recvfrom(bufsiz)  # 接收服务器返回的数据
            data = data.decode('utf-8').split(',')  # 解码并分割数据
            for d in data:
                result.append(d.split('-'))  # 将数据添加到结果列表
            # print(result)
            return result  # 返回结果
        # udpCliSock.close()

    def write_in(self, addr, data):  # 写入结果方法
        # addrs=addr[0]+':'+str(addr[1])
        if not self.res.has_section(addr):  # 如果结果中没有该节
            self.res.add_section(addr)  # 添加节
        for d in data:
            self.res.set(addr, d[0], d[1] + ':' + d[2])  # 设置配置项
            if self.flag_f == 1:  # 如果标志位为1
                print(d[0] + '=' + d[1] + ':' + d[2])  # 打印配置项

if __name__ == '__main__':  # 主程序入口
    main = Client_pq()  # 创建客户端实例
