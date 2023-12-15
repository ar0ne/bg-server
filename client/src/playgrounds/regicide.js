// Regicide
import { Component } from "react";
import { styles } from "../styles/regicide";
import RoomService from "../services/room.service";


function isContainsCard(card, cards) {
    return cards && cards.filter(sc => sc[0] === card[0] && sc[1] === card[1]).length > 0;
}

function PlayerHand (props) {
    if (!props.hand) {
        return (<div></div>);
    }

    const { isActivePlayer, onCardClick, playerId, selectedCards, hand } = props;
    const playerHand = hand.map((card, idx) => {
        return (
            <Card 
                key={idx+card[0]+card[1]} 
                rank={card[0]} 
                suit={card[1]}
                onCardClick={isActivePlayer ? () => onCardClick(card) : undefined}
                highlighted={selectedCards && isContainsCard(card, selectedCards)}
            />
        )
    });

    return (
        <div>
            <h5>Player ({playerId}) hand</h5>
            <div style={styles.PlayerHand}>
                {playerHand}
            </div>
        </div>
    )
}


function PlayerHands(props) {
    const { hands, playerId, selectedCards, isActivePlayer, onCardClick } = props;
    const playerHand = !!playerId && hands.filter(ph => ph.id === playerId)[0];
    const otherHands = hands.filter(ph => ph !== playerHand);
    const hiddenPlayerHands = otherHands && otherHands.map(pHand => {
        const fakeHand = [...Array(pHand.size).keys()].map(i => ['\u00A0', '\u00A0']);
        return (
            <PlayerHand
                key="fake"
                hand={fakeHand}
                playerId={pHand.id} 
                isActivePlayer={false}
            />
        );
    });
    return (
        <div>
            <PlayerHand
                hand={playerHand.hand}
                size={playerHand.size}
                selectedCards={selectedCards}
                playerId={playerHand.id} 
                isActivePlayer={isActivePlayer} 
                onCardClick={onCardClick}
            />
            {hiddenPlayerHands}
        </div>
    );
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
    const [ healthLeft, damageLeft ] = props.state;

    return (
        <div>
            { card && (
                <div style={styles.EnemyArea}>
                    <div style={styles.EnemyHealth}>
                        <div>Health</div>
                        {healthLeft}
                    </div>
                    <Card rank={rank} suit={card[1]} disabled={true} />
                    <div style={styles.EnemyAttack}>
                        <div>Attack</div>
                        {damageLeft}
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
            <div key={idx} style={styles.PlayedCombo}>
                {comboCards}
            </div>
        )
    });

    return (
        <div>
            <p>Played cards</p>
            <div style={styles.PlayedCardsArea}>
                {combos}
            </div>
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
            <div className="card-rank-top" style={styles.CardRankTop}>{rank}</div>
            <div className="card-suit" style={suitStyle}>{suit}</div>
            <div className="card-rank-botton" style={styles.CardRankBottom}>{rank}</div>
        </div>
    );
}

// FIXME: refactor this mess
function GameState(props) {
    let msg = "";
    const {status, isActivePlayer, isAnonymous, turn} = props;
    const isPlayingCards = status === "playing_cards";
    const isDiscardingCards = status === "discarding_cards";
    if (isAnonymous) {
        if (isPlayingCards) {
            msg = "Game in progress";
        } else {
            msg = "Game is over.";
        }
    } else {
        if (isPlayingCards) {
            msg = isActivePlayer ? "Your turn." : "Your partner plays.";
        } else if (isDiscardingCards) {
            msg = isActivePlayer ? "Discard cards" : "Your partners should discard cards.";
        } else if (status === "lost") {
            msg = "You have lost! Try again.";
        } else if (status === "won") {
            msg = "Hooray! You won!";
        }
    }
    const style = isPlayingCards ? styles.PlayingCards : (
        isDiscardingCards ? styles.DiscardingCards : (
            status === "lost" || status === "won" ? styles.GameOver : undefined
        )
    );
    return (
        <div style={style}><b>Turn {turn}</b>. {msg}</div>
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
                enemy_state: [],
                first_player_id: "",
                state: "",
                player_id: "",
                played_combos: [],
                tavern_size: 0,
                turn: 0,
                hands: [],
            },
            selectedCards: [],
        };
        this.handleCardClick = this.handleCardClick.bind(this);
        this.playSelectedCards = this.playSelectedCards.bind(this);
    }

    handleCardClick(card) {
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
        RoomService.createTurnData(
            this.props.room_id, {cards: selectedCards}
        ).then(room => {
            this.setState({isLoading: false, room: room, selectedCards: []});
            this.props.notifyAllAboutUpdate();
        });
    }

    componentDidUpdate(prevProps) {
        if (prevProps.data.enemy_deck_size !== this.props.data.enemy_deck_size) {
            this.setState({selectedCards: []})
        }
    }

    render() {
        const { data } = this.props;
        if (!(data && data.hands)) {
            return (
                <div>Loading...</div>
            )
        }
        const isGameInProgress = data.status === "playing_cards" || data.status === "discarding_cards";
        const { selectedCards } = this.state; 
        const hasSelectedCards = selectedCards && selectedCards.length > 0;
        const isAnonymous = !!!data.player_id;
        const isActivePlayer = !isAnonymous && isGameInProgress && data.first_player_id === data.player_id;

        return (
            <div>
                <div>
                    <GameState 
                        status={data.status} 
                        isAnonymous={isAnonymous}
                        isActivePlayer={isActivePlayer}
                        turn={data.turn} 
                    />
                </div>
                <div style={styles.Container}>
                    <div style={styles.SideColumn}>
                        <EnemyDeck name="Enemy" size={data.enemy_deck_size} />
                        <Deck name="Discard" size={data.discard_size} />
                        <Deck name="Tavern" size={data.tavern_size} />
                    </div>
                    <div style={styles.PlayArea}>
                        <EnemyCard card={data.enemy} state={data.enemy_state} />
                        <PlayedCombos combos={data.played_combos} />
                        {hasSelectedCards && (
                            <div>
                                <button onClick={this.playSelectedCards}>Play</button>
                            </div>
                        )}
                        <PlayerHands 
                            hands={data.hands}
                            selectedCards={selectedCards}
                            playerId={data.player_id} 
                            isActivePlayer={isActivePlayer} 
                            onCardClick={this.handleCardClick}
                        />
                    </div>
                </div>
            </div>
        );
    }
}

export default Game;