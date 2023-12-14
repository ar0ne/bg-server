// Regicide
import { Component } from "react";
import { styles } from "../styles/regicide";


function isContainsCard(card, cards) {
    return cards.filter(sc => sc[0] === card[0] && sc[1] === card[1]).length > 0;
}

function PlayerHand (props) {
    if (!props.hand) {
        return (<div></div>);
    }

    const { isActivePlayer, onCardClick, playerId, selectedCards } = props;
    const hand = props.hand.map((card) => {
        return (
            <Card 
                key={(card[0] + card[1])} 
                rank={card[0]} 
                suit={card[1]}
                onCardClick={isActivePlayer ? () => onCardClick(card) : undefined}
                highlighted={isContainsCard(card, selectedCards)}
            />
        )
    });

    return (
        <div>
            <h5>Player ({playerId}) hand</h5>
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
            <Card rank="&nbsp;" suit={props.size} disabled={true} />
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
    const healthAndAttack = {
        "J": [20, 10],
        "Q": [30, 15],
        "K": [40, 20],
    };

    const [ health, attack ] = healthAndAttack[rank];

    return (
        <div>
            { card && (
                <div style={styles.EnemyArea}>
                    <div style={styles.EnemyHealth}>
                        <div>Health</div>
                        {health}
                    </div>
                    <Card rank={rank} suit={card[1]} disabled={true} />
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
                <Card key={key} rank={card[0]} suit={card[1]} disable={true} />
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

    const { suit, rank, disabled, highlighted, onCardClick } = props;
    const redSuits = ["\u2665", "\u2666"];
    const suitStyle = redSuits.includes(suit) ? styles.RedCardSuit : styles.CardSuit;
    return (
        <div 
            style={highlighted ? styles.HighlightCard : styles.Card} 
            onClick={!disabled ? onCardClick: undefined} 
            role="button" 
            tabIndex={disabled ? "-1" : "0"}
            aria-disabled={disabled}
            >
            <div style={styles.CardRankTop}>{rank}</div>
            <div style={suitStyle}>{suit}</div>
            <div style={styles.CardRankBottom}>{rank}</div>
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
            selectedCards: [],
        };
        this.handleCardClick = this.handleCardClick.bind(this);
        this.playSelectedCards = this.playSelectedCards.bind(this);
    }

    handleCardClick(card) {
        console.log("handleCardClick", card);
        const { selectedCards } = this.state;
        if (isContainsCard(card, selectedCards)) {
            let cards = selectedCards.filter((c) => c[0] !== card[0] || c[1] !== card[1]);
            this.setState({selectedCards: cards})
        } else{
            this.setState({selectedCards: [...selectedCards, card]})
        }
    }

    playSelectedCards() {
        const { selectedCards } = this.state;
        console.log("play cards", selectedCards);
    }

    render() {
        const { data } = this.props;
        if (!data) {
            return (
                <div>Loading...</div>
            )
        }
        const hand = data.hand;
        const { selectedCards } = this.state; 
        const hasSelectedCards = selectedCards && selectedCards.length > 0;

        const isActivePlayer = data.first_player_id === data.player_id;
        return (
            <div style={styles.Container}>
                <div style={styles.SideColumn}>
                    <GameState state={data.status} isActivePlayer={isActivePlayer} turn={data.turn} />
                    <EnemyDeck name="Enemy" size={data.enemy_deck_size} />
                    <Deck name="Discard" size={data.discard_size} />
                    <Deck name="Tavern" size={data.tavern_size} />
                </div>
                <div style={styles.PlayArea}>
                    <EnemyCard card={data.enemy} />
                    <PlayedCombos combos={data.played_combos} />
                    {hasSelectedCards && (
                        <div>
                            <button onClick={this.playSelectedCards}>Play</button>
                        </div>
                    )}
                    <PlayerHand 
                        hand={hand} 
                        selectedCards={selectedCards}
                        playerId={data.player_id} 
                        isActivePlayer={isActivePlayer} 
                        onCardClick={this.handleCardClick}
                    />
                </div>
            </div>
        );
    }
}

export default Game;