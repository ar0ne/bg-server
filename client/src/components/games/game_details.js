// Game Details page component

// Game Page component
import { Component } from "react";
import {
    Navigate,
    useParams
} from "react-router-dom";
import GameService from "../../services/game.service";


function withParams(Component) {
  return props => <Component {...props} params={useParams()} />;
}


class GameDetailsPage extends Component {
    constructor(props) {
        super(props);

        this.state = {
            game: {
                "id": "",
                "name": "",
                "details": "",
                "image": "",
            }
        }
    }

    render() {
        const { game } = this.state;
        return (
            <div>
                <h3>Welcome to {game.name} page</h3>
                <p>Description: {game.description}</p>

                <h3>Create Game</h3>
                <div>Create game form</div>
            </div>
        )
    }

    componentDidMount() {
        const { name } = this.props.params;
        GameService.getDetails(name).then(
            response => {
                this.setState({
                    game: response.data
                });
            },
            error => {
                console.log("unable to fetch games");
                console.log(
                    (error.response && error.response.data) ||
                    error.message ||
                    error.toString()
                );
//                <Navigate to="/" />
            }
        )
    }
}

export default withParams(GameDetailsPage);