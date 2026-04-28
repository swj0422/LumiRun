class WebSocketService {
  private ws: WebSocket | null = null;
  private url: string = '';
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;
  private reconnectDelay: number = 1000;
  private messageHandlers: Map<string, ((data: any) => void)[]> = new Map();
  private isConnected: boolean = false;

  connect(token: string, classId: number): Promise<boolean> {
    return new Promise((resolve) => {
      // 构建WebSocket URL
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      this.url = `${protocol}//${host}/v1/ws?token=${token}&class_id=${classId}`;

      try {
        // 检查token是否存在
        if (!token) {
          console.error('WebSocket连接失败: 缺少token');
          resolve(false);
          return;
        }

        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('WebSocket连接成功');
          this.isConnected = true;
          this.reconnectAttempts = 0;
          resolve(true);
        };

        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('解析WebSocket消息失败:', error);
          }
        };

        this.ws.onclose = () => {
          console.log('WebSocket连接关闭');
          this.isConnected = false;
          // 只有在token存在时才尝试重连
          if (token) {
            this.attemptReconnect(token, classId);
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket错误:', error);
          this.isConnected = false;
          resolve(false);
        };
      } catch (error) {
        console.error('WebSocket连接失败:', error);
        resolve(false);
      }
    });
  }

  private attemptReconnect(token: string, classId: number) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(
        `尝试重连WebSocket (${this.reconnectAttempts}/${this.maxReconnectAttempts})`
      );

      setTimeout(() => {
        this.connect(token, classId);
      }, this.reconnectDelay * this.reconnectAttempts);
    } else {
      console.error('WebSocket重连失败，已达到最大尝试次数');
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.isConnected = false;
      this.messageHandlers.clear();
    }
  }

  send(message: any) {
    if (this.ws && this.isConnected) {
      this.ws.send(JSON.stringify(message));
      return true;
    }
    return false;
  }

  on(type: string, handler: (data: any) => void) {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, []);
    }
    this.messageHandlers.get(type)?.push(handler);
  }

  off(type: string, handler: (data: any) => void) {
    const handlers = this.messageHandlers.get(type);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  private handleMessage(message: any) {
    const type = message.type;
    if (this.messageHandlers.has(type)) {
      const handlers = this.messageHandlers.get(type);
      handlers?.forEach((handler) => {
        try {
          handler(message);
        } catch (error) {
          console.error(`处理WebSocket消息失败 [${type}]:`, error);
        }
      });
    }
  }

  isConnect(): boolean {
    return this.isConnected;
  }

  // 获取排行榜数据
  getLeaderboard() {
    this.send({ type: 'get_leaderboard' });
  }

  // 发送ping消息保持连接
  ping() {
    this.send({ type: 'ping' });
  }
}

// 导出单例
export const websocketService = new WebSocketService();
