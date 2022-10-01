import React from 'react';
import { createRoot } from 'react-dom/client';
import './regicide.css';

class Card extends React.Component {

    render() {
        let classNames = "card"
        const { rank, suit } = this.props;
        return (
            <button
            className={classNames}
            onClick={this.props.onClick}
            >
            {rank}{suit}
            </button>
        )
    };

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
        return (
            <div>
                <h1>Played cards component</h1>
            </div>
        )
    }
}

class PlayerHand extends React.Component {
    render() {
        const { hand } = this.props;
        let hand_elements = hand.map((c, i) => <Card key={i} suit={c[0]} rank={c[1]} />);
        return (
            <div>
                <h1>Cards</h1>
                {hand_elements}
            </div>
        )
    }
}

class Game extends React.Component {

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
            tavernDeckSize: [],
        };
    }


    loadData() {
        let data = {
            "enemy_deck_size": 12,
            "enemy": {
                "attack": 10,
                "card": ['J', '♣'],
                "health": 20,
            },
            "discard_deck_size": 0,
            'first_player_id': '5f684832-9106-4d7f-b69a-74bc0b8a1179',
            'hand': [['3', '♦'], ['10', '♣'], ['8', '♣'], ['5', '♥'], ['4', '♠'], ['7', '♣'], ['4', '♣']],
            'played_combos': [],
            'state': 'playing_cards',
            "tavern_deck_size": 26,
            "turn": 1,
        }

        this.setState({
            discardDeckSize: data["discard_deck_size"],
            enemy: data["enemy"],
            enemyDeckSize: data["enemy_deck_size"],
            gameState: data["state"],
            hand: data["hand"],
            player: data['first_player_id'],
            tavernDeckSize: data["tavern_deck_size"],
        });
    }

    render() {
        this.loadData();

        const { enemy, enemyDeckSize, discardDeckSize, tavernDeckSize, gameState, hand } = this.state

         return (
             <div>
                 <h1 className='status'>{gameState}</h1>

                 <EnemyDeck size={ enemyDeckSize }/>
                 <DiscardPile size={ discardDeckSize }/>
                 <TavernDeck size={ tavernDeckSize }/>
                 <Enemy
                     rank={enemy["card"][0]}
                     suit={enemy["card"][1]}
                     attack={enemy["attack"]}
                     health={enemy["health"]}
                 />
                 <PlayedCards/>
                 <PlayerHand hand={ hand }/>

             </div>
         )
    }
}

const container = document.getElementById('root');
const root = createRoot(container);
root.render(<Game />);
