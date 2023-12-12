// TicTacToe
import { Component } from "react";
import { styles } from "../styles/tictactoe";


function GameState(props) {
    let msg = "";
    const {state, is_active_player, is_anonymous} = props;
    if (state === "in_progress") {
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

    function handeClick(row, col) {
        console.log(row, col);
    }

    // todo: highlight if game is finished in different colors depends on player

    if (!props || !props.board) {
        return (
            <div>Can't draw a board.</div>
        )
    }

    const canClick = props.is_active_player;

    const board = props.board.map((line, line_idx) => {
        const row = line.map((val, sq_idx) => {
            let key = line_idx + "_" + sq_idx;
            return (
                <Square 
                    key={key} 
                    value={val}
                    onSquareClick={canClick ? () => handeClick(line_idx, sq_idx): undefined} 
                />
            )

        })
        return (
            <div className="board-row" key={line_idx}>
                {row}
            </div>
        )

    });

    return (
        <div id="game-board">
            {board}
        </div>
    )
}


class Game extends Component {
    constructor(props) {
        super(props);

        this.state = {
            room_id: "",
            data: {
                active_player_id: "",
                players: "",
                player_id: "",
                board: [],
                state: "",
                turn: 0,
            }
        }
    }

    render() {
        /**
        {
            "active_player_id": "uuid-2", 
            "players": ["uuid-1", "uuid-2"], 
            "player_id": null,
            "board": [
                ["uuid-1", null, null], 
                [null, "uuid1", null], 
                [null, null, "uuid2"]
            ], 
            "state": "in_progress", 
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

        return (
            <div className="game" style={styles.Game}>
                <GameState 
                    state={data.state} 
                    is_active_player={is_active_player} 
                    is_anonymous={is_anonymous} 
                />
                <Board 
                    board={data.board} 
                    is_active_player={is_active_player} 
                />
            </div>
        )
    }
}

export default Game;