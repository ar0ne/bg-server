// TicTacToe
import { Component } from "react";
import { styles } from "../styles/tictactoe";
import RoomService from "../services/room.service";


// FIXME: refactor this logic
function GameStatus(props) {
    let msg = "";
    const {status, is_active_player, is_anonymous, is_winner} = props;
    if (status === "in_progress") {
        if (!is_anonymous) {
            msg = is_active_player ? "Your turn." : "Your opponent turn.";
        } else {
            msg = "Game in progress.";
        }
    } else if (status === "finished") {
        if (is_winner) {
            msg = "Hooray! You won!";
        } else if (is_anonymous) {
            msg = "Game over!";
        } else if (is_active_player) {
            msg = "You lost!";
        }
    }
    return <h5>{msg}</h5>
}


function Square({ value, onSquareClick, style }) {
    return (
        <button className="square" onClick={onSquareClick} style={style}>
            {value}
        </button>
    );
}


function getWinnerIndexes(squares) {
    const lines = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6],
    ];
    for (let i = 0; i < lines.length; i++) {
        const [a, b, c] = lines[i];
        if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]) {
            return [a, b, c];
        }
    }
    return null;
}


function Board(props) {

    if (!props || !props.board) {
        return (
            <div>Can't draw a board.</div>
        )
    }

    const canClick = props.is_active_player && props.status === "in_progress";
    const items = props.board;
    const size = Math.sqrt(items.length);
    const cross_player_id = props.cross_player_id;

    const group = (items, n) => items.reduce((acc, x, i) => {
        const idx = Math.floor(i / n);
        acc[idx] = [...(acc[idx] || []), x];
        return acc;
      }, []);

    const sign = (val) => {
        if (!!!val) {
            return;
        }
        return cross_player_id === val ? 'x' : 'o'
    }

    // [0, 1, 2]
    const winnerIndexes = getWinnerIndexes(items);

    return (
        <div className="game-board">
            {group(items, size).map((row, row_idx) => (
                <div className="board-row" key={row_idx}>
                    {row.map((val, col_idx) => {
                        let idx = row_idx * size + col_idx;
                        let isHighlighted = winnerIndexes && winnerIndexes.includes(idx);
                        return (
                            <Square 
                                key={idx} 
                                value={sign(val)}
                                style={isHighlighted ? styles.RedSquare : styles.Square}
                                onSquareClick={canClick ? () => props.onSquareClick(idx) : undefined} 
                            />
                        )
                        })
                    }
                </div>
            ))}
        </div>
    );
};


class Game extends Component {

    constructor(props) {
        super(props);

        this.state = {
            isLoading: false,
            room_id: "",
            data: {
                active_player_id: "",
                board: [],
                players: "",
                player_id: "",
                status: "",
                turn: 0,
                winner_id: "",
            }
        }
    }

    handeClick(idx) {
        this.setState({ isLoading: true });

        // send http request, but wait for ws hook to make data refresh?
        RoomService.createTurnData(
            this.props.room_id, {index: idx}
        ).then(response => {
            console.log("successfuly sent turn data");
            this.setState({isLoading: false});
            // this.props.fetchRoomData();
            this.props.notifyAllAboutUpdate();
        },
        error => {
            console.log("unable to make a turn");
            console.log(
                (error.response &&
                error.response.data &&
                error.response.data.error &&
                error.response.data.error.message) ||
                error.message ||
                error.toString()
            );
        })
    }

    render() {
        /**
        {
            "data": 
            {
                "active_player_id": "uuid-2", 
                "players": ["uuid-1", "uuid-2"], 
                "player_id": null,
                "board": [
                    "uuid-1", null, null
                    null, "uuid1", null 
                    null, null, "uuid2"
                ], 
                "status": "in_progress", 
                "turn": 4,
                "winner_id": null
            }
        }
        **/
        const { data } = this.props;
        if (!data) {
            return (
                <div>Game not found</div>
            )
        }

        const is_active_player = data.active_player_id === data.player_id;
        const is_anonymous = !!!data.player_id;
        const is_winner = !is_anonymous && data.player_id === data.winner_id;
        const cross_player_id = data.players && data.players[0]

        return (
            <div className="game" style={styles.Game}>
                <GameStatus 
                    status={data.status} 
                    is_active_player={is_active_player} 
                    is_anonymous={is_anonymous} 
                    is_winner={is_winner}
                />
                <Board 
                    board={data.board} 
                    status={data.status}
                    is_active_player={is_active_player}
                    onSquareClick={this.handeClick.bind(this)}
                    cross_player_id={cross_player_id}
                />
            </div>
        )
    }
}

export default Game;