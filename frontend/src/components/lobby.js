// Lobby Page component
import { Component } from "react";
import { Link } from "react-router-dom";
import AuthService from "../services/auth.service";
import RoomService from "../services/room.service";


function PublicRooms(props) {
    const { rooms } = props;
    if (!(rooms && rooms.length)) {
        return <p>No Available rooms</p>
    }
    const roomItems = rooms.map((room) => {
        const participants = room.participants.length;
        const roomSize = room.size;
        const info = `${room.game.name} [${RoomService.getRoomStatus(room.status)}] (${participants}/${roomSize})`;
        const url = `/rooms/${room.id}`;
        return (
            <li key={room.id}>
                <Link to={ url }>{ info }</Link>
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
            isLoading: false,
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
        this.setState({isLoading: true});
        const user = AuthService.getCurrentUser();
        if (user) {
            this.setState({isLoggedIn: true});
        }
        RoomService.getAllPublicRooms().then(
            rooms => this.setState({rooms: rooms, isLoading: false})
        );
    }
}