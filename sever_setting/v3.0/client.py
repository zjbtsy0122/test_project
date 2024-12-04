# -*- coding: gbk -*-  # 设置文件编码为GBK
import os
import signal
from socket import *  # 从socket模块中导入所有内容
import configparser  # 导入配置解析器模块
import multiprocessing
from pathlib import Path  # 导入路径模块
import datetime  # 导入日期时间模块
import sys

class Client_pq():  # 定义客户端类

    def __init__(self, result_folder="./result", timeout=20):  # 初始化方法,参数方便修改

        self.result_folder = result_folder  # 结果文件夹路径
        self.timeout = timeout  # 超时时间
        self.create_result_folder()  # 创建结果文件夹


        while True:  # 无限循环
            self.flag_f = 0  # 标记初始化
            do = input('请输入指令（Find）：')  # 提示用户输入指令
            self.select_action(do)  # 调用操作选择方法


    def select_action(self, data):  # 操作选择方法
        if data == 'Find':  # 如果指令为'Find'
            print(self.Find())  # 调用Find方法并打印结果
        elif data[0:5] == 'Find_':  # 如果指令以'Find_'开头
            self.flag_f = 1  # 设置标记
            print(self.Find(data[5:]))  # 调用Find方法并打印结果
        else:
            print('无法识别')  # 无法识别的指令

    def Find(self, section=[]):
        """
        查找指定节的服务器配置并启动连接。
        参数:
        section (list): 要查找的节名称列表。如果未指定，将查找所有节。
        返回:
        str: 完成信息或错误信息。
        功能:
        1. 读取配置文件 'c_cfg.ini'。
        2. 如果未指定节，则获取所有节名称。
        3. 如果指定的节不存在，返回错误信息。
        4. 遍历所有节，获取主机地址、端口号和缓冲区大小。
        5. 启动服务器连接并处理结果。
        6. 如果没有有效结果，打印提示信息。
        7. 处理保存操作（如果有有效结果）。
        """
        sections = []  # 初始化节列表
        cfg = configparser.ConfigParser()  # 创建配置解析器对象
        cfg.read('c_cfg.ini', encoding='utf-8')  # 读取配置文件，确保使用GBK编码
        self.res = configparser.ConfigParser()  # 创建结果配置解析器对象
        if not section:  # 如果没有指定节
            sections = cfg.sections()  # 获取所有节名称
        else:
            if not cfg.has_section(section):  # 如果指定节不存在
                return ('No this server or port!')  # 返回错误信息
            else:
                sections.append(section)  # 添加指定节

        for s in sections:  # 遍历所有节

            host = cfg.get(s, 'host')  # 获取主机地址
            port = cfg.get(s, 'port')  # 获取端口号
            bufsiz = int(cfg.get(s, 'bufsiz'))  # 获取缓冲区大小
            ADDR = (host, int(port))  # 服务器地址
            path = cfg.get(s, 'path')  # 获取路径

            result = self.start_server(ADDR, bufsiz, path)  # 启动服务器并获取结果

            if not result:
                continue
            self.write_in(s, result)  # 将结果写入文件

        if not self.res.sections():
            print("本次查询未获取到有效结果")
        else:
            self.handle_save_action()  # 保存结果并比较结果，让客户判断是否要保存

        return ('Complete!!!')  # 返回完成信息

    def start_server(self, ADDR, bufsiz, path):
        result = []  # 初始化结果列表
        udpCliSock = socket(AF_INET, SOCK_DGRAM)  # 创建 UDP 套接字

        try:
            path = 'Find-' + path  # 构造请求路径
            print(f"Sending request: {path} to {ADDR}")  # 打印发送的请求路径和地址
            udpCliSock.sendto(path.encode(), ADDR)  # 发送请求
            # 设置超时时间（这里设置为 5 秒，可根据实际调整）
            udpCliSock.settimeout(self.timeout)
            data, ADDR = udpCliSock.recvfrom(bufsiz)  # 接收数据
        except timeout:
            print("连接超时")
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

        return result

    def write_in(self, addr, data):
        """
        :param addr: 要写入的节的地址
        :param data: 包含要写入的数据的列表，每个数据项应为长度3的列表
        :return:
        功能：
            -检查结果中是否存在指定的节，如果不存在则添加该节。
            -遍历数据列表，将每个数据项的第一个元素作为配置项的键，第二和第三个元素组合成值并设置。
            -如果flag_f为1，则打印配置项。
        """
        if not self.res.has_section(addr):  # 如果结果中没有该节
            self.res.add_section(addr)  # 添加节
        for d in data:
            if len(d) == 3:  # 检查数据长度
                self.res.set(addr, d[0], d[1] + ':' + d[2])  # 设置配置项
                if self.flag_f == 1:
                    print(d[0] + '=' + d[1] + ':' + d[2])  # 打印配置项

    def handle_save_action(self):
        """
        获取最近结果文件并生成当前时间的结果文件路径。
        保存结果配置文件。
        比较前后查询差异，并更具用户输入决定是否保存结果。
        """
        # 获取最近的结果文件
        last_result_file_path = self.get_last_result_file_path()

        current_datetime = self.get_current_datetime()
        result_file_path = f"{self.result_folder}/{current_datetime}-result.ini"
        print(f"last_result_file_path is {last_result_file_path}, result_file_path is {result_file_path}")
        # 保存结果配置文件
        with open(result_file_path, 'w', encoding='gbk') as configfile:
            self.res.write(configfile)

    # 比较前后查询的差异
        if last_result_file_path: #如果有之前的文件
            # 比较配置文件的不同
            add_part, delete_part, change_part = self.compare_config_files(last_result_file_path, result_file_path)
            if add_part or delete_part or change_part:
                print("本次查询结果与上次查询结果存在差异,差异详情如下:")
                self.print_result_diff(add_part, delete_part, change_part)

                # 是否保存处理
                save_do = input('是否保存数据, 请输入Y/[N]: ')  # 提示用户输入指令
                if save_do.upper() == 'Y':
                    print('本次查询结果已保存')
                else:
                    Path(f'{result_file_path}').unlink()
                    print('本次查询结果不保存')
            else:
                print("本次查询结果与上次查询结果无差异，不保存")
                Path(f'{result_file_path}').unlink()
        else:
            print("本次查询结果如下:")
            with Path(result_file_path).open('r') as f:
                content = f.read()
                print(content)

            save_do = input('是否保存数据, 请输入Y/[N]: ')  # 提示用户输入指令
            if save_do.upper() == 'Y':
                print('本次查询结果已保存')
            else:
                Path(f'{result_file_path}').unlink()
                print('本次查询结果不保存')


    @staticmethod
    def get_current_datetime():
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    @staticmethod
    def compare_config_files(last_result_file_path, current_result_file_path):
        """
        比较文件差异
        :param current_result_folder:
        :return:
        """
        add_part = dict()
        delete_part = dict()
        change_part = dict()

        # 读取之前的结果配置文件
        previous_result = configparser.ConfigParser()
        previous_result.read(last_result_file_path, encoding='gbk')

        # 读取当前的结果配置文件
        current_result = configparser.ConfigParser()
        current_result.read(current_result_file_path, encoding='gbk')

        # 比较当前结果与之前结果，当前结果为基准
        for section in current_result.sections():
            if not previous_result.has_section(section):
                add_part[section] = dict(current_result.items(section))
            else:
                for option in current_result.options(section):
                    if not previous_result.has_option(section, option):
                        if section not in add_part:
                            add_part[section] = dict()
                        add_part[section][option] = current_result.get(section, option)
                    elif previous_result.get(section, option) != current_result.get(section, option):
                        if section not in change_part:
                            change_part[section] = dict()
                        change_part[section][option] = current_result.get(section, option)

        # 比较之前结果与当前结果，之前结果为基准
        for section in previous_result.sections():
            if not current_result.has_section(section):
                delete_part[section] = dict(previous_result.items(section))
            else:
                for option in previous_result.options(section):
                    if not current_result.has_option(section, option):
                        if section not in delete_part:
                            delete_part[section] = dict()
                        delete_part[section][option] = previous_result.get(section, option)

        return add_part, delete_part, change_part

    @staticmethod
    def print_result_diff(add_part, delete_part, change_part):
        # 打印新增的部分
        if add_part:
            print("新增的部分：")
            for section, options in add_part.items():
                print(f"{section}")
                for option, value in options.items():
                    print(f"{option}={value}")

        # 打印删除的部分
        if delete_part:
            print("删除的部分：")
            for section, options in delete_part.items():
                print(f"{section}")
                for option, value in options.items():
                    print(f"{option}={value}")

        # 打印修改的部分
        if change_part:
            print("修改的部分：")
            for section, options in change_part.items():
                print(f"{section}")
                for option, value in options.items():
                    print(f"{option}={value}")

    def get_last_result_file_path(self):
        """
        获取最近的结果文件
        :return:
        """
        result_file_list = [file.name.split("-")[0] for file in Path(self.result_folder).iterdir() if file.is_file()]
        if not result_file_list:
            return None
        last_result_file_name = sorted(result_file_list)[-1]

        return f"{self.result_folder}/{last_result_file_name}-result.ini"

    def create_result_folder(self):
        """
        创建结果文件夹
        :return: 
        """
        Path(self.result_folder).mkdir(parents=True, exist_ok=True)


if __name__ == '__main__':  # 主程序入口

    main = Client_pq()  # 创建客户端实例
    def cleanup_files(result_folder):
        for file in Path(result_folder).glob('*-result.ini'):
            file.unlink()
        print("已删除")
    def signal_handler(signum,frame):
        cleanup_files(main.result_folder)
        os.exit(0)

    if __name__ == '__main__':
        signal.signal(signal.SIGINT,signal_handler)
        signal.signal(signal.SIGTERM,signal_handler)
        process = multiprocessing.Process(target=signal_handler,args=(None,None))
        process.start()