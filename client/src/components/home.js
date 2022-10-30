// Home Page component
import { Component } from "react";
import RoomService from "../services/room.service";


function PublicRooms(props) {
    const rooms = props.rooms;
    const roomItems = rooms.map((room) => <li>{room.id}</li>);
    return (
        <ul>{roomItems}</ul>
    );
}

export default class HomePage extends Component {
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
                <h1>Hello world</h1>
                <h3>Rooms</h3>
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