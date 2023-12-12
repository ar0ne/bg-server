// TicTacToe
import { Component } from "react";
import { styles } from "../styles/tictactoe";
import RoomService from "../services/room.service";


function GameStatus(props) {
    let msg = "";
    const {status, is_active_player, is_anonymous} = props;
    if (status === "in_progress") {
        if (!is_anonymous) {
            msg = is_active_player ? "Your turn." : "Your opponent turn.";
        } else {
            msg = "Game in progress."
        }
    }
    return (
        <h5>{msg}</h5>
    )
}


function Square({ value, onSquareClick }) {
    return (
        <button className="square" onClick={onSquareClick} style={styles.Square}>
            {value}
        </button>
    );
}

function Board(props) {

    // todo: highlight if game is finished in different colors depends on player

    if (!props || !props.board) {
        return (
            <div>Can't draw a board.</div>
        )
    }

    const canClick = props.is_active_player && props.status == "in_progress";
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

    return (
        <div className="game-board">
            {group(items, size).map((row, row_idx) => (
                <div className="board-row" key={row_idx}>
                    {row.map((val, col_idx) => {
                        let idx = row_idx * size + col_idx;
                        return (
                            <Square 
                                key={idx} 
                                value={sign(val)}
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
                players: "",
                player_id: "",
                board: [],
                status: "",
                turn: 0,
            }
        }
    }

    handeClick(idx) {
        console.log(idx);
        this.setState({ isLoading: true });

        RoomService.createTurnData(
            this.props.room_id, {cell: idx}
        ).then(response => {
            console.log(response);
            this.setState({isLoading: false});
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
            "active_player_id": "uuid-2", 
            "players": ["uuid-1", "uuid-2"], 
            "player_id": null,
            "board": [
                "uuid-1", null, null
                null, "uuid1", null 
                null, null, "uuid2"
            ], 
            "status": "in_progress", 
            "turn": 4
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
        const cross_player_id = data.players && data.players[0]

        return (
            <div className="game" style={styles.Game}>
                <GameStatus 
                    status={data.status} 
                    is_active_player={is_active_player} 
                    is_anonymous={is_anonymous} 
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