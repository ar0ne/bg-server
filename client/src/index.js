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
            <h1>this is discard deck</h1>
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
                <h1>this is tavern deck</h1>
                <p>Count: {size}</p>
            </div>
        );
    }
}

class EnemyDeck extends React.Component {
    render() {
        return (
            <div>
                <h1>this is enemy deck</h1>

            </div>
        )
    }
}

class CurrentEnemy extends React.Component {

    render() {
        const { enemy } = this.props;
        let rank = "";
        let suit = "";
        let health = "";
        let attack = "";
        if (enemy) {
            rank = enemy[0];
            suit = enemy[1];
        }
        return (
            <div>
                <h1>This is Current enemy component</h1>
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
        return (
            <div>
                <h1>Played cards</h1>
            </div>
        )
    }
}

class Game extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            discardDeck: [],
            enemyDeck: [],
            firstPlayer: "",
            gameState: "",
            players: [],
            tavernDeck: [],
        };
    }


    loadData() {
        let data = {'enemy_deck': [['J', '♣'], ['J', '♦'], ['J', '♥'], ['J', '♠'], ['Q', '♥'], ['Q', '♣'], ['Q', '♦'], ['Q', '♠'], ['K', '♠'], ['K', '♥'], ['K', '♣'], ['K', '♦']], 'discard_deck': [], 'first_player_id': '5f684832-9106-4d7f-b69a-74bc0b8a1179', 'players': [['5f684832-9106-4d7f-b69a-74bc0b8a1179', [['3', '♦'], ['10', '♣'], ['8', '♣'], ['5', '♥'], ['4', '♠'], ['7', '♣'], ['4', '♣']]], ['fd91c4e4-e385-47b7-9ea4-18314c8d25eb', [['9', '♦'], ['A', '♣'], ['2', '♥'], ['5', '♠'], ['4', '♥'], ['8', '♦'], ['A', '♥']]]], 'played_combos': [], 'state': 'playing_cards', 'tavern_deck': [['8', '♠'], ['9', '♥'], ['A', '♦'], ['4', '♦'], ['6', '♣'], ['7', '♥'], ['9', '♣'], ['8', '♥'], ['6', '♥'], ['5', '♣'], ['10', '♦'], ['3', '♣'], ['A', '♠'], ['5', '♦'], ['2', '♠'], ['7', '♠'], ['3', '♠'], ['2', '♣'], ['7', '♦'], ['10', '♥'], ['10', '♠'], ['6', '♠'], ['2', '♦'], ['9', '♠'], ['3', '♥'], ['6', '♦']], 'turn': 1}

        this.setState({
            discardDeck: data["discard_deck"],
            enemyDeck: data["enemy_deck"],
            firstPlayer: data["first_player_id"],
            gameState: data["state"],
            players: data["players"],
            tavernDeck: data["tavern_deck"],
        });
    }

    render() {
        this.loadData();

        const { enemyDeck, discardDeck, tavernDeck, gameState } = this.state

         return (
             <div>
                 <h1 className='status'>{gameState}</h1>

                 <EnemyDeck deck={enemyDeck}/>
                 <DiscardPile size={discardDeck.length}/>
                 <TavernDeck size={tavernDeck.length}/>
                 <CurrentEnemy enemy={enemyDeck[0]}/>
                 <PlayedCards/>
                 <PlayerHand/>

             </div>
         )
    }
}

const container = document.getElementById('root');
const root = createRoot(container);
root.render(<Game />);
