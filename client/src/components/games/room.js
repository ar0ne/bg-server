// Create new game component
import { Component } from "react";
import GameService from "../../services/game.service";
import { withRouter } from "../../common/with-router";

class GameRoom extends Component {
    constructor(props) {
        super(props);

        this.state = {
            isLoading: false,
        }

        this.createRoom = this.createRoom.bind(this);
    }

    createRoom(e) {
        e.preventDefault();
        console.log('Created');
        this.setState({
            isLoading: true
        });

        GameService.createRoom(this.props.game_id).then(() => {
            console.log("room created");

        },
        error => {
            console.log("unable to create game room");
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

    render() {
        return (
            <div>
                <button onClick={this.createRoom}>
                    New Game
                </button>
            </div>
        )
    }
}

export default withRouter(GameRoom);