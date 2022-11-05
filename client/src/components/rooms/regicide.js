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
            <h3>Player hand</h3>
            <div>
                {hand}
            </div>
        </div>
    )
}

function Deck (props) {
    const isEmpty = !(props.size);
    const card = props.card;
//    const isHidden = !props.show;  // do show top card
    return (
        <div>
            This is <b>{ props.name }</b> deck. Size is {props.size}.
            { isEmpty && (
                <p>Empty deck</p>
            )}
            { card && (
                <Card rank={card[0]} suit={card[1]} />
            )}
        </div>
    )
}

function PlayedCombos (props) {

    const combos = props.combos.map((combo) => {
        const comboCards = combo.map((card) => {
            return (
                <Card rank={card[0]} suit={card[1]} />
            );
        })
        return (
            <div>{comboCards}</div>
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

class Regicide extends Component {
    constructor(props) {
        super(props);

        const { data, room } = props;

//        this.state = {
//            data: data,
//            room: room,
//        };
    }


    render() {
        const { data } = this.props;
        if (!data) {
            return (
                <div>Game not found</div>
            )
        }
        return (
            <div>
                <h4>Turn: {data.turn}</h4>
                <Deck name="enemy" size={data.enemy_deck_size} card={data.enemy} />
                <Deck name="discard" size={data.discard_size} />
                <Deck name="tavern" size={data.tavern_size} />
                <PlayedCombos combos={data.played_combos} />
                <PlayerHand hand={data.hand} />
            </div>
        );
    }
}

export default Regicide;