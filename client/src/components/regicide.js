import React from 'react';

function Card(props) {
    let classNames = "card"
    const { rank, suit } = props;
    return (
        <button
            className={classNames}
            onClick={props.onClick}
        >
            {rank}{suit}
        </button>
    )
}

function CardCombo (props) {
    let { combo } = props;
    let combos = combo.map((card, i) => <Card key={i} rank={card[0]} suit={card[1]} />);
    return (
        <div className="card-combo">
            {combos}
        </div>
    )
}


class DiscardPile extends React.Component {
    render() {
        const { size } = this.props;
        return (
            <div>
                <h1>Discard deck</h1>
                <p>Count: {size}</p>
            </div>
        )
    }
}

class GameBanner extends React.Component {

    handleOnConfirm(event) {
        event.preventDefault();
        console.log("Confirmed!")
    }

    handleOnCancel(event) {
        event.preventDefault();
        console.log("Cancelled!")
    }

    render() {

        return (
            <div className="banner">
                Some text here
                <button
                    onClick={(event) => this.handleOnConfirm(event)}
                    className="btn-confirm"
                >Confirm</button>
                <button
                    onClick={(event) => this.handleOnCancel(event)}
                    className="btn-cancel"
                >Cancel</button>
            </div>
        )
    }
}

class TavernDeck extends React.Component {
    render() {
        const { size } = this.props;
        return (
            <div>
                <h1>Tavern deck</h1>
                <p>Count: {size}</p>
            </div>
        );
    }
}

class EnemyDeck extends React.Component {
    render() {
        const { size } = this.props;
        return (
            <div>
                <h1>Enemy deck</h1>
                <p>Left: { size }</p>
            </div>
        )
    }
}

class Enemy extends React.Component {

    render() {
        const { rank, suit, health, attack } = this.props;

        return (
            <div>
                <h1>Enemy</h1>
                <p>Health: {health}</p>
                <p>Attack: {attack}</p>
                <Card
                    rank={rank}
                    suit={suit}
                    onClick={() => console.log("do nothing")}
                />
            </div>
        )
    }
}

class PlayedCards extends React.Component {

    render() {
        const { combos } = this.props;
        let cardCombos = combos.map((combo, i) => <CardCombo key={i} combo={combo} />);
        return (
            <div>
                <h1>Played cards component</h1>
                <div className="card-combo-list">
                    {cardCombos}
                </div>
            </div>
        )
    }
}

class PlayerHand extends React.Component {
    render() {
        const { hand } = this.props;
        let hand_elements = hand.map((c, i) => <Card key={i} suit={c[1]} rank={c[0]} />);
        return (
            <div>
                <h1>Cards</h1>
                {hand_elements}
            </div>
        )
    }
}

export default class Game extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            discardDeckSize: 0,
            enemyDeckSize: 0,
            enemy: {
                "attack": 0,
                "card": [],
                "health": 0,
            },
            gameState: "",
            hand: [],
            player: "",
            playedCombos: [],
            tavernDeckSize: [],
            turn: 0,
        };
    }


    loadData() {
        let data = {
            "enemy_deck_size": 12,
            "enemy": {
                "attack": 10,
                "card": ['J', '???'],
                "health": 20,
            },
            "discard_deck_size": 0,
            'first_player_id': '5f684832-9106-4d7f-b69a-74bc0b8a1179',
            'hand': [['3', '???'], ['8', '???'], ['5', '???'], ['4', '???'], ['7', '???'], ['4', '???']],
            'played_combos': [[['10', '???']], [['A', '???'], ['2', '???']]],
            'state': 'playing_cards',
            "tavern_deck_size": 26,
            "turn": 2,
        }

        this.setState({
            discardDeckSize: data["discard_deck_size"],
            enemy: data["enemy"],
            enemyDeckSize: data["enemy_deck_size"],
            gameState: data["state"],
            hand: data["hand"],
            player: data['first_player_id'],
            playedCombos: data["played_combos"],
            tavernDeckSize: data["tavern_deck_size"],
            turn: data["turn"],
        });
    }

    componentDidMount() {
        this.loadData();
    }


    render() {
        const {
            discardDeckSize,
            enemy,
            enemyDeckSize,
            gameState,
            hand,
            playedCombos,
            tavernDeckSize,
            turn
        } = this.state

        return (
            <div>
                <GameBanner />
                <h1 className='status'>State: { gameState }, Turn: { turn }</h1>

                <EnemyDeck size={ enemyDeckSize }/>
                <DiscardPile size={ discardDeckSize }/>
                <TavernDeck size={ tavernDeckSize }/>
                <Enemy
                    rank={enemy["card"][0]}
                    suit={enemy["card"][1]}
                    attack={enemy["attack"]}
                    health={enemy["health"]}
                />
                <PlayedCards combos={ playedCombos }/>
                <PlayerHand hand={ hand }/>

            </div>
        )
    }
}