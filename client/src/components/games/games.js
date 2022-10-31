// Game Page component
import { Component } from "react";
import { NavLink, Outlet } from "react-router-dom";
import GameService from "../../services/game.service";


function GameList(props) {
    const games = props.games;
    const gameItems = games.map((game) => (
        <div>
            <nav>
                <NavLink
                    to={`/games/${game.name}`}
                    key={game.id}
                >
                {game.name}
                </NavLink>
            </nav>
            <Outlet />
        </div>
    ));
    return (
        <ul>{gameItems}</ul>
    );
}

export default class GameListPage extends Component {
    constructor(props) {
        super(props);

        this.state = {
            games: []
        }
    }

    render() {
        const { games } = this.state;
        return (
            <div>
                <h3>Available Game</h3>
                <GameList games={games} />
            </div>
        )
    }

    componentDidMount() {
        GameService.getAll().then(
            response => {
                this.setState({
                    games: response.data
                });
            },
            error => {
                console.log("unable to fetch games");
                console.log(
                    (error.response && error.response.data) ||
                    error.message ||
                    error.toString()
                );
            }
        )
    }
}
