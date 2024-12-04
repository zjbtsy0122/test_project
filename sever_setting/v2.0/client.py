# -*- coding: gbk -*-  # 设置文件编码为GBK
from socket import *  # 从socket模块中导入所有内容
import configparser  # 导入配置解析器模块

from pathlib import Path  # 导入路径模块
import datetime  # 导入日期时间模块


# 创建结果文件夹
def create_result_folder():
    Path("result").mkdir(parents=True, exist_ok=True)


# 获取yyyymmdd格式的日期
def get_date():
    return datetime.datetime.now().strftime('%Y%m%d')


# 获取result文件夹下的以yyyymmdd开头的文件夹的数量
def get_folder_count():
    return len([name for name in Path("result").iterdir() if name.is_dir() and name.name.startswith(get_date())])


# 如果存在以yyyymmdd开头的文件夹，则返回最晚创建的那个
# 最晚创建的文件夹 yyyymmdd-n n为当天创建的第n个文件夹
def get_latest_folder():
    return sorted([name for name in Path("result").iterdir() if name.is_dir() and name.name.startswith(get_date())])[-1]


# 比较配置文件的不同
def compare_config_files(previous_result_folder, current_result_folder):
    add_part = dict()
    delete_part = dict()
    change_part = dict()


    # 读取之前的结果配置文件
    previous_result = configparser.ConfigParser()
    previous_result.read(previous_result_folder / 'result.ini', encoding='gbk')

    # 读取当前的结果配置文件
    current_result = configparser.ConfigParser()
    current_result.read(current_result_folder / 'result.ini', encoding='gbk')

    # compare current_result with previous_result
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

    # compare previous_result with current_result
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


# 保存比较出的不同
def save_diff(add_part, delete_part, change_part, current_result_folder):

    if add_part or delete_part or change_part:
        diff_folder = current_result_folder / 'diff'
        diff_folder.mkdir(parents=True, exist_ok=True)

        # 保存新增的部分
        if add_part:
            with open(diff_folder / 'add.ini', 'w', encoding='gbk') as configfile:
                add_config = configparser.ConfigParser()
                for section, options in add_part.items():
                    add_config.add_section(section)
                    for option, value in options.items():
                        add_config.set(section, option, value)
                add_config.write(configfile)

        if delete_part:
            with open(diff_folder / 'delete.ini', 'w', encoding='gbk') as configfile:
                delete_config = configparser.ConfigParser()
                for section, options in delete_part.items():
                    delete_config.add_section(section)
                    for option, value in options.items():
                        delete_config.set(section, option, value)
                delete_config.write(configfile)

        if change_part:
            with open(diff_folder / 'change.ini', 'w', encoding='gbk') as configfile:
                change_config = configparser.ConfigParser()
                for section, options in change_part.items():
                    change_config.add_section(section)
                    for option, value in options.items():
                        change_config.set(section, option, value)
                change_config.write(configfile)


# 打印不同
def print_diff(add_part, delete_part, change_part):
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


class Client_pq():  # 定义客户端类
    def __init__(self):  # 初始化方法
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

    def Find(self, section=[]):  # 查找方法
        sections = []  # 初始化节列表
        cfg = configparser.ConfigParser()  # 创建配置解析器对象
        cfg.read('c_cfg.ini', encoding='utf-8')  # 读取配置文件，确保使用GBK编码
        self.res = configparser.ConfigParser()  # 创建结果配置解析器对象
        self.res.read('result.ini', encoding='gbk')  # 读取结果配置文件，确保使用GBK编码
        if not section:  # 如果没有指定节
            sections = cfg.sections()  # 获取所有节名称
        else:
            if not cfg.has_section(section):  # 如果指定节不存在
                return('No this server or port!')  # 返回错误信息
            else:
                sections.append(section)  # 添加指定节
        for s in sections:  # 遍历所有节
            host = cfg.get(s, 'host')  # 获取主机地址
            port = cfg.get(s, 'port')  # 获取端口号
            bufsiz = int(cfg.get(s, 'bufsiz'))  # 获取缓冲区大小
            ADDR = (host, int(port))  # 服务器地址
            path = cfg.get(s, 'path')  # 获取路径
            result = self.start_server(ADDR, bufsiz, path)  # 启动服务器并获取结果
            self.write_in(s, result)  # 将结果写入文件

        # 是否保存处理
        save_do = input('是否保存数据, 请输入Y/[N]: ')  # 提示用户输入指令
        if save_do.upper() == 'Y':
            print('已选择保存数据')
            self.handle_save_action()
        else:
            print('未保存数据')

        return('Complete!!!')  # 返回完成信息


    def start_server(self, ADDR, bufsiz, path):  # 启动服务器方法
        result = []  # 初始化结果列表
        udpCliSock = socket(AF_INET, SOCK_DGRAM)  # 创建UDP套接字
        try:
            path = 'Find-' + path  # 构造请求路径
            print(f"Sending request: {path} to {ADDR}")  # 打印发送的请求路径和地址
            udpCliSock.sendto(path.encode(), ADDR)  # 发送请求
            data, ADDR = udpCliSock.recvfrom(bufsiz)  # 接收数据
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
            udpCliSock.close()  # 关闭套接字
        return result  # 返回结果


    def handle_save_action(self):
        # 20240906 修改
        # 当前日期文件夹前缀
        date_folder_prefix = get_date()
        # 当前日期文件夹数量
        create_result_folder()  # 创建结果文件夹, 以防删除
        folder_count = get_folder_count()

        # 如果 folder_count > 0，取最近创建的一个
        previous_result_folder = get_latest_folder() if folder_count > 0 else None

        # 当前日期文件夹路径
        date_folder_path = Path("result") / f"{date_folder_prefix}-{folder_count + 1}"
        # 创建当前日期文件夹
        date_folder_path.mkdir(parents=True, exist_ok=True)
        # 保存结果配置文件
        with open(date_folder_path / 'result.ini', 'w', encoding='gbk') as configfile:
            self.res.write(configfile)

        # 比较前后查询的差异
        if folder_count > 0:
            current_result_folder = date_folder_path
            # 比较配置文件的不同
            add_part, delete_part, change_part = compare_config_files(previous_result_folder, current_result_folder)
            # 保存比较出的不同
            save_diff(add_part, delete_part, change_part, current_result_folder)

            if add_part or delete_part or change_part:
                print("比对不一致")
                print_diff(add_part, delete_part, change_part)
            else:
                print("比对一致")


    def write_in(self, addr, data):  # 写入结果方法
        if not self.res.has_section(addr):  # 如果结果中没有该节
            self.res.add_section(addr)  # 添加节
        for d in data:
            if len(d) == 3:  # 检查数据长度
                self.res.set(addr, d[0], d[1] + ':' + d[2])  # 设置配置项
                if self.flag_f == 1:
                    print(d[0] + '=' + d[1] + ':' + d[2])  # 打印配置项

if __name__ == '__main__':  # 主程序入口
    # 创建结果文件夹
    create_result_folder()
    main = Client_pq()  # 创建客户端实例
