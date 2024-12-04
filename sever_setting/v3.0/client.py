# -*- coding: gbk -*-  # �����ļ�����ΪGBK
import os
import signal
from socket import *  # ��socketģ���е�����������
import configparser  # �������ý�����ģ��
import multiprocessing
from pathlib import Path  # ����·��ģ��
import datetime  # ��������ʱ��ģ��
import sys

class Client_pq():  # ����ͻ�����

    def __init__(self, result_folder="./result", timeout=20):  # ��ʼ������,���������޸�

        self.result_folder = result_folder  # ����ļ���·��
        self.timeout = timeout  # ��ʱʱ��
        self.create_result_folder()  # ��������ļ���


        while True:  # ����ѭ��
            self.flag_f = 0  # ��ǳ�ʼ��
            do = input('������ָ�Find����')  # ��ʾ�û�����ָ��
            self.select_action(do)  # ���ò���ѡ�񷽷�


    def select_action(self, data):  # ����ѡ�񷽷�
        if data == 'Find':  # ���ָ��Ϊ'Find'
            print(self.Find())  # ����Find��������ӡ���
        elif data[0:5] == 'Find_':  # ���ָ����'Find_'��ͷ
            self.flag_f = 1  # ���ñ��
            print(self.Find(data[5:]))  # ����Find��������ӡ���
        else:
            print('�޷�ʶ��')  # �޷�ʶ���ָ��

    def Find(self, section=[]):
        """
        ����ָ���ڵķ��������ò��������ӡ�
        ����:
        section (list): Ҫ���ҵĽ������б����δָ�������������нڡ�
        ����:
        str: �����Ϣ�������Ϣ��
        ����:
        1. ��ȡ�����ļ� 'c_cfg.ini'��
        2. ���δָ���ڣ����ȡ���н����ơ�
        3. ���ָ���Ľڲ����ڣ����ش�����Ϣ��
        4. �������нڣ���ȡ������ַ���˿ںźͻ�������С��
        5. �������������Ӳ���������
        6. ���û����Ч�������ӡ��ʾ��Ϣ��
        7. ������������������Ч�������
        """
        sections = []  # ��ʼ�����б�
        cfg = configparser.ConfigParser()  # �������ý���������
        cfg.read('c_cfg.ini', encoding='utf-8')  # ��ȡ�����ļ���ȷ��ʹ��GBK����
        self.res = configparser.ConfigParser()  # ����������ý���������
        if not section:  # ���û��ָ����
            sections = cfg.sections()  # ��ȡ���н�����
        else:
            if not cfg.has_section(section):  # ���ָ���ڲ�����
                return ('No this server or port!')  # ���ش�����Ϣ
            else:
                sections.append(section)  # ���ָ����

        for s in sections:  # �������н�

            host = cfg.get(s, 'host')  # ��ȡ������ַ
            port = cfg.get(s, 'port')  # ��ȡ�˿ں�
            bufsiz = int(cfg.get(s, 'bufsiz'))  # ��ȡ��������С
            ADDR = (host, int(port))  # ��������ַ
            path = cfg.get(s, 'path')  # ��ȡ·��

            result = self.start_server(ADDR, bufsiz, path)  # ��������������ȡ���

            if not result:
                continue
            self.write_in(s, result)  # �����д���ļ�

        if not self.res.sections():
            print("���β�ѯδ��ȡ����Ч���")
        else:
            self.handle_save_action()  # ���������ȽϽ�����ÿͻ��ж��Ƿ�Ҫ����

        return ('Complete!!!')  # ���������Ϣ

    def start_server(self, ADDR, bufsiz, path):
        result = []  # ��ʼ������б�
        udpCliSock = socket(AF_INET, SOCK_DGRAM)  # ���� UDP �׽���

        try:
            path = 'Find-' + path  # ��������·��
            print(f"Sending request: {path} to {ADDR}")  # ��ӡ���͵�����·���͵�ַ
            udpCliSock.sendto(path.encode(), ADDR)  # ��������
            # ���ó�ʱʱ�䣨��������Ϊ 5 �룬�ɸ���ʵ�ʵ�����
            udpCliSock.settimeout(self.timeout)
            data, ADDR = udpCliSock.recvfrom(bufsiz)  # ��������
        except timeout:
            print("���ӳ�ʱ")
        except Exception as e:
            print(f"�����쳣: {e}")
        else:
            print(f"Received raw data: {data}")  # ��ӡ���յ���ԭʼ����
            data = data.decode('utf-8').strip().split(',')  # ���벢�ָ�����
            for d in data:
                parts = d.split('-')
                print(f"Parsed data parts: {parts}")  # ��ӡ�ָ������ݲ���
                if len(parts) == 3:  # ������ݸ�ʽ�Ƿ���ȷ
                    result.append(parts)  # ��������ӵ�����б�
                else:
                    print(f"Unexpected data format: {d}")  # ��ӡ������Ϣ�Ա����
        finally:
            udpCliSock.close()

        return result

    def write_in(self, addr, data):
        """
        :param addr: Ҫд��Ľڵĵ�ַ
        :param data: ����Ҫд������ݵ��б�ÿ��������ӦΪ����3���б�
        :return:
        ���ܣ�
            -��������Ƿ����ָ���Ľڣ��������������Ӹýڡ�
            -���������б���ÿ��������ĵ�һ��Ԫ����Ϊ������ļ����ڶ��͵�����Ԫ����ϳ�ֵ�����á�
            -���flag_fΪ1�����ӡ�����
        """
        if not self.res.has_section(addr):  # ��������û�иý�
            self.res.add_section(addr)  # ��ӽ�
        for d in data:
            if len(d) == 3:  # ������ݳ���
                self.res.set(addr, d[0], d[1] + ':' + d[2])  # ����������
                if self.flag_f == 1:
                    print(d[0] + '=' + d[1] + ':' + d[2])  # ��ӡ������

    def handle_save_action(self):
        """
        ��ȡ�������ļ������ɵ�ǰʱ��Ľ���ļ�·����
        �����������ļ���
        �Ƚ�ǰ���ѯ���죬�������û���������Ƿ񱣴�����
        """
        # ��ȡ����Ľ���ļ�
        last_result_file_path = self.get_last_result_file_path()

        current_datetime = self.get_current_datetime()
        result_file_path = f"{self.result_folder}/{current_datetime}-result.ini"
        print(f"last_result_file_path is {last_result_file_path}, result_file_path is {result_file_path}")
        # �����������ļ�
        with open(result_file_path, 'w', encoding='gbk') as configfile:
            self.res.write(configfile)

    # �Ƚ�ǰ���ѯ�Ĳ���
        if last_result_file_path: #�����֮ǰ���ļ�
            # �Ƚ������ļ��Ĳ�ͬ
            add_part, delete_part, change_part = self.compare_config_files(last_result_file_path, result_file_path)
            if add_part or delete_part or change_part:
                print("���β�ѯ������ϴβ�ѯ������ڲ���,������������:")
                self.print_result_diff(add_part, delete_part, change_part)

                # �Ƿ񱣴洦��
                save_do = input('�Ƿ񱣴�����, ������Y/[N]: ')  # ��ʾ�û�����ָ��
                if save_do.upper() == 'Y':
                    print('���β�ѯ����ѱ���')
                else:
                    Path(f'{result_file_path}').unlink()
                    print('���β�ѯ���������')
            else:
                print("���β�ѯ������ϴβ�ѯ����޲��죬������")
                Path(f'{result_file_path}').unlink()
        else:
            print("���β�ѯ�������:")
            with Path(result_file_path).open('r') as f:
                content = f.read()
                print(content)

            save_do = input('�Ƿ񱣴�����, ������Y/[N]: ')  # ��ʾ�û�����ָ��
            if save_do.upper() == 'Y':
                print('���β�ѯ����ѱ���')
            else:
                Path(f'{result_file_path}').unlink()
                print('���β�ѯ���������')


    @staticmethod
    def get_current_datetime():
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    @staticmethod
    def compare_config_files(last_result_file_path, current_result_file_path):
        """
        �Ƚ��ļ�����
        :param current_result_folder:
        :return:
        """
        add_part = dict()
        delete_part = dict()
        change_part = dict()

        # ��ȡ֮ǰ�Ľ�������ļ�
        previous_result = configparser.ConfigParser()
        previous_result.read(last_result_file_path, encoding='gbk')

        # ��ȡ��ǰ�Ľ�������ļ�
        current_result = configparser.ConfigParser()
        current_result.read(current_result_file_path, encoding='gbk')

        # �Ƚϵ�ǰ�����֮ǰ�������ǰ���Ϊ��׼
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

        # �Ƚ�֮ǰ����뵱ǰ�����֮ǰ���Ϊ��׼
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
        # ��ӡ�����Ĳ���
        if add_part:
            print("�����Ĳ��֣�")
            for section, options in add_part.items():
                print(f"{section}")
                for option, value in options.items():
                    print(f"{option}={value}")

        # ��ӡɾ���Ĳ���
        if delete_part:
            print("ɾ���Ĳ��֣�")
            for section, options in delete_part.items():
                print(f"{section}")
                for option, value in options.items():
                    print(f"{option}={value}")

        # ��ӡ�޸ĵĲ���
        if change_part:
            print("�޸ĵĲ��֣�")
            for section, options in change_part.items():
                print(f"{section}")
                for option, value in options.items():
                    print(f"{option}={value}")

    def get_last_result_file_path(self):
        """
        ��ȡ����Ľ���ļ�
        :return:
        """
        result_file_list = [file.name.split("-")[0] for file in Path(self.result_folder).iterdir() if file.is_file()]
        if not result_file_list:
            return None
        last_result_file_name = sorted(result_file_list)[-1]

        return f"{self.result_folder}/{last_result_file_name}-result.ini"

    def create_result_folder(self):
        """
        ��������ļ���
        :return: 
        """
        Path(self.result_folder).mkdir(parents=True, exist_ok=True)


if __name__ == '__main__':  # ���������

    main = Client_pq()  # �����ͻ���ʵ��
    def cleanup_files(result_folder):
        for file in Path(result_folder).glob('*-result.ini'):
            file.unlink()
        print("��ɾ��")
    def signal_handler(signum,frame):
        cleanup_files(main.result_folder)
        os.exit(0)

    if __name__ == '__main__':
        signal.signal(signal.SIGINT,signal_handler)
        signal.signal(signal.SIGTERM,signal_handler)
        process = multiprocessing.Process(target=signal_handler,args=(None,None))
        process.start()