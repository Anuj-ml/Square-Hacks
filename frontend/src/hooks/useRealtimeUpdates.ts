import { useState, useEffect } from 'react';
import { getWebSocketManager } from '../lib/websocket';

export function useRealtimeUpdates() {
  const [isConnected, setIsConnected] = useState(false);
  const [latestUpdate, setLatestUpdate] = useState<any>(null);
  const [wsManager] = useState(() => getWebSocketManager());
  
  useEffect(() => {
    // Track WebSocket connection status
    const unsubscribeOpen = wsManager.onOpen(() => {
      setIsConnected(true);
      console.log('[useRealtimeUpdates] WebSocket connected');
    });

    const unsubscribeClose = wsManager.onClose(() => {
      setIsConnected(false);
      console.log('[useRealtimeUpdates] WebSocket disconnected');
    });

    const unsubscribeMessage = wsManager.onMessage((data: any) => {
      setLatestUpdate(data);
    });
    
    wsManager.connect();
    
    return () => {
      unsubscribeOpen();
      unsubscribeClose();
      unsubscribeMessage();
      wsManager.disconnect();
    };
  }, [wsManager]);
  
  const sendMessage = (message: any) => {
    wsManager.send(message);
  };
  
  return { isConnected, latestUpdate, sendMessage };
}
