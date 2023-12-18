// Game Page component
import { Component } from "react";
import { NavLink, Outlet } from "react-router-dom";
import GameService from "../../services/game.service";


function GameList(props) {
    const games = props.games;
    if (!(games && games.length)) {
        return (<p>No Available games!</p>);
    }
    const gameItems = games.map((game) => (
        <div key={game.id}>
            <li>
                <NavLink
                    to={`/games/${game.name}`}
                >
                {game.name}
                </NavLink>
            </li>
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

    componentDidMount() {
        GameService.getAll().then(games => this.setState({games: games}));
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

}
