# -*- coding: gbk -*-  # �����ļ�����ΪGBK
from socket import *  # ��socketģ���е�����������
import configparser  # �������ý�����ģ��

from pathlib import Path  # ����·��ģ��
import datetime  # ��������ʱ��ģ��


# ��������ļ���
def create_result_folder():
    Path("result").mkdir(parents=True, exist_ok=True)


# ��ȡyyyymmdd��ʽ������
def get_date():
    return datetime.datetime.now().strftime('%Y%m%d')


# ��ȡresult�ļ����µ���yyyymmdd��ͷ���ļ��е�����
def get_folder_count():
    return len([name for name in Path("result").iterdir() if name.is_dir() and name.name.startswith(get_date())])


# ���������yyyymmdd��ͷ���ļ��У��򷵻����������Ǹ�
# ���������ļ��� yyyymmdd-n nΪ���촴���ĵ�n���ļ���
def get_latest_folder():
    return sorted([name for name in Path("result").iterdir() if name.is_dir() and name.name.startswith(get_date())])[-1]


# �Ƚ������ļ��Ĳ�ͬ
def compare_config_files(previous_result_folder, current_result_folder):
    add_part = dict()
    delete_part = dict()
    change_part = dict()


    # ��ȡ֮ǰ�Ľ�������ļ�
    previous_result = configparser.ConfigParser()
    previous_result.read(previous_result_folder / 'result.ini', encoding='gbk')

    # ��ȡ��ǰ�Ľ�������ļ�
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


# ����Ƚϳ��Ĳ�ͬ
def save_diff(add_part, delete_part, change_part, current_result_folder):

    if add_part or delete_part or change_part:
        diff_folder = current_result_folder / 'diff'
        diff_folder.mkdir(parents=True, exist_ok=True)

        # ���������Ĳ���
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


# ��ӡ��ͬ
def print_diff(add_part, delete_part, change_part):
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


class Client_pq():  # ����ͻ�����
    def __init__(self):  # ��ʼ������
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

    def Find(self, section=[]):  # ���ҷ���
        sections = []  # ��ʼ�����б�
        cfg = configparser.ConfigParser()  # �������ý���������
        cfg.read('c_cfg.ini', encoding='utf-8')  # ��ȡ�����ļ���ȷ��ʹ��GBK����
        self.res = configparser.ConfigParser()  # ����������ý���������
        self.res.read('result.ini', encoding='gbk')  # ��ȡ��������ļ���ȷ��ʹ��GBK����
        if not section:  # ���û��ָ����
            sections = cfg.sections()  # ��ȡ���н�����
        else:
            if not cfg.has_section(section):  # ���ָ���ڲ�����
                return('No this server or port!')  # ���ش�����Ϣ
            else:
                sections.append(section)  # ���ָ����
        for s in sections:  # �������н�
            host = cfg.get(s, 'host')  # ��ȡ������ַ
            port = cfg.get(s, 'port')  # ��ȡ�˿ں�
            bufsiz = int(cfg.get(s, 'bufsiz'))  # ��ȡ��������С
            ADDR = (host, int(port))  # ��������ַ
            path = cfg.get(s, 'path')  # ��ȡ·��
            result = self.start_server(ADDR, bufsiz, path)  # ��������������ȡ���
            self.write_in(s, result)  # �����д���ļ�

        # �Ƿ񱣴洦��
        save_do = input('�Ƿ񱣴�����, ������Y/[N]: ')  # ��ʾ�û�����ָ��
        if save_do.upper() == 'Y':
            print('��ѡ�񱣴�����')
            self.handle_save_action()
        else:
            print('δ��������')

        return('Complete!!!')  # ���������Ϣ


    def start_server(self, ADDR, bufsiz, path):  # ��������������
        result = []  # ��ʼ������б�
        udpCliSock = socket(AF_INET, SOCK_DGRAM)  # ����UDP�׽���
        try:
            path = 'Find-' + path  # ��������·��
            print(f"Sending request: {path} to {ADDR}")  # ��ӡ���͵�����·���͵�ַ
            udpCliSock.sendto(path.encode(), ADDR)  # ��������
            data, ADDR = udpCliSock.recvfrom(bufsiz)  # ��������
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
            udpCliSock.close()  # �ر��׽���
        return result  # ���ؽ��


    def handle_save_action(self):
        # 20240906 �޸�
        # ��ǰ�����ļ���ǰ׺
        date_folder_prefix = get_date()
        # ��ǰ�����ļ�������
        create_result_folder()  # ��������ļ���, �Է�ɾ��
        folder_count = get_folder_count()

        # ��� folder_count > 0��ȡ���������һ��
        previous_result_folder = get_latest_folder() if folder_count > 0 else None

        # ��ǰ�����ļ���·��
        date_folder_path = Path("result") / f"{date_folder_prefix}-{folder_count + 1}"
        # ������ǰ�����ļ���
        date_folder_path.mkdir(parents=True, exist_ok=True)
        # �����������ļ�
        with open(date_folder_path / 'result.ini', 'w', encoding='gbk') as configfile:
            self.res.write(configfile)

        # �Ƚ�ǰ���ѯ�Ĳ���
        if folder_count > 0:
            current_result_folder = date_folder_path
            # �Ƚ������ļ��Ĳ�ͬ
            add_part, delete_part, change_part = compare_config_files(previous_result_folder, current_result_folder)
            # ����Ƚϳ��Ĳ�ͬ
            save_diff(add_part, delete_part, change_part, current_result_folder)

            if add_part or delete_part or change_part:
                print("�ȶԲ�һ��")
                print_diff(add_part, delete_part, change_part)
            else:
                print("�ȶ�һ��")


    def write_in(self, addr, data):  # д��������
        if not self.res.has_section(addr):  # ��������û�иý�
            self.res.add_section(addr)  # ��ӽ�
        for d in data:
            if len(d) == 3:  # ������ݳ���
                self.res.set(addr, d[0], d[1] + ':' + d[2])  # ����������
                if self.flag_f == 1:
                    print(d[0] + '=' + d[1] + ':' + d[2])  # ��ӡ������

if __name__ == '__main__':  # ���������
    # ��������ļ���
    create_result_folder()
    main = Client_pq()  # �����ͻ���ʵ��
