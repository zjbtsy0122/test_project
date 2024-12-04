import configparser


file_path=r"D:\testclient\client.ini"
config = configparser.ConfigParser(strict=False)
config.read(file_path, encoding='gbk')
config.set('ClientComm_Common', 'deal_second', str('1000').strip())
with open(file_path, 'w', encoding='gbk') as configfile:
    config.write(configfile)