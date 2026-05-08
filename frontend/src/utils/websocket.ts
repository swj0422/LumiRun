class WebSocketService {
  private ws: WebSocket | null = null;
  private url: string = '';
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;
  private reconnectDelay: number = 1000;
  private messageHandlers: Map<string, ((data: any) => void)[]> = new Map();
  private isConnected: boolean = false;
  private currentToken: string = '';
  private currentClassId: number = 0;

  connect(token: string, classId: number): Promise<boolean> {
    return new Promise((resolve) => {
      this.currentToken = token;
      this.currentClassId = classId;

      if (!token) {
        console.error('WebSocket连接失败: 缺少token');
        resolve(false);
        return;
      }

      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      this.url = `${protocol}//${host}/api/v1/ws?token=${encodeURIComponent(token)}&class_id=${classId}`;

      console.log(`[WebSocket] 尝试连接: ${this.url}`);

      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('[WebSocket] 连接成功');
          this.isConnected = true;
          this.reconnectAttempts = 0;
          resolve(true);
        };

        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            console.log('[WebSocket] 收到消息:', message);
            this.handleMessage(message);
          } catch (error) {
            console.error('[WebSocket] 解析消息失败:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log(`[WebSocket] 连接关闭 - 代码: ${event.code}, 原因: ${event.reason}`);
          this.isConnected = false;
          if (this.currentToken) {
            this.attemptReconnect();
          }
        };

        this.ws.onerror = (error) => {
          console.error('[WebSocket] 连接错误:', error);
          console.error('[WebSocket] URL:', this.url);
          this.isConnected = false;
          resolve(false);
        };
      } catch (error) {
        console.error('[WebSocket] 创建连接失败:', error);
        resolve(false);
      }
    });
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`[WebSocket] 尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

      setTimeout(() => {
        this.connect(this.currentToken, this.currentClassId);
      }, this.reconnectDelay * this.reconnectAttempts);
    } else {
      console.error('[WebSocket] 重连失败，已达到最大尝试次数');
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
