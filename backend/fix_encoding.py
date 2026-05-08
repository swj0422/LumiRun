import os

def fix_file(file_path):
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # 替换乱码字节序列（不考虑行首空格）
    # 文档字符串乱码
    content = content.replace(
        b'"""\\xc3\\xa8\\xc2\\x8e\\xc2\\xb7\\xc3\\xa5\\xc2\\x8f\\xc2\\x96\\xc3\\xa7\\xc2\\x8f\\xc2\\xad\\xc3\\xa7\\xc2\\xba\\xc2\\xa7\\xc3\\xa8\\xc2\\xaf\\xc2\\xa6\\xc3\\xa6\\xc2\\x83\\xc2\\x85"""\r',
        '"""\u83b7\u53d6\u73ed\u7ea7\u8be6\u60c5"""\r'.encode('utf-8')
    )
    # detail乱码
    content = content.replace(
        b'\\xc3\\xa7\\xc2\\x8f\\xc2\\xad\\xc3\\xa7\\xc2\\xba\\xc2\\xa7\\xc3\\xa4\\xc2\\xb8\\xc2\\x8d\\xc3\\xa5\\xc2\\xad\\xc2\\x98\\xc3\\xa5\\xc2\\x9c?\r',
        '\u73ed\u7ea7\u4e0d\u5b58\u5728"\r'.encode('utf-8')
    )

    with open(file_path, 'wb') as f:
        f.write(content)
    
    print('Fixed:', file_path)

files = [
    'app/api/v1/admin_class.py',
    'app/api/v1/admin_gift.py',
    'app/api/v1/admin_order.py',
    'app/api/v1/admin_suggestion.py'
]

for file in files:
    if os.path.exists(file):
        fix_file(file)
    else:
        print('File not found:', file)
