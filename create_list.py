import re

# 打开文件
with open('mzml_list.txt', 'r') as file:
    # 读取文件内容
    content = file.read()
    # 进行正则匹配
    matches = re.findall(r'MTBLS.+?/', content)
    a = list(set(matches))
    print(len(a))
    # 打印匹配结果
with open('download_list.txt', 'a') as file:
    for directory in a:
        file.write(directory[:-1] + '\n')
