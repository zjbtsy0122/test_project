import subprocess
import os

exe_path = r'D:\testclient\testclient.exe'
a= subprocess.run(exe_path,capture_output=False,text=False)
print(a)



# bat_file_path = r"D:\testclient\start.bat"
# with open(bat_file_path,'w') as bat_file:
#     bat_file.write(f'@echo off\nstart "" "{exe_path}"\n')
#
# os.startfile(bat_file_path)