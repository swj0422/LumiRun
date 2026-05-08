import os

def fix_file(file_path):
    # 读取文件
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # 修复所有乱码模式
    # 订单状态
    content = content.replace(
        b'description="\xe8\xae\xa2\xe5\x8d\x95\xe7\x8a\xb6\xe6\x80\x81),\r',
        b'description="\xe8\xae\xa2\xe5\x8d\x95\xe7\x8a\xb6\xe6\x80\x81"),\r'
    )
    # 开始时间
    content = content.replace(
        b'description="\xe5\xbc\x80\xe5\xa7\x8b\xe6\x97\xb6\xef\xbf\xbd?),\r',
        b'description="\xe5\xbc\x80\xe5\xa7\x8b\xe6\x97\xb6\xe9\x97\xb4"),\r'
    )
    # 结束时间
    content = content.replace(
        b'description="\xe7\xbb\x93\xe6\x9d\x9f\xe6\x97\xb6\xef\xbf\xbd?\r',
        b'description="\xe7\xbb\x93\xe6\x9d\x9f\xe6\x97\xb6\xe9\x97\xb4")\r'
    )
    # 班级ID
    content = content.replace(
        b'description="\xe7\x8f\xad\xe7\xba\xa7ID?\r',
        b'description="\xe7\x8f\xad\xe7\xba\xa7ID")\r'
    )
    
    # 写入修复后的内容
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
