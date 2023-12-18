const Container = {
    display: "flex",
    flexDirection: "row",
    flexWrap: "nowrap",
}

const SideColumn = {
    flexDirection: "column",
    alignItems: "stretch",
    width: "25%",
}

const PlayArea = {
    flexDirection: "column",
    width: "75%"
}

const PlayerHand = {
    display: "flex",
    flexDirection: "row",
    flexWrap: "wrap",
}

const Card = {
    width: "3em",
    height: "auto",
    border: "1px solid black",
    margin: "0.1em 0.2em",
    padding: "0.1em 0.2em",
}

const CardRankTop = {
    textAlign: "left",
}

const CardRankBottom = {
    textAlign: "right",
}

const CardSuit = {
    textAlign: "center",
}

const RedCardSuit = {
    ...CardSuit,
    color: "red",
}

const HighlightCard = {
    ...Card,
    backgroundColor: "grey",
}

const EnemyArea = {
    display: "flex",
    flexDirection: "row",
    alignContent: "center",
    justifyContent: "space-around",
    textAlign: "center",
    fontSize: "2em",
}

const EnemyHealth = {
    color: "red",
}

const EnemyAttack = {
    color: "blue",
}

const PlayedCombo = {
    display: "flex",
}

const PlayedCardsArea = {
    display: "flex",
    flexDirection: "row",
    flexWrap: "wrap",
    gap: "1em",
}

const PlayingCards = {
    backgroundColor: "green",
    color: "white",
}

const DiscardingCards = {
    backgroundColor: "red",
    color: "white",
}

const GameOver = {
    backgroundColor: "grey",
    color: "white",
}

const PlayButtons = {
    display: "flex",
    flexDirection: "row",
    paddingTop: "1em",
}


export const styles = {
    Container: Container,
    Card: Card,
    CardRankTop: CardRankTop,
    CardRankBottom: CardRankBottom,
    CardSuit: CardSuit,
    GameOver: GameOver,
    RedCardSuit: RedCardSuit,
    EnemyArea: EnemyArea,
    EnemyHealth: EnemyHealth,
    EnemyAttack: EnemyAttack,
    HighlightCard: HighlightCard,
    SideColumn: SideColumn,
    PlayArea: PlayArea,
    PlayerHand: PlayerHand,
    PlayedCardsArea: PlayedCardsArea,
    PlayButtons: PlayButtons,
    PlayedCombo: PlayedCombo,
    PlayingCards: PlayingCards,
    DiscardingCards: DiscardingCards,
}