// TicTacToe
import { Component } from "react";
import { styles } from "../styles/tictactoe";
import RoomService from "../services/room.service";


const GAME_STATUS = {
    ABANDONED: "abandoned",
    DRAW: "draw",
    FINISHED: "finished",
    IN_PROGRESS: "in_progress",
}

function GameErrorNotification(props) {
    const msg = props.msg;
    return (
        <div style={styles.ErrorNotification}>
            {msg}
        </div>
    )
}


// FIXME: refactor this logic
function GameStatus(props) {
    let msg = "";
    const { status, isActivePlayer, isAnonymous, isWinner } = props;

    let style = null
    if (status === GAME_STATUS.IN_PROGRESS) {
        if (isAnonymous) {
            msg = "Game in progress.";
        } else if (isActivePlayer) {
            msg = "Your turn.";
            style = styles.ActivePlayerTurn;
        } else {
            msg = "Opponent plays.";
            style = styles.OpponentTurn;
        }
    } else if (status === GAME_STATUS.FINISHED) {
        style = styles.GameOver;
        if (isWinner) {
            msg = "Hooray! You won!";
        } else if (isAnonymous) {
            msg = "Game over!";
        } else if (isActivePlayer) {
            msg = "You lost!";
        }
    } else if (status === GAME_STATUS.DRAW || status === GAME_STATUS.ABANDONED) {
        msg = "Game over. It's a draw."
        style = styles.GameOver;
    }

    return (
        <div className="status" style={style}>
            {msg}
        </div>
    );
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

    const { crossPlayerId, status, isActivePlayer, board, onSquareClick} = props;
    const canClick = isActivePlayer && status === GAME_STATUS.IN_PROGRESS;
    const size = Math.sqrt(board.length);

    const group = (items, n) => items.reduce((acc, x, i) => {
        const idx = Math.floor(i / n);
        acc[idx] = [...(acc[idx] || []), x];
        return acc;
      }, []);

    const sign = val => {
        if (!!!val) {
            return;
        }
        return crossPlayerId === val ? 'x' : 'o'
    }

    // [0, 1, 2]
    const winnerIndexes = getWinnerIndexes(board);

    return (
        <div className="game-board-field" style={styles.GameBoardField}>
            <div>
            {group(board, size).map((row, row_idx) => (
                <div className="board-row" key={row_idx}>
                    {row.map((val, col_idx) => {
                        let idx = row_idx * size + col_idx;
                        let isHighlighted = winnerIndexes && winnerIndexes.includes(idx);
                        return (
                            <Square 
                                key={idx} 
                                value={sign(val)}
                                style={isHighlighted ? styles.RedSquare : styles.Square}
                                onSquareClick={canClick && !val ? () => onSquareClick(idx) : undefined} 
                            />
                        )
                        })
                    }
                </div>
            ))}
            </div>
        </div>
    );
};


class Game extends Component {

    constructor(props) {
        super(props);

        this.state = {
            isLoading: false,
            isErrorMessageVisible: false,
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
        RoomService.createTurnData(
            this.props.room_id, {index: idx}
        ).then(room => {
            this.setState({isLoading: false, room: room});
        }, error => {
            let message = error.response.status === 400 ? error.response?.statusText : "Something went wrong. Try again later.";
            this.showErrorMessage(message);
        });
    }

    showErrorMessage(msg) {
        this.setState({isErrorMessageVisible: true, errorMessage: msg});
        setTimeout(() => {
            this.setState({isErrorMessageVisible: false});
        }, 5000);
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

        const isAnonymous = !!!data.player_id;
        const isActivePlayer = !isAnonymous && data.active_player_id === data.player_id;
        const isWinner = !isAnonymous && data.player_id === data.winner_id;
        const crossPlayerId = data.players && data.players[0];
        const isCrossSing = data.players && data.players[0] === data.player_id;
        const { isErrorMessageVisible, errorMessage } = this.state;

        return (
            <div className="game">
                <div className="game-board" style={styles.GameBoard}>
                    <GameStatus 
                        status={data.status} 
                        isActivePlayer={isActivePlayer}
                        isAnonymous={isAnonymous} 
                        isWinner={isWinner}
                        isCrossSing={isCrossSing}
                    />
                    {isErrorMessageVisible && <GameErrorNotification msg={errorMessage} />}
                    <Board 
                        board={data.board} 
                        status={data.status}
                        isActivePlayer={isActivePlayer}
                        onSquareClick={this.handeClick.bind(this)}
                        crossPlayerId={crossPlayerId}
                    />
                </div>
            </div>
        )
    }
}

export default Game;