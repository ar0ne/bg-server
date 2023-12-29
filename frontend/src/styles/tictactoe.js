/** styles for TicTacToe game */

const GameBoard = {

}

const GameBoardField = {
    display: "flex",
    flexDirection: "row",
    boxSizing: "border-box",
    marginTop: "1em",
}

const ErrorNotification = {
    backgroundColor: "pink",
    color: "white",
}

const Square = {
    background: "#fff",
    border: "1px solid #999",
    fontSize: "3em",
    fontWeight: "bold",
    lineHeight: "3em",
    height: "3em",
    marginRight: "-1px",
    marginTop: "-1px",
    padding: 0,
    textAlign: "center",
    width: "3em",
    float: "left",
    boxSizing: "border-box",
}

const RedSquare = {
    ...Square,
    background: "red",
}

const Status = {

}

const ActivePlayerTurn = {
    ...Status,
    background: "green",
    color: "white",
}

const OpponentTurn = {
    ...Status,
    background: "blue",
    color: "white",
}

const GameOver = {
    ...Status,
    background: "grey",
    color: "white",
}

export const styles = {
    ActivePlayerTurn: ActivePlayerTurn,
    ErrorNotification: ErrorNotification,
    GameBoard: GameBoard,
    GameBoardField: GameBoardField,
    GameOver: GameOver,
    Square: Square,
    OpponentTurn: OpponentTurn,
    RedSquare: RedSquare,
}