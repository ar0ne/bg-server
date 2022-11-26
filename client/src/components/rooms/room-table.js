// Base room table component
import { Component } from "react";

import AuthService from "../../services/auth.service";
import RoomService from "../../services/room.service";
import { withRouter } from "../../common/with-router";


import Regicide from "./regicide";

class RoomTable extends Component {
    constructor(props) {
        super(props);

        this.state = {
            isLoading: false,
            room: {
                admin: {
                    id: "",
                },
                game: {
                    name: "",
                },
                id: "",
                participants: [],
                room_state: "",
            },
            data: {
                enemy_deck_size: 0,
                discard_size: 0,
                enemy: [],
                first_player_id: "",
                state: "",
                player_id: "",
                played_combos: [],
                tavern_size: 0,
                turn: 0,
                hand: undefined,
            },
        }
    }

    componentDidMount() {
        this.setState({isLoading: true});
        const { room_id } = this.props.router.params;
        RoomService.getRoom(room_id).then(response => {
            const room  = response.data;
            this.setState({room: room});
            if (room.room_state === "CREATED") {
                // redirect to Setup page
                return setTimeout(() => this.props.router.navigate(`/rooms/${room_id}/setup`, { replace: true }), 1);
            } else if (room.room_state === "STARTED") {
                RoomService.getRoomData(room_id).then(response => {
                    const data = response.data;
                    this.setState({isLoading: false, data: data});
                });
            }
        });

    }

    render() {
        const { room, data } = this.state;

        if (!room.room_state) {
            return (
                <div></div>
            )
        }
        if (room.room_state === "CANCELED") {
            return (
                <div>Game has been canceled</div>
            )
        }

        return (
            <div>
                <div>Game Table: {room.game.name}</div>
                <Regicide data={data} room={room} />
            </div>
        )
    }

}

export default withRouter(RoomTable);