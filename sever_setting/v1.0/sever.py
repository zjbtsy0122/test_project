# -*- coding: gbk -*-  # �����ļ�����ΪGBK
from socket import *  # ��socketģ���е�����������
import configparser  # �������ý�����ģ��

class Server_pq():  # �����������
    def __init__(self):  # ��ʼ������
        cfg = configparser.ConfigParser()  # �������ý���������
        cfg.read('s_cfg.ini')  # ��ȡ�����������ļ�
        host = cfg.get('server', 'host')  # ��ȡ������������ַ
        port = cfg.get('server', 'port')  # ��ȡ�������˿�
        self.bufsiz = int(cfg.get('server', 'bufsiz'))  # ��ȡ��������С
        self.ADDR = (host, int(port))  # ���÷�������ַ
        self.section = cfg.get('server', 'section').split(',')  # ��ȡ���ý������б�
        # self.section = ['jsdspxa_common', 'jsdspxa_credit', 'jsdspxgoldexch_common']
        self.item = ['���ص�ַ', '���ض˿�']  # �����������б�

    def get_data(self, path, section, item, file='TradeTrans_private.ini'):  # �Ӿ����ļ���ȡ����
        conf = configparser.ConfigParser()  # �������ý���������
        conf.read(path + file)  # ��ȡָ��·���µ������ļ�
        geted_data = []  # ��ʼ����ȡ�������б�
        for i in range(len(section)):  # �������ý�
            value = []  # ��ʼ��ֵ�б�
            for j in range(len(item)):  # ����������
                value.append(conf.get(section[i], item[j]))  # ��ȡ����ֵ
            geted_data.append([section[i], value])  # ��ӽں�ֵ�������б�
        return geted_data  # ���ػ�ȡ������

    def change_aryy(self, data):  # ����ת�ַ���
        for i in range(len(data)):  # ��������
            data[i][1] = '-'.join(data[i][1])  # ��ֵ�б�ת��Ϊ�ַ���
            data[i] = '-'.join(data[i])  # ���ں�ֵת��Ϊ�ַ���
        data = ','.join(data)  # �������������ӳ�һ���ַ���
        return data  # �����ַ���

    def start_server(self):  # ��������������
        udpSerSock = socket(AF_INET, SOCK_DGRAM)  # ����UDP�׽���
        print(self.ADDR)  # ��ӡ��������ַ
        udpSerSock.bind(self.ADDR)  # �󶨷�������ַ
        while True:
            print('waiting for message...')  # �ȴ���Ϣ
            data, addr = udpSerSock.recvfrom(self.bufsiz)  # ��������
            result = data.decode('utf-8')  # ��������
            print(result)  # ��ӡ���յ�������
            result = self.select_action(result)  # ѡ�����
            udpSerSock.sendto(result.encode(), addr)  # ������Ӧ
            print('...received from and returned to:', addr)  # ��ӡ�ͻ��˵�ַ

    def select_action(self, data):  # ����ѡ�񷽷�
        if data[0:5] == 'Find-':  # �������Ϊ����
            result = self.get_data(data[5:], self.section, self.item)  # ��ȡ����
            result = self.change_aryy(result)  # ת�����ݸ�ʽ
            # print(result)
            return result  # ���ؽ��
        else:
            print("NO!!!")  # ������Ч

if __name__ == '__main__':  # ���������
    main = Server_pq()  # ����������ʵ��
    main.start_server()  # ����������
