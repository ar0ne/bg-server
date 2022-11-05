// Regicide
import { Component } from "react";


function Deck (props) {
    const isEmpty = !(props.deck && props.deck.length > 0);
//    const isHidden = !props.show;  // do show top card
    const topCard = props.deck[0];
    return (
        <div>
            This is <b>{ props.name }</b> deck.
            { isEmpty && (
                <p>Empty deck</p>
            )}
            { !isEmpty && (
                <Card rank={topCard[0]} suit={topCard[1]} />
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

        this.state = {
            data: props.data,
            room: props.room
        };

    }


    render() {
        const { data } = this.state;
        return (
            <div>
                <h4>Turn: {data.turn}</h4>
                <Deck name="enemy" deck={data.enemy_deck} />
                <Deck name="discard" deck={data.discard_deck} />
                <Deck name="tavern" deck={data.tavern_deck} />
                <PlayedCombos combos={data.played_combos} />
            </div>
        );
    }
}

export default Regicide;