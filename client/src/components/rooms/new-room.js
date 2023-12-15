// Create new game component
import { Component } from "react";
import AuthService from "../../services/auth.service";
import GameService from "../../services/game.service";
import { withRouter } from "../../common/with-router";

class NewRoom extends Component {
    constructor(props) {
        super(props);
        this.state = {
            isLoading: false,
            isLoggedIn: false
        }
        this.createNewRoom = this.createNewRoom.bind(this);
    }

    createNewRoom(e) {
        e.preventDefault();
        this.setState({isLoading: true});

        GameService.createNewGame(this.props.game_id).then(room => {
            this.setState({ isLoading: false });
            this.props.router.navigate(`/rooms/${room.id}`);
        });
    }

    componentDidMount() {
        const user = AuthService.getCurrentUser();
        if (user) {
            this.setState({ isLoggedIn: true });
        }
    }

    render() {
        return (
            <div>
                <button
                    disabled={!this.state.isLoggedIn}
                    onClick={this.createNewRoom}
                >New Game
                </button>
            </div>
        )
    }
}

export default withRouter(NewRoom);