// Regicide
import { Component } from "react";
import { styles } from "../styles/regicide";
import RoomService from "../services/room.service";
import AuthService from "../services/auth.service";


const GameStatus = {
    PLAY: "playing_cards",
    DISCARD: "discarding_cards",
    LOST: "lost",
    WON: "won",
}

function isContainsCard(card, cards) {
    return cards && cards.filter(sc => sc[0] === card[0] && sc[1] === card[1]).length > 0;
}

function PlayerHand (props) {
    if (!props.hand) {
        return (<div></div>);
    }

    const { isActivePlayer, onCardClick, playerId, selectedCards, hand, currentUserId } = props;
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

    const greetings = (currentUserId && currentUserId === playerId) ? "Your hand" : `Player hand`;

    return (
        <div>
            <h5>{greetings}</h5>
            <div style={styles.PlayerHand}>
                {playerHand}
            </div>
        </div>
    )
}

function PlayerHands(props) {
    const { hands, playerId, selectedCards, isActivePlayer, onCardClick, currentUserId } = props;
    const playerHand = !!playerId && hands.filter(ph => ph.id === playerId)[0];
    const otherHands = hands.filter(ph => ph !== playerHand);
    const hiddenPlayerHands = otherHands && otherHands.map(pHand => {
        const fakeHand = [...Array(pHand.size).keys()].map(i => ['\u00A0', '\u00A0']);
        return (
            <PlayerHand
                key={pHand.id}
                hand={fakeHand}
                playerId={pHand.id} 
                isActivePlayer={false}
            />
        );
    });
    return (
        <div>
            {playerHand && <PlayerHand
                hand={playerHand.hand}
                size={playerHand.size}
                selectedCards={selectedCards}
                playerId={playerHand.id}
                currentUserId={currentUserId}
                isActivePlayer={isActivePlayer} 
                onCardClick={onCardClick}
            />
            }
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
    const { status, isActivePlayer, isAnonymous, turn } = props;
    const isPlayingCards = status === GameStatus.PLAY;
    const isDiscardingCards = status === GameStatus.DISCARD;
    const isLoseGame = status === GameStatus.LOST;
    const isWinGame = status === GameStatus.WON;

    let style = null;
    if (isPlayingCards) {
        style = styles.PlayingCards;
        if (isAnonymous) {
            msg = "Playing cards.";
        } else if (isActivePlayer) {
            msg = "Play cards or skip.";
        } else {
            msg = "Your partner plays";
        }
    } else if (isDiscardingCards) {
        style = styles.DiscardingCards;
        if (isAnonymous) {
            msg = "Discarding cards.";
        } else if (isActivePlayer) {
            msg = "Discard cards to defeat enemy attack.";
        } else {
            msg = "Your partner should discard cards.";
        }
    } else if (isLoseGame) {
        style = styles.GameOver;
        if (isAnonymous) {
            msg = "Game over.";
        } else {
            msg = "You lost! Try again.";
        }
    } else if (isWinGame) {
        style = styles.GameOver;
        if (isAnonymous) {
            msg = "Game over. Victory!";
        } else {
            msg = "Hooray! You won!";
        }
    }

    return (
        <div style={style}><b>Turn {turn}</b>. {msg}</div>
    )
}

function GameErrorNotification(props) {
    const msg = props.msg;
    return (
        <div style={styles.ErrorNotification}>
            {msg}
        </div>
    )
}

class Game extends Component {
    constructor(props) {
        super(props);
        this.state = {
            currentUserId: "",
            data:  {
                enemy_deck_size: 0,
                discard_size: 0,
                enemy: [],
                enemy_state: [],
                active_player_id: "",
                state: "",
                player_id: "",
                played_combos: [],
                tavern_size: 0,
                turn: 0,
                hands: [],
            },
            errorMessage: "",
            isErrorMessageVisible: false,
            selectedCards: [],
        };
        this.handleCardClick = this.handleCardClick.bind(this);
        this.playSelectedCards = this.playSelectedCards.bind(this);
        this.playSkipCards = this.playSkipCards.bind(this);
    }

    showErrorMessage(msg) {
        this.setState({isErrorMessageVisible: true, errorMessage: msg});
        setTimeout(() => {
            this.setState({isErrorMessageVisible: false});
        }, 5000);
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
            this.setState({isLoading: false, room: room, selectedCards: [], isErrorMessageVisible: false});
            this.props.notifyAllAboutUpdate();
        }, error => {
            let message = error.response.status === 400 ? error.response?.statusText : "Something went wrong. Try again later.";
            this.showErrorMessage(message);
            this.setState({selectedCards: []});
        });
    }

    playSkipCards() {
        RoomService.createTurnData(
            this.props.room_id, {cards: []}
        ).then(room => {
            this.setState({isLoading: false, room: room, selectedCards: [], isErrorMessageVisible: false});
            this.props.notifyAllAboutUpdate();
        }, error => {
            let message = error.response.status === 400 ? error.response?.statusText : "Something went wrong. Try again later.";
            this.showErrorMessage(message);
            this.setState({selectedCards: []});
        });
    }

    componentDidMount() {
        const user = AuthService.getCurrentUser();
        if (user) {
            this.setState({ currentUserId: user.user_id });
        }
    }

    componentDidUpdate(prevProps) {
        if (prevProps.data.enemy_deck_size !== this.props.data.enemy_deck_size) {
            this.setState({selectedCards: []})
        }
    }

    render() {
        const { data } = this.props;
        const { currentUserId, errorMessage, isErrorMessageVisible } = this.state;
        if (!(data && data.hands)) {
            return (
                <div>Loading...</div>
            )
        }
        const isAnonymous = !!!data.player_id;
        const isGameInProgress = data.status === GameStatus.PLAY || data.status === GameStatus.DISCARD;
        const isActivePlayer = !isAnonymous && isGameInProgress && data.active_player_id === data.player_id;
        const { selectedCards } = this.state; 
        const hasSelectedCards = isActivePlayer && selectedCards && selectedCards.length > 0;
        const canSkipCards = isActivePlayer && data.status === GameStatus.PLAY;

        return (
            <div>
                <div>
                    <GameState 
                        status={data.status} 
                        isAnonymous={isAnonymous}
                        isActivePlayer={isActivePlayer}
                        turn={data.turn} 
                    />
                    {isErrorMessageVisible && <GameErrorNotification msg={errorMessage} />}
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
                        <div className="play-buttons" style={styles.PlayButtons}>
                            {hasSelectedCards && (
                                <div>
                                    <button onClick={this.playSelectedCards}>Play</button>
                                </div>
                            )}
                            {canSkipCards && (
                                <div>
                                    <button onClick={this.playSkipCards}>Skip</button>
                                </div>
                            )}
                        </div>
                        <PlayerHands 
                            hands={data.hands}
                            selectedCards={selectedCards}
                            playerId={data.player_id} 
                            isActivePlayer={isActivePlayer}
                            currentUserId={currentUserId}
                            onCardClick={this.handleCardClick}
                        />
                    </div>
                </div>
            </div>
        );
    }
}

export default Game;