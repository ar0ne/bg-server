// Regicide
import { Component } from "react";
import { styles } from "../styles/regicide";


function PlayerHand (props) {
    if (!props.hand) {
        return (<div></div>);
    }
    const hand = props.hand.map((card) => {
        return (
            <Card key={(card[0] + card[1])} rank={card[0]} suit={card[1]} />
        )
    });

    return (
        <div>
            <h5>Player ({props.player_id}) hand</h5>
            <div style={styles.PlayerHand}>
                {hand}
            </div>
        </div>
    )
}

function Deck(props) {
    return (
        <div>
            <b>{ props.name }</b> deck.
            <Card rank="&nbsp;" suit={props.size} />
        </div>
    )
}

function EnemyDeck(props) {

    return (
        <Deck name={props.name} size={props.size} />
    );
}

function EnemyCard(props) {
    const card = props.card;
    if (!card || !card.length) {
        return (
            <div></div>
        )
    }
    // FIXME: we could let to configure difficulty later, for now just hardcode it
    const rank = card[0];
    const health_and_attack = {
        "J": [20, 10],
        "Q": [30, 15],
        "K": [40, 20],
    };

    const [ health, attack ] = health_and_attack[rank];

    return (
        <div>
            { card && (
                <div style={styles.EnemyArea}>
                    <div style={styles.EnemyHealth}>
                        <div>Health</div>
                        {health}
                    </div>
                    <Card rank={rank} suit={card[1]} />
                    <div style={styles.EnemyAttack}>
                        <div>Attack</div>
                        {attack}
                    </div>
                </div>
            )}
        </div>
    );
}

function PlayedCombos (props) {
    if (!props || !props.combos) {
        return
    }
    const combos = props.combos.map((combo, idx) => {
        const comboCards = combo.map((card) => {
            let key = card[0] + "_" + card[1];
            return (
                <Card key={key} rank={card[0]} suit={card[1]} />
            );
        });
        return (
            <div key={idx}>{comboCards}</div>
        )
    });

    return (
        <div>
            <p>Played combos</p>
            {combos}
        </div>
    );
}

function Card (props) {

    const redSuits = ["\u2665", "\u2666"];
    const { suit } = props;
    const suitStyle = redSuits.includes(suit) ? styles.RedCardSuit : styles.CardSuit;
    return (
        <div style={styles.Card}>
            <div style={styles.CardRankTop}>{props.rank}</div>
            <div style={suitStyle}>{props.suit}</div>
            <div style={styles.CardRankBottom}>{props.rank}</div>
        </div>
    );
}

function GameState(props) {
    let msg = "";
    const {state, is_active_player, turn} = props;
    if (state === "playing_cards") {
        msg = is_active_player ? "Your turn." : "Your partner plays.";
    }
    return (
        <div><b>Turn {turn}</b>. {msg}</div>
    )
}

class Game extends Component {
    constructor(props) {
        super(props);

        this.state = {
            data:  {
                enemy_deck_size: 0,
                discard_size: 0,
                enemy: [],
                first_player_id: "",
                state: "",
                player_id: "",
                played_combos: [],
                tavern_size: 0,
                turn: 0,
                hand: undefined,
            },
            room_id: "",
        };
    }

    render() {
        const { data } = this.props;
        if (!data) {
            return (
                <div>Game not found</div>
            )
        }
        const is_active_player = data.first_player_id === data.player_id;
        return (
            <div style={styles.Container}>
                <div style={styles.SideColumn}>
                    <GameState state={data.status} is_active_player={is_active_player} turn={data.turn} />
                    <EnemyDeck name="Enemy" size={data.enemy_deck_size} />
                    <Deck name="Discard" size={data.discard_size} />
                    <Deck name="Tavern" size={data.tavern_size} />
                </div>
                <div style={styles.PlayArea}>
                    <EnemyCard card={data.enemy} />
                    <PlayedCombos combos={data.played_combos} />
                    <PlayerHand hand={data.hand} player_id={data.player_id} />
                </div>
            </div>
        );
    }
}

export default Game;