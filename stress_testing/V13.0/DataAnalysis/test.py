import re
from datetime import datetime

def parse_log(log_file, start_time, end_time):
    section_data = {}
    with open(log_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        in_search_section = False
        for line in lines:
            timestamp_match = re.match(r'\[ERROR\](\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
            if timestamp_match:
                timestamp = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')
                if start_time <= timestamp <= end_time:
                    if "Search计划开始了" in line:
                        in_search_section = True
                    elif "Search计划结束了！" in line:
                        in_search_section = False
                    
                    if in_search_section and "增压" in line:
                        match = re.search(r'(\d+)次增压，req_num的当前值为: (\d+)', line)
                        if match:
                            count = match.group(1)
                            req_num = match.group(2)
                            section_name = f"S{timestamp.strftime('%Y%m%d%H%M%S')}_为:{req_num}"
                            section_data[section_name] = {'st': timestamp.strftime('%Y-%m-%d %H:%M:%S'), 't': req_num}
    
    return section_data

def write_to_ini(data, ini_file):
    with open(ini_file, 'w', encoding='utf-8') as file:
        for section, options in data.items():
            file.write(f'[{section}]\n')
            for key, value in options.items():
                file.write(f'{key}={value}\n')

if __name__ == "__main__":
    log_file = r'D:\test_project\stress_testing\V11.0\DataAnalysis\pushtest_2024_12_10.log'
    ini_file = r'D:\test_project\stress_testing\V11.0\DataAnalysis\data.ini'
    
    start_time_input = input("请输入开始时间 (格式: YYYY-MM-DD HH:MM:SS): ")
    end_time_input = input("请输入结束时间 (格式: YYYY-MM-DD HH:MM:SS): ")
    
    start_time = datetime.strptime(start_time_input, '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(end_time_input, '%Y-%m-%d %H:%M:%S')
    
    parsed_data = parse_log(log_file, start_time, end_time)
    write_to_ini(parsed_data, ini_file)