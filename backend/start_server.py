import subprocess
import time
import sys
import socket

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def kill_port_8000():
    """强制停止占用8000端口的进程"""
    try:
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if ':8000' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    print(f'正在停止进程 {pid}...')
                    subprocess.run(['taskkill', '/F', '/PID', pid])
        time.sleep(2)
    except Exception as e:
        print(f'停止进程时出错: {e}')

# 先确保端口未被占用
if is_port_in_use(8000):
    print('端口8000已被占用，正在停止...')
    kill_port_8000()
else:
    print('端口8000未被占用')

# 启动后端服务
print('正在启动后端服务...')
subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000'],
    cwd=r'd:\LumiRun\LumiRun\backend',
    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
)
print('后端服务启动命令已执行，请在新的终端窗口中查看服务状态')