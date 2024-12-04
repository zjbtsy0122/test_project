import configparser
import datetime
from pathlib import Path
from socket import *


class Client_pq():

    def __init__(self,result_folder="./result",timeout=10):

        self.timeout=timeout
        self.result_folder = result_folder  # 结果文件夹路径
        self.create_result_folder()  # 创建结果文件夹

        while True:
            do = input("请输入指令（Find）：")
            self.select_action(do)


    def select_action(self,data):

        if data == 'Find':
            print(self.find())
        elif data[0:5] == 'Find_':
            #172.190.117.203:6020（10环境-主系统-PC）
            print(self.find(data[5:]))
        else:
            print('无法识别')

    #Sending request: Find - D:\E海通财PC\trade主系统\TradeTrans\ to('172.190.117.203', 21563)
    #Received raw data: b'jsdspxa_common-172.192.64.163-19204,jsdspxa_credit-172.192.86.86-1700,jsdspxgoldexch_common-172.192.48.9-16800'

    def find(self,section=[]):

        sections = []
        cfg =configparser.ConfigParser()
        cfg.read('c_cfg.ini', encoding='utf-8')
        self.res = configparser.ConfigParser()
        if not cfg.sections():  # 配置文件有问题
            print("配置文件有问题，请检查！")
        if not section:  # 如果没有指定节
            sections = cfg.sections()  # 获取所有节名称
        else:
            if not cfg.has_section(section):
                return ('No this server or port!')
            else:
                sections.append(section)

        for s in sections:

            try:
                host = cfg.get(s,'host')
                port = cfg.get(s, 'port')
                bufsiz = int(cfg.get(s, 'bufsiz'))
                ADDR = (host, int(port))
                path = cfg.get(s, 'path')

                result = self.start_server(ADDR, bufsiz, path)

                if not result:
                    continue
                self.write_in(s, result)

            except Exception as e:
                print('-'*100)
                print(f"发生异常: {e}")
                continue

        if not self.res.sections():
            print("本次查询未获取到有效结果")
        else:
            self.handle_save_action()


        return ('Complete!!!')


    def start_server(self,ADDR, bufsiz, path):

        result =[]
        udpCliSock = socket(AF_INET, SOCK_DGRAM)

        try:
            path = 'Find-' + path
            print('-'*100)
            print(f"Sending request: {path} to {ADDR}")
            udpCliSock.sendto(path.encode(), ADDR)
            udpCliSock.settimeout(self.timeout)


        except timeout:
            print("超时！")
        except Exception as e:
            print(f"发生异常: {e}")
        else:
            data, ADDR = udpCliSock.recvfrom(bufsiz)
            print(f"Received raw data: {data}")
            # Received raw data: b'jsdspxa_common-172.192.64.163-19204,jsdspxa_credit-172.192.86.86-1700,jsdspxgoldexch_common-172.192.48.9-16800'
            data = data.decode('utf-8').strip().split(',')

            for d in data:
                result.append(d.split('-'))  # 将数据添加到结果列表
                # Parsed data parts: ['jsdspxa_common', '172.192.64.163', '19204']
                # Parsed data parts: ['jsdspxa_credit', '172.192.86.86', '1700']
                # Parsed data parts: ['jsdspxgoldexch_common', '172.192.48.9', '16800']

        finally:
            udpCliSock.close()

        return result  # 返回结果

    def write_in(self, addr, data):

        if not self.res.has_section(addr):  # 如果结果中没有该节
            self.res.add_section(addr)  # 添加节
        for d in data:
            if len(d) == 3:  # 检查数据长度
                self.res.set(addr, d[0], d[1] + ':' + d[2])  # 设置配置项


    def handle_save_action(self):

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

        # 比较当前结果与之前结果，当前结果为基准,没有的或者不一样的 就是新增或者修改的。
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

        # 比较之前结果与当前结果，之前结果为基准，当前文件数据不存在就是删除的。
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
            #('section1',{'option1':'value1','option2':'value2'})
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


    def create_result_folder(self):
        """
        创建结果文件夹
        :return:
        """
        Path(self.result_folder).mkdir(parents=True, exist_ok=True)

if __name__ == '__main__':
    main = Client_pq()