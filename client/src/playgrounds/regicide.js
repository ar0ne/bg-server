// Regicide
import { Component } from "react";


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
            <h3>Player ({props.player_id}) hand</h3>
            <div>
                {hand}
            </div>
        </div>
    )
}

function Deck(props) {
    const isEmpty = !(props.size);
//    const isHidden = !props.show;  // do show top card
    return (
        <div>
            This is <b>{ props.name }</b> deck. Size is {props.size}.
            { isEmpty && (
                <p>Empty deck</p>
            )}
            { !isEmpty && (
                <p>...</p>
            )}
        </div>
    )
}

function EnemyDeck(props) {
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
            <Deck name={props.name} size={props.size} />
            { card && (
                <div>
                    <Card rank={rank} suit={card[1]} />
                    <p>Health: {health}</p>
                    <p>Attack: {attack}</p>
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
    return (
        <div>
            Card is {props.rank} {props.suit}
        </div>
    );
}

function GameState(props) {
    let msg = "";
    const {state, is_active_player} = props;
    if (state === "playing_cards") {
        msg = is_active_player ? "You should play cards or yield (TBA)." : "Your partner plays.";
    }
    return (
        <div>{msg}</div>
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
            <div>
                <GameState state={data.state} is_active_player={is_active_player} />
                <h5>Turn: {data.turn}</h5>
                <EnemyDeck name="enemy" size={data.enemy_deck_size} card={data.enemy} />
                <Deck name="discard" size={data.discard_size} />
                <Deck name="tavern" size={data.tavern_size} />
                <PlayedCombos combos={data.played_combos} />
                <PlayerHand hand={data.hand} player_id={data.player_id} />
            </div>
        );
    }
}

export default Game;