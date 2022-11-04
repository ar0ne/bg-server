// Room Setup component
import { Component } from "react";

import AuthService from "../../services/auth.service";
import RoomService from "../../services/room.service";
import { withRouter } from "../../common/with-router";


function RoomInfo (props) {
    const { room } = props;
    return (
        <div>
            <h3>Setup Game</h3>
            <p>Game image: TBD</p>
            <p>Name: {room.game.name}</p>
            <p>State: {room.room_state}</p>
            <p>Room size is {room.size}</p>
        </div>
    );
}

function RoomSize (props) {
    const { min, max, size } = props;
    return (
        <div>
            <button
                disabled={size === max}
                onClick={props.increaseRoomSize}
            >+</button>
            <button
                disabled={size === min}
                onClick={props.decreaseRoomSize}
            >-</button>
        </div>
    )
}


function ParticipantList (props) {
    const { room } = props;
    const participants = room.participants;
    if (!(participants && participants.length)) {
        return (<div>No participants</div>);
    }
    const participantItems = participants.map((participant) => (
        <div key={participant.id}>
            <p>Name: {participant.name}</p>
            <p>Avatar: TBD</p>
            <p>ID : {participant.id}</p>
            <p>Nickname: {participant.nickname}</p>
            { participant.id === room.admin.id && (
                <pre>(table administrator)</pre>
            )}
        </div>
    ));

    return (
        <div>
            <h3>Players at this room</h3>
            {participantItems}
        </div>
    );
}

class RoomSetup extends Component {
    constructor(props) {
        super(props);

        this.state = {
            isLoading: false,
            isLoggedIn: false,
            isAdmin: false,
            isParticipant: false,
            isCanJoin: false,
            isCanStart: false,
            isSetupRoom: false,
            user_id: "",
            room: {
                admin: [],
                date_created: "",
                game: {
                    id: "",
                    max_size: 1,
                    min_size: 1,
                    name: "",
                },
                id: "",
                room_state: "",
                participants: [],
                size: 1,
            },
        }

        this.updateRoom = this.updateRoom.bind(this);
        this.startGame = this.startGame.bind(this);
        this.quitGame = this.quitGame.bind(this);
        this.joinGame = this.joinGame.bind(this);
        this.increaseRoomSize = this.increaseRoomSize.bind(this);
        this.decreaseRoomSize = this.decreaseRoomSize.bind(this);
    }

    updateRoom(data) {
        console.log('Room update');
        this.setState({
            isLoading: true
        });

        const body = {
            size: data.size || this.state.room.size,
            room_state: data.room_state || this.state.room.room_state,
        }
        RoomService.updateRoom(this.state.room.id, body).then(response => {
            console.log("room updated");
            this.setState({
                isLoading: false,
                room: response.data,
            });
        },
        error => {
            console.log("unable to update game room setup");
            console.log(
                (error.response &&
                error.response.data &&
                error.response.data.error &&
                error.response.data.error.message) ||
                error.message ||
                error.toString()
            );
        });
    }

    startGame() {
        console.log("start the game");
    }

    quitGame() {
        console.log("quit the game");
        this.setState({
            isLoading: true,
        })
        RoomService.removeParticipant(this.state.room.id, this.state.user_id)
            .then(response => {
                this.setState({
                    room: response.data,
                    isLoading: false,
                });
            },
            error => {
                console.log("unable to remove participant");
                console.log(
                    (error.response &&
                     error.response.data &&
                     error.response.data.error &&
                     error.response.data.error.message) ||
                    error.message ||
                    error.toString()
                );
            });
    }

    joinGame() {
        console.log("joined the game");
        this.setState({
            isLoading: true,
        })
        RoomService.addParticipant(this.state.room.id, this.state.user_id)
            .then(response => {
                this.setState({
                    room: response.data,
                    isLoading: false,
                });
            },
            error => {
                console.log("unable to add participant");
                console.log(
                    (error.response &&
                     error.response.data &&
                     error.response.data.error &&
                     error.response.data.error.message) ||
                    error.message ||
                    error.toString()
                );
            });
    }

    increaseRoomSize() {
        console.log("+")
        let data = {size: this.state.room.size + 1};
        this.updateRoom(data);
    }
    decreaseRoomSize() {
        console.log("-")
        let data = {size: this.state.room.size - 1};
        this.updateRoom(data);
    }

    componentDidMount() {
        const user = AuthService.getCurrentUser();
        if (user) {
            this.setState({
                user_id: user.user_id,
                isLoggedIn: true,
            });
        }
        const { room_id } = this.props.router.params;
        RoomService.getRoom(room_id).then(response => {
            const data = response.data;
            let isAdmin = (user && user.user_id === data.admin.id);
            let isParticipant = !!(user && data.participants.find((p) => p.id === user.user_id));
            let isSetupRoom = data.room_state === "CREATED";
            let isCanJoin = (user && isSetupRoom && data.participants.length < data.size);
            let isCanStart = (isAdmin && isSetupRoom && data.participants.length === data.size)
            this.setState({
                room: response.data,
                isAdmin,
                isParticipant,
                isCanJoin,
                isCanStart,
                isSetupRoom,
            });
        })
    }

    render() {
        const {
            isAdmin, isLoggedIn, isParticipant, isCanJoin, isCanStart, isSetupRoom, room,
         } = this.state;
        return (
            <div>
                <RoomInfo room={room} />
                { isCanStart && (
                    <div>
                        <button
                            className={this.isAdmin ? "" : "hidden"}
                            onClick={this.startGame}
                        >Start Game</button>

                    </div>
                )}

                { isLoggedIn && !isParticipant && isCanJoin && (
                    <div>
                        <button
                            onClick={this.joinGame}
                        >Join Game</button>
                    </div>
                )}


                { isSetupRoom && isAdmin && (
                    <RoomSize
                        size={this.state.room.size}
                        min={this.state.room.game.min_size}
                        max={this.state.room.game.max_size}
                        increaseRoomSize={this.increaseRoomSize}
                        decreaseRoomSize={this.decreaseRoomSize}
                    />
                )}

                <ParticipantList room={ room } isAdmin={ isAdmin } />

            </div>
        )
    }
}

export default withRouter(RoomSetup);