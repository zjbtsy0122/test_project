import re
from datetime import datetime

log_file_path = r'D:\test_project\stress_testing\V11.0\DataAnalysis\pushtest_2024_12_10.log'
output_file_path = r'D:\test_project\stress_testing\V11.0\DataAnalysis\data.ini'

start_time = datetime.strptime("2024-12-10 13:30:51", "%Y-%m-%d %H:%M:%S")
end_time = datetime.strptime("2024-12-10 14:17:56", "%Y-%m-%d %H:%M:%S")

section = {}
options = {}

with open(log_file_path, 'r', encoding='utf-8') as log_file:
    lines = log_file.readlines()
    search_started = False

    for line in lines:
        timestamp_match = re.match(r'\[ERROR\](\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
        if timestamp_match:
            log_time = datetime.strptime(timestamp_match.group(1), "%Y-%m-%d %H:%M:%S")
            if start_time <= log_time <= end_time:
                if "Search计划开始了" in line:
                    search_started = True
                elif "Search计划结束了！" in line and search_started:
                    search_started = False

                if search_started:
                    if "第1次增压" in line:
                        section_name = f"Search{log_time.strftime('%Y-%m-%d %H:%M:%S')}"
                        section[section_name] = log_time.strftime('%Y-%m-%d %H:%M:%S')
                        req_num_match = re.search(r'req_num的当前值为: (\d+)', line)
                        if req_num_match:
                            options['st'] = req_num_match.group(1)

                    elif "第2次增压" in line:
                        req_num_match = re.search(r'req_num的当前值为: (\d+)', line)
                        if req_num_match:
                            options['ed'] = log_time.strftime('%Y-%m-%d %H:%M:%S')
                            options['td'] = req_num_match.group(1)

with open(output_file_path, 'w', encoding='utf-8') as ini_file:
    ini_file.write("[Section]\n")
    for key, value in section.items():
        ini_file.write(f"{key}={value}\n")
    for key, value in options.items():
        ini_file.write(f"{key}={value}\n")