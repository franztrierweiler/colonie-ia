/**
 * WebSocket client for real-time game communication
 */
import { io, Socket } from 'socket.io-client';

const SOCKET_URL = import.meta.env.VITE_API_URL?.replace('/api', '') || 'http://localhost:5000';

class SocketService {
  private socket: Socket | null = null;
  private listeners: Map<string, Set<(data: unknown) => void>> = new Map();

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      const token = localStorage.getItem('access_token');

      if (!token) {
        reject(new Error('No access token'));
        return;
      }

      if (this.socket?.connected) {
        resolve();
        return;
      }

      this.socket = io(SOCKET_URL, {
        auth: { token },
        transports: ['websocket', 'polling'],
      });

      this.socket.on('connect', () => {
        console.log('[Socket] Connected');
        resolve();
      });

      this.socket.on('connect_error', (error) => {
        console.error('[Socket] Connection error:', error);
        reject(error);
      });

      this.socket.on('disconnect', (reason) => {
        console.log('[Socket] Disconnected:', reason);
      });

      this.socket.on('error', (data: { message: string }) => {
        console.error('[Socket] Error:', data.message);
      });

      // Re-emit events to registered listeners
      this.socket.onAny((event, data) => {
        const callbacks = this.listeners.get(event);
        if (callbacks) {
          callbacks.forEach(cb => cb(data));
        }
      });
    });
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  isConnected(): boolean {
    return this.socket?.connected ?? false;
  }

  // Game room methods
  joinGame(gameId: number): void {
    this.socket?.emit('join_game', { game_id: gameId });
  }

  leaveGame(gameId: number): void {
    this.socket?.emit('leave_game', { game_id: gameId });
  }

  sendChatMessage(gameId: number, message: string): void {
    this.socket?.emit('chat_message', { game_id: gameId, message });
  }

  // Event listeners
  on<T = unknown>(event: string, callback: (data: T) => void): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback as (data: unknown) => void);

    // Return unsubscribe function
    return () => {
      this.listeners.get(event)?.delete(callback as (data: unknown) => void);
    };
  }

  off(event: string, callback?: (data: unknown) => void): void {
    if (callback) {
      this.listeners.get(event)?.delete(callback);
    } else {
      this.listeners.delete(event);
    }
  }

  // Convenience methods for common events
  onConnected(callback: (data: { message: string }) => void): () => void {
    return this.on('connected', callback);
  }

  onGameJoined(callback: (data: { game_id: number; message: string }) => void): () => void {
    return this.on('game_joined', callback);
  }

  onGameLeft(callback: (data: { game_id: number; message: string }) => void): () => void {
    return this.on('game_left', callback);
  }

  onPlayerJoined(callback: (data: { user_id: number; pseudo: string }) => void): () => void {
    return this.on('player_joined', callback);
  }

  onPlayerLeft(callback: (data: { user_id: number; pseudo: string }) => void): () => void {
    return this.on('player_left', callback);
  }

  onChatMessage(callback: (data: { user_id: number; pseudo: string; message: string }) => void): () => void {
    return this.on('chat_message', callback);
  }

  onGameUpdate(callback: (data: unknown) => void): () => void {
    return this.on('game_update', callback);
  }

  onTurnEnd(callback: (data: unknown) => void): () => void {
    return this.on('turn_end', callback);
  }
}

export const socketService = new SocketService();
export default socketService;
