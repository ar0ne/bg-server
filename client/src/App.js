import React from "react";
import {
    BrowserRouter as Router,
    Link,
    Route,
    Routes,
} from "react-router-dom";

import AuthService from "./services/auth.service";
import AuthVerify from "./common/auth-verify";
import EventBus from "./common/EventBus";
import GameDetailsPage from "./components/games/details";
import GameListPage from "./components/games/games";
import HomePage from "./components/home";
import LobbyPage from "./components/lobby";
import Login from "./components/auth/login";
import PlayerProfilePage from "./components/player";
import RoomSetup from "./components/rooms/room-setup";
import RoomTable from "./components/rooms/room-table";
import SignUp from "./components/auth/signup";


class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            currentUser: undefined,
        }
    }

    componentDidMount() {
        const user = AuthService.getCurrentUser();
        if (user) {
            this.setState({
                currentUser: user,
            })
        }
        EventBus.on("logout", () => {
            AuthService.logOut();
        });
    }

    logOut() {
        AuthService.logOut();
        window.location.href = "/login";
    }

    componentWillUnmount() {
        EventBus.remove("logout");
    }

    render() {
        const { currentUser } = this.state;
        return (
            <Router>
                <div>
                    <ul>
                        <li>
                            <Link to="/">Home</Link>
                        </li>
                        <li>
                            <Link to="/lobby">Lobby</Link>
                        </li>
                        <li>
                            <Link to="/games">Games</Link>
                        </li>

                        {currentUser && (
                          <li>
                            <Link to="/player">
                              My profile ({currentUser.user_id})
                            </Link>
                          </li>
                        )}
                        {currentUser && (
                          <li>
                            <a href="/logout" onClick={this.logOut} >Log Out</a>
                          </li>
                        )}
                        {!currentUser && (
                            <li>
                                <Link to={"/login"}>
                                    Log In
                                </Link>
                            </li>
                        )}
                        {!currentUser && (
                           <li>
                                <Link to={"/signup"}>
                                    Sign Up
                                </Link>
                           </li>
                        )}

                    </ul>

                    <hr />

                    <Routes>
                        <Route exact path="/" element={ <HomePage /> } />
                        <Route path="/login" element={ <Login /> } />
                        <Route path="/signup" element={ <SignUp /> } />
                        <Route path="/lobby" element={ <LobbyPage /> } />
                        <Route path="/player" element={ <PlayerProfilePage /> } />
                        <Route path="/games" element={ <GameListPage /> } />
                        <Route path="/games/:name" element={ <GameDetailsPage /> } />
                        <Route path="/rooms/:room_id" element={ <RoomTable /> } />
                        <Route path="/rooms/:room_id/setup" element={ <RoomSetup /> } />
                        <Route
                          path="*"
                          element={
                            <main style={{ padding: "1rem" }}>
                              <p>There's nothing here!</p>
                            </main>
                          }
                        />
                    </Routes>
                    <AuthVerify logOut={ this.logOut }/>
                </div>
            </Router>
        );
    };
}

export default App;


