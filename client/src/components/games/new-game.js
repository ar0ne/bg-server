// Create new game component
import { Component } from "react";
import GameService from "../../services/game.service";
import AuthService from "../../services/auth.service";
import { withRouter } from "../../common/with-router";

class NewGame extends Component {
    constructor(props) {
        super(props);
        this.state = {
            isLoading: false,
            isLoggedIn: false
        }
        this.createNewGame = this.createNewGame.bind(this);
    }

    createNewGame(e) {
        e.preventDefault();
        console.log('Room created');
        this.setState({
            isLoading: true
        });

        GameService.createNewGame(this.props.game_id).then(response => {
            this.setState({ isLoading: false });
            this.props.router.navigate(`/rooms/${response.data.id}`);
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

    componentDidMount() {
        const user = AuthService.getCurrentUser();
        if (user) {
            this.setState({
                isLoggedIn: true
            });
        }
    }

    render() {
        return (
            <div>
                <button
                    disabled={!this.state.isLoggedIn}
                    onClick={this.createNewGame}
                >New Game
                </button>
            </div>
        )
    }
}

export default withRouter(NewGame);