/**
 * WebSocket client for real-time game updates
 */
import { io, Socket } from 'socket.io-client';

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'http://localhost:5000';

class SocketClient {
  private socket: Socket | null = null;

  connect(token?: string): Socket {
    if (this.socket?.connected) {
      return this.socket;
    }

    this.socket = io(SOCKET_URL, {
      auth: token ? { token } : undefined,
      transports: ['websocket', 'polling'],
    });

    this.socket.on('connect', () => {
      console.log('Socket connected:', this.socket?.id);
    });

    this.socket.on('disconnect', (reason) => {
      console.log('Socket disconnected:', reason);
    });

    this.socket.on('connect_error', (error) => {
      console.error('Socket connection error:', error.message);
    });

    return this.socket;
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  // Game room operations
  joinGame(gameId: string): void {
    this.socket?.emit('join_game', { game_id: gameId });
  }

  leaveGame(gameId: string): void {
    this.socket?.emit('leave_game', { game_id: gameId });
  }

  // Event listeners
  onGameUpdate(callback: (data: unknown) => void): void {
    this.socket?.on('game_update', callback);
  }

  onTurnEnd(callback: (data: unknown) => void): void {
    this.socket?.on('turn_end', callback);
  }

  onChatMessage(callback: (data: unknown) => void): void {
    this.socket?.on('chat_message', callback);
  }

  // Send chat message
  sendChatMessage(gameId: string, message: string): void {
    this.socket?.emit('chat_message', { game_id: gameId, message });
  }

  // Remove listeners
  off(event: string): void {
    this.socket?.off(event);
  }

  get isConnected(): boolean {
    return this.socket?.connected ?? false;
  }
}

export const socketClient = new SocketClient();
export default socketClient;
