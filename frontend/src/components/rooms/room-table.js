// Base room table component
import { Component, lazy, Suspense } from "react";

import RoomService from "../../services/room.service";
import { withRouter } from "../../common/with-router";
import wsRoom from "./room-ws";


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
        this.fetchRoomData = this.fetchRoomData.bind(this);
        this.notifyAllAboutUpdate = this.notifyAllAboutUpdate.bind(this);
    }

    componentDidMount() {
        this.setState({isLoading: true});
        const { room_id } = this.props.router.params;
        RoomService.getRoom(room_id).then(room => {
            this.setState({room: room, isLoading: false});
            if (RoomService.isCreated(room)) {
                // redirect to Setup page
                return setTimeout(
                    () => this.props.router.navigate(`/rooms/${room_id}/setup`, { replace: true }),
                    1
                );
            } else if (!RoomService.isCanceled(room) || !RoomService.isAbandoned(room)) {
                this.fetchRoomData();
            }
        });
    }

    fetchRoomData() {
        const { room_id } = this.props.router.params;
        RoomService.getRoomData(room_id).then(roomData => {
            this.setState({data: roomData});
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
                <div>Loading.</div>
            )
        }
        if (RoomService.isCanceled(room) || RoomService.isAbandoned(room)) {
            return (
                <div>Game has been canceled.</div>
            )
        }

        const Game = lazy(() => import(`../../playgrounds/${room.game.name.toLowerCase()}.js`));

        return (
            <div>
                <div>{room.game.name}</div>
                <Suspense fallback={<div>Loading...</div>}>
                    {!isLoading ? <Game 
                        room_id={room.id} 
                        data={data} 
                        notifyAllAboutUpdate={this.notifyAllAboutUpdate} 
                        /> : ""
                    }
                </Suspense>
            </div>
        )
    }

}


export default withRouter(wsRoom(RoomTable));