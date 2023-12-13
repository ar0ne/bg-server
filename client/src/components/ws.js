import { useState, useRef, useEffect } from "react";

export const useWs = () => {
    const [isReady, setIsReady] = useState(false);
    const [val, setVal] = useState(null);
  
    const ws = useRef(null);
  
    useEffect(() => {
        const socket = new WebSocket("ws://localhost:8888/api/v1/ws");
    
        socket.onopen = () => setIsReady(true);
        socket.onclose = () => setIsReady(false);
        socket.onmessage = (event) => setVal(event.data);
    
        ws.current = socket;
  
        return () => {
            socket.close();
        }
    }, [])
  
    // bind is needed to make sure `send` references correct `this`
    return [isReady, val, ws.current?.send.bind(ws.current)]
}