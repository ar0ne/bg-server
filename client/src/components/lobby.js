// Lobby Page component
import { Component } from "react";
import { Link } from "react-router-dom";
import RoomService from "../services/room.service";
import AuthService from "../services/auth.service";


function PublicRooms(props) {
    const { rooms, isLoggedIn} = props;
    if (!(rooms && rooms.length)) {
        return <p>No Available rooms</p>
    }
    const roomItems = rooms.map((room) => {
        const participants = room.participants.length;
        const roomSize = room.size;
        const info = `${room.game.name} [${room.room_state.toUpperCase()}] (${participants}/${roomSize})`;
        const url = `/rooms/${room.id}`;
        return (
            <li key={room.id}>
                <Link to={ url }>{ info }</Link>
                <button
                    disabled={ !isLoggedIn || participants === roomSize }
                >Join</button>
            </li>
        )
    });
    return (
        <ul>{roomItems}</ul>
    );
}

export default class LobbyPage extends Component {
    constructor(props) {
        super(props);
        this.state = {
            rooms: [],
            isLoggedIn: false,
        }
    }

    render() {
        const { rooms } = this.state;
        return (
            <div>
                <h3>Join Game</h3>
                <PublicRooms rooms={rooms} isLoggedIn={this.state.isLoggedIn} />
            </div>
        )
    }

    componentDidMount() {
        const user = AuthService.getCurrentUser();
        if (user) {
            this.setState({
                isLoggedIn: true
            });
        }
        RoomService.getAllPublicRooms().then(
            response => {
                this.setState({
                    rooms: response.data
                });
            },
            error => {
                console.log("unable to fetch public rooms");
                console.log(
                    (error.response && error.response.data) ||
                    error.message ||
                    error.toString()
                );
            }
        )
    }
}