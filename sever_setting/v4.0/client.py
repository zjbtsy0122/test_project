import configparser
from socket import *


class Client_pq():


    def __init__(self,timeout=10):


        self.timeout = timeout

        while True:

            do = input("输入请求命令（Find）：")


            self.select_action(do)


    def select_action(self,data):

        if data == 'Find':
            print(self.find())
        elif data[0:5] =='Find_':
            print(self.find(data[5:]))
        else:
            print("有误！")




    def find(self,section=[]):

        sections =[]

        cfg =configparser.ConfigParser()
        cfg.read('c_cfg.ini',encoding='utf-8')
        self.res = configparser.ConfigParser()

        if not section :
            sections= cfg.sections()

        else:
            if not cfg.has_section(section):
                return ('no sever or port!')
            else:
                sections.append(section)

        for s in sections:
            host = cfg.get(s,'host')
            port = cfg.get(s,'port')
            bufsiz = int(cfg.get(s, 'bufsiz'))
            ADDR = (host, int(port))
            path = cfg.get(s, 'path')

            result = self.start_server(ADDR, bufsiz, path)

            self.write_in(s,result)

        return ('Complete!!!')


    def start_server(self, ADDR, bufsiz, path):  # 启动服务器方法
        result = []  # 初始化结果列表
        udpCliSock = socket(AF_INET, SOCK_DGRAM)  # 创建UDP套接字


        try:
            path = 'Find-' + path  # 构造请求路径
            print(f"Sending request: {path} to {ADDR}")
            udpCliSock.sendto(path.encode(), ADDR)  # 发送请求到服务器
            udpCliSock.settimeout(self.timeout)
            data, ADDR = udpCliSock.recvfrom(bufsiz)  # 接收服务器返回的数据

        except timeout:
            print('超时！')

        except Exception as e:

            print(f"发生异常: {e}")
        else:

            print(f"Received raw data: {data}")  # 打印接收到的原始数据
            data = data.decode('utf-8').strip().split(',')  # 解码并分割数据
            for d in data:
                parts = d.split('-')
                print(f"Parsed data parts: {parts}")  # 打印分割后的数据部分
                if len(parts) == 3:  # 检查数据格式是否正确
                    result.append(parts)  # 将数据添加到结果列表
                else:
                    print(f"Unexpected data format: {d}")  # 打印出错信息以便调试
        finally:
            udpCliSock.close()


        return result  # 返回结果

    def write_in(self, addr, data):

        if not self.res.has_section(addr):  # 如果结果中没有该节
            self.res.add_section(addr)

        for d in data:
            if len(d) == 3:  # 检查数据长度
                self.res.set(addr, d[0], d[1] + ':' + d[2])



if __name__ == '__main__':
    main = Client_pq()