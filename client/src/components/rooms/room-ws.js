import { useWs } from "../ws";


export default function wsRoom(WrappedComponent) {

    return function(props) {
        const { room_id } = props.router.params;
        const [ready, val, timeStamp, send] = useWs(`${process.env.REACT_APP_WS_SERVER_ROOT}/rooms/${room_id}/ws`);
        return (
            <WrappedComponent {...props} wsVal={val} wsTimeStamp={timeStamp} wsSend={send} wsReady={ready} />
        );
    };
}
