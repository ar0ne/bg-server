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
        </div>
    );
}

function RoomSize (props) {
    return (
        <div>
            <p>Room size is {props.size}</p>
            <button
                onClick={props.increaseRoomSize}
            >+</button>
            <button
                onClick={props.decreaseRoomSize}
            >-</button>
        </div>
    )
}


function ParticipantList (props) {
    const { isAdmin, room } = props;
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
            {isAdmin && (
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

    updateRoom() {
        console.log('Room update');
        this.setState({
            isLoading: true
        });

        RoomService.updateRoom(this.props.room_id).then(() => {
            console.log("room updated");
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
        this.setState({
            ...this.state.room, size: this.state.room.size + 1
        })
    }

    decreaseRoomSize() {
        console.log("-")
        this.setState({
            ...this.state.room, size: this.state.room.size - 1
        })
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
            let isCanJoin = (user && data.room_state === "created" && data.participants.length < data.size);
            this.setState({
                room: response.data,
                isAdmin:  isAdmin,
                isParticipant: isParticipant,
                isCanJoin: isCanJoin,
            });
        })
    }

    render() {
        const { isAdmin, isLoggedIn, isParticipant, isCanJoin, room } = this.state;
        return (
            <div>
                <RoomInfo room={room} />
                { isLoggedIn && isParticipant && (
                    <div>
                        <button
                            className={this.isAdmin ? "" : "hidden"}
                            onClick={this.startGame}
                        >Start Game</button>
                        <button
                            onClick={this.quitGame}
                        >Quit Game</button>
                    </div>
                )}

                { isLoggedIn && !isParticipant && isCanJoin && (
                    <div>
                        <button
                            onClick={this.joinGame}
                        >Join Game</button>
                    </div>
                )}


                { isAdmin && (
                    <RoomSize
                        size={room.size}
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