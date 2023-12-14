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



export const styles = {
    Container: Container,
    Card: Card,
    CardRankTop: CardRankTop,
    CardRankBottom: CardRankBottom,
    CardSuit: CardSuit,
    RedCardSuit: RedCardSuit,
    EnemyArea: EnemyArea,
    EnemyHealth: EnemyHealth,
    EnemyAttack: EnemyAttack,
    HighlightCard: HighlightCard,
    SideColumn: SideColumn,
    PlayArea: PlayArea,
    PlayerHand: PlayerHand,
}