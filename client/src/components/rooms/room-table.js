// Base room table component
import { Component, lazy, Suspense } from "react";

import RoomService from "../../services/room.service";
import { withRouter } from "../../common/with-router";
import { useWs } from "../ws";


function wsComponent(WrappedComponent) {

    return function(props) {
        const { room_id } = props.router.params;
        const [ready, val, timeStamp, send] = useWs(`${process.env.REACT_APP_WS_SERVER_ROOT}/rooms/${room_id}/ws`);
        return (
            <WrappedComponent {...props} wsVal={val} wsTimeStamp={timeStamp} wsSend={send} wsReady={ready} />
        );
    };
}


class RoomTable extends Component {
    constructor(props) {
        super(props);

        this.state = {
            isLoading: true,
            room: {
                admin: {
                    id: "",
                },
                game: {
                    name: "",
                },
                id: "",
                participants: [],
                status: 0,
            },
            data: {}
        }
        this.fetchRoomData.bind(this);
        this.notifyAllAboutUpdate.bind(this);
    }

    componentDidMount() {
        this.setState({isLoading: true});
        const { room_id } = this.props.router.params;
        RoomService.getRoom(room_id).then(response => {
            const room  = response.data.data;
            this.setState({room: room, isLoading: false});
            if (RoomService.isCreated(room)) {
                // redirect to Setup page
                return setTimeout(
                    () => this.props.router.navigate(`/rooms/${room_id}/setup`, { replace: true }),
                    1
                );
            } else if (RoomService.isStarted(room)) {
                this.fetchRoomData();
            }
        });
    }

    fetchRoomData() {
        // FIXME: maybe take it from websocket channel ?
        const { room_id } = this.props.router.params;
        RoomService.getRoomData(room_id).then(response => {
            // {"data": {...}}
            const data = response.data.data;
            this.setState({data: data});
        });
    }

    notifyAllAboutUpdate() {
        // send a message via ws to make page refresh
        this.props.wsSend("refresh");
    }

    componentDidUpdate(prevProps) {
        const { wsVal, wsTimeStamp } = this.props;
        if (wsVal === "refresh" && prevProps.wsTimeStamp !== wsTimeStamp) {
            this.fetchRoomData();
        }
    }

    render() {
        const { room, data, isLoading } = this.state;

        if (!room || !room.status) {
            return (
                <div>Nothing is here.</div>
            )
        }
        if (RoomService.isCanceled(room)) {
            return (
                <div>Game has been canceled</div>
            )
        }

        const Game = lazy(() => import(`../../playgrounds/${room.game.name.toLowerCase()}.js`));

        return (
            <div>
                <div>Game Table: {room.game.name}</div>
                <Suspense fallback={<div>Loading...</div>}>
                    {isLoading ? "" : <Game 
                        room_id={room.id} 
                        data={data} 
                        // fetchRoomData={() => this.fetchRoomData()} 
                        notifyAllAboutUpdate={() => this.notifyAllAboutUpdate()} />}
                </Suspense>
            </div>
        )
    }

}

export default withRouter(wsComponent(RoomTable));