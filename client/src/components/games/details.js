// Game Details page component
import { Component } from "react";
import GameService from "../../services/game.service";
import NewRoom from "../rooms/new-room";
import { withRouter } from "../../common/with-router";


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

    componentDidMount() {
        const { name } = this.props.router.params;
        GameService.getDetails(name).then(game => this.setState({game: game}));
    }

    render() {
        const { game } = this.state;
        return (
            <div>
                <h3>Welcome to {game.name} page</h3>
                <p>Description: {game.description}</p>

                <NewRoom game_id={game.id} />
            </div>
        )
    }

}

export default withRouter(GameDetailsPage);