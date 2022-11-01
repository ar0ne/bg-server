// Lobby Page component
import { Component } from "react";
import RoomService from "../services/room.service";


function PublicRooms(props) {
    const rooms = props.rooms;
    if (!(rooms && rooms.length)) {
        return <p>No Available rooms</p>
    }
    const roomItems = rooms.map((room) => <li key={room.id}>{room.id}</li>);
    return (
        <ul>{roomItems}</ul>
    );
}

export default class LobbyPage extends Component {
    constructor(props) {
        super(props);

        this.state = {
            rooms: []
        }
    }

    render() {
        const { rooms } = this.state;
        return (
            <div>
                <h3>Join Game</h3>
                <PublicRooms rooms={rooms} />
            </div>
        )
    }

    componentDidMount() {
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