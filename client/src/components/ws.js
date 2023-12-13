import { useState, useRef, useEffect } from "react";

export const useWs = (url) => {
    const [isReady, setIsReady] = useState(false);
    const [val, setVal] = useState(null);
    const [timeStamp, setTimeStamp] = useState(null);
  
    const ws = useRef(null);
  
    useEffect(() => {
        const socket = new WebSocket(url);
    
        socket.onopen = () => setIsReady(true);
        socket.onclose = () => setIsReady(false);
        socket.onmessage = (event) => {
            console.log("received on message", event);
            setVal(event.data);
            setTimeStamp(event.timeStamp);
        }
    
        ws.current = socket;
  
        return () => {
            socket.close();
        }
    }, []);
  
    // bind is needed to make sure `send` references correct `this`
    return [isReady, val, timeStamp, ws.current?.send.bind(ws.current)]
}