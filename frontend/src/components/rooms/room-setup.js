// Room Setup component
import { Component } from "react";

import AuthService from "../../services/auth.service";
import RoomService from "../../services/room.service";
import { withRouter } from "../../common/with-router";
import wsRoom from "./room-ws";


function RoomInfo (props) {
    const { room } = props;
    return (
        <div>
            <h3>Setup Game</h3>
            <p>Game image: TBD</p>
            <p>Name: {room.game.name}</p>
            <p>Status: {RoomService.getRoomStatus(room.status)}</p>
            <p>Room size is {room.size}</p>
            <p>Min/Max: ({room.game.min_size}/{room.game.max_size})</p>
        </div>
    );
}

function RoomSize (props) {
    const { min, max, size } = props;
    return (
        <div>
            <button
                disabled={size >= max}
                onClick={props.increaseRoomSize}
            >+</button>
            <button
                disabled={size <= min}
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
            isStarted: false,
            user_id: "",
            room: {
                admin: {
                    id: "",
                },
                created: null,
                game: {
                    id: "",
                    max_size: 1,
                    min_size: 1,
                    name: "",
                },
                id: "",
                status: 0,
                participants: [],
                size: 1,
            },
        }

        this.changeRoomSize = this.changeRoomSize.bind(this);
        this.startGame = this.startGame.bind(this);
        this.redirectToRoomTable = this.redirectToRoomTable.bind(this);
        this.quitGame = this.quitGame.bind(this);
        this.joinGame = this.joinGame.bind(this);
        this.increaseRoomSize = this.increaseRoomSize.bind(this);
        this.decreaseRoomSize = this.decreaseRoomSize.bind(this);
    }

    changeRoomSize(newSize) {
        this.setState({ isLoading: true });

        RoomService.changeRoomSize(this.state.room.id, newSize).then(room => {
            console.log("room updated");
            this.setRoom(room);
            this.setState({isLoading: false});
            this.notifyAllAboutUpdate();
        });
    }

    startGame() {
        console.log("start the game");
        this.setState({ isLoading: true });
        RoomService.startRoom(this.state.room.id)
            .then(room => {
                this.setRoom(room);
                this.setState({isLoading: false});
                this.notifyAllAboutUpdate();
                this.redirectToRoomTable();
            });
    }

    quitGame() {
        console.log("quit the game");
        this.setState({isLoading: true});
        RoomService.removeParticipant(this.state.room.id, this.state.user_id)
            .then(response => {
                // empty body
                this.setState({isLoading: false});
                this.notifyAllAboutUpdate();
            });
    }

    joinGame() {
        console.log("joined the game");
        this.setState({ isLoading: true })
        RoomService.addParticipant(this.state.room.id, this.state.user_id)
            .then(room => {
                this.setRoom(room);
                this.setState({isLoading: false});
                this.notifyAllAboutUpdate();
            });
    }
    redirectToRoomTable() {
        setTimeout(() => this.props.router.navigate(`/rooms/${this.state.room.id}`, { replace: true }), 1);
    }

    increaseRoomSize() {
        console.log("+")
        this.changeRoomSize(this.state.room.size + 1);
    }
    decreaseRoomSize() {
        console.log("-")
        this.changeRoomSize(this.state.room.size - 1);
    }
    setRoom(room) {
        let isStarted = RoomService.isStarted(room);
        let isAdmin = (this.state.user_id && this.state.user_id === room.admin.id);
        let isParticipant = !!(this.state.user_id && room.participants.find((p) => p.id === this.state.user_id));
        let isSetupRoom = RoomService.isCreated(room);
        let isCanJoin = (this.state.user_id && isSetupRoom && room.participants.length < room.size);
        let isCanStart = (isAdmin && isSetupRoom && room.participants.length === room.size)
        this.setState({
            room: room,
            isAdmin,
            isParticipant,
            isCanJoin,
            isCanStart,
            isSetupRoom,
            isStarted,
        });
    }

    fetchRoom() {
        const { room_id } = this.props.router.params;
        RoomService.getRoom(room_id).then(room => this.setRoom(room));
    }

    notifyAllAboutUpdate() {
        // send a message via ws to make page refresh
        this.props.wsSend("refresh");
    }

    componentDidUpdate(prevProps) {
        const { wsVal, wsTimeStamp } = this.props;
        if (wsVal === "refresh" && prevProps.wsTimeStamp !== wsTimeStamp) {
            this.fetchRoom();
            if (RoomService.isStarted(this.state.room)) {
                this.redirectToRoomTable();
            }
        }
    }

    componentDidMount() {
        const user = AuthService.getCurrentUser();
        if (user) {
            this.setState({
                user_id: user.user_id,
                isLoggedIn: true,
            });
        }
        this.fetchRoom();
        if (RoomService.isStarted(this.state.room)) {
            this.redirectToRoomTable();
        }
    }

    render() {
        const {
            isAdmin, isLoggedIn, isParticipant, isCanJoin, isCanStart, isSetupRoom, isStarted, room,
         } = this.state;
        return (
            <div>
                <RoomInfo room={room} />
                { isStarted && (
                    <div>
                        <button
                            onClick={this.redirectToRoomTable}
                        >Go to game</button>
                    </div>
                )}
                { isCanStart && (
                    <div>
                        <button
                            className={isAdmin ? "" : "hidden"}
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
                { isLoggedIn && isParticipant && isSetupRoom && (
                    <div>
                        <button
                            onClick={this.quitGame}
                        >Quit Game</button>
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

export default withRouter(wsRoom(RoomSetup));