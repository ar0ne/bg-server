// Base room table component
import { Component, lazy, Suspense } from "react";

import RoomService from "../../services/room.service";
import { withRouter } from "../../common/with-router";


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
                RoomService.getRoomData(room_id).then(response => {
                    // {"data": {...}}
                    const data = response.data.data;
                    this.setState({isLoading: false, data: data});
                });
            }
        });
    }



    render() {
        const { room, data, isLoading } = this.state;

        if (!room || !room.status) {
            return (
                <div></div>
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
                    {isLoading ? "" : <Game room_id={room.id} data={data} />}
                </Suspense>
            </div>
        )
    }

}

export default withRouter(RoomTable);