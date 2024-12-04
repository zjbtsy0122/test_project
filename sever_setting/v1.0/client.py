# -*- coding: gbk -*-  # �����ļ�����ΪGBK
from socket import *  # ��socketģ���е�����������
import configparser  # �������ý�����ģ��

class Client_pq():  # ����ͻ�����
    def __init__(self):  # ��ʼ������
        while True:  # ����ѭ��
            self.flag_f = 0  # ��־λ��ʼ��Ϊ0
            do = input('������ָ�Find����')  # ��ʾ�û�����ָ��
            self.select_action(do)  # ���ò���ѡ�񷽷�

    def select_action(self, data):  # ����ѡ�񷽷�
        if data == 'Find':  # �������Ϊ'Find'
            print(self.Find())  # ִ��Find��������ӡ���
        elif data[0:5] == 'Find_':  # ���������'Find_'��ͷ
            self.flag_f = 1  # ���ñ�־λΪ1
            print(self.Find(data[5:]))  # ִ��Find��������ӡ���
        else:
            print('�޷�ʶ��')  # ��ӡ�޷�ʶ�����ʾ

    def Find(self, section=[]):  # ���ҷ���
        sections = []  # ��ʼ�����б�
        cfg = configparser.ConfigParser()  # �������ý���������
        cfg.read('c_cfg.ini')  # ��ȡ�ͻ��������ļ�
        self.res = configparser.ConfigParser()  # ����������ý���������
        self.res.read('result.ini')  # ��ȡ��������ļ�
        if section == []:  # ���û��ָ����
            sections = cfg.sections()  # ��ȡ���н�����
        else:
            if not cfg.has_section(section):  # ���ָ���ڲ�����
                return('No this server or port!')  # ���ش�����Ϣ
            else:
                sections.append(section)  # ��ָ������ӵ��б�
        for s in sections:  # �������н�
            host = cfg.get(s, 'host')  # ��ȡ������ַ
            port = cfg.get(s, 'port')  # ��ȡ�˿ں�
            bufsiz = int(cfg.get(s, 'bufsiz'))  # ��ȡ��������С
            ADDR = (host, int(port))  # ������������ַ
            # print(ADDR)
            path = cfg.get(s, 'path')  # ��ȡ·��
            # section = cfg.get(s, 'section').split(',')
            result = self.start_server(ADDR, bufsiz, path)  # ��������������ȡ���
            self.write_in(s, result)  # �����д�������ļ�
        self.res.write(open('result.ini', 'w'))  # �����������ļ�
        return('Complete!!!')  # ���������Ϣ

    def start_server(self, ADDR, bufsiz, path):  # ��������������
        result = []  # ��ʼ������б�
        udpCliSock = socket(AF_INET, SOCK_DGRAM)  # ����UDP�׽���
        while True:
            path = 'Find-' + path  # ��������·��
            udpCliSock.sendto(path.encode(), ADDR)  # �������󵽷�����
            data, ADDR = udpCliSock.recvfrom(bufsiz)  # ���շ��������ص�����
            data = data.decode('utf-8').split(',')  # ���벢�ָ�����
            for d in data:
                result.append(d.split('-'))  # ��������ӵ�����б�
            # print(result)
            return result  # ���ؽ��
        # udpCliSock.close()

    def write_in(self, addr, data):  # д��������
        # addrs=addr[0]+':'+str(addr[1])
        if not self.res.has_section(addr):  # ��������û�иý�
            self.res.add_section(addr)  # ��ӽ�
        for d in data:
            self.res.set(addr, d[0], d[1] + ':' + d[2])  # ����������
            if self.flag_f == 1:  # �����־λΪ1
                print(d[0] + '=' + d[1] + ':' + d[2])  # ��ӡ������

if __name__ == '__main__':  # ���������
    main = Client_pq()  # �����ͻ���ʵ��
