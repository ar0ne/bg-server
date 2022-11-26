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
            const { room, data } = response.data;
            if (room.room_state === "CREATED") {
                // redirect to Setup page
                return setTimeout(() => this.props.router.navigate(`/rooms/${room_id}/setup`, { replace: true }), 1);
            } else if (room.room_state === "STARTED") {
                // get game turn ?
            }

            this.setState({
                isLoading: false,
                room: room,
                data: data,
            });
        });

    }

    render() {
        const { room, data } = this.state;

        if (!room.room_state) {
            return (
                <div></div>
            )
        }

        return (
            <div>
                <div>Table {room.game.name}</div>
                <Regicide data={data} room={room} />
            </div>
        )
    }

}

export default withRouter(RoomTable);