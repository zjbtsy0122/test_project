import configparser


class Test:

    def get_section_data(self, section_name):
        config = configparser.ConfigParser()
        config.read(r'./data.ini')
        return config[section_name]


    def huoqu(self):
        section_name = input("Enter the section name: ")

        section_data = self.get_section_data(section_name)



        print(section_data['t'])

if __name__ == '__main__':
    T =Test()
    T.huoqu()
