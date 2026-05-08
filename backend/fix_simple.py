import os

# 读取文件
with open('app/api/v1/admin_order.py', 'rb') as f:
    content = f.read()

# 字节级替换 - 修复第106行的乱码
# 现在的问题是: description="订单状态),
# 需要替换为: description="订单状态"),
old_bytes = b'description="\xe8\xae\xa2\xe5\x8d\x95\xe7\x8a\xb6\xe6\x80\x81),\r'
new_bytes = b'description="\xe8\xae\xa2\xe5\x8d\x95\xe7\x8a\xb6\xe6\x80\x81"),\r'
content = content.replace(old_bytes, new_bytes)

# 写入修复后的内容
with open('app/api/v1/admin_order.py', 'wb') as f:
    f.write(content)

print('Fixed admin_order.py')
