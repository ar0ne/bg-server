// Room Setup component

import { Component } from "react";
import GameService from "../../services/game.service";
import AuthService from "../../services/auth.service";
import { withRouter } from "../../common/with-router";

class RoomSetup extends Component {
    constructor(props) {
        super(props);

        this.state = {
            isLoading: false,
            isLoggedIn: false,
            room: {
                size: 0,
            },
        }

        this.updateRoom = this.updateRoom.bind(this);
        this.startGame = this.startGame.bind(this);
        this.increaseRoomSize = this.increaseRoomSize.bind(this);
        this.decreaseRoomSize = this.decreaseRoomSize.bind(this);
    }

    updateRoom() {
        console.log('Room update');
        this.setState({
            isLoading: true
        });

        GameService.updateRoom(this.props.room_id).then(() => {
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
                isLoggedIn: true
            });
        }
        const { room_id } = this.props.router.params;
        const room = GameService.getRoom(room_id).then(response => {
            this.setState({
                room: response.data
            });
        })
    }

    render() {
        return (
            <div>
                <h3>Room page</h3>
                <div>
                    <p>Room size</p>
                    <button
                        onClick={this.increaseRoomSize}
                    >+</button>
                    <button
                        onClick={this.decreaseRoomSize}
                    >-</button>
                </div>

            </div>
        )
    }
}

export default withRouter(RoomSetup);