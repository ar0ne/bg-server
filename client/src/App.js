import React from "react";
import {
    BrowserRouter as Router,
    Link,
    Routes,
    Route,
} from "react-router-dom";

import HomePage from "./components/home";
import GameListPage from "./components/games/games";
import GameDetailsPage from "./components/games/game_details";
import PlayersPage from "./components/players";
import LobbyPage from "./components/lobby";


export default function App() {
    return (
//        <AuthProvider>
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
                            <Link to="/players">Players</Link>
                        </li>
                        <li>
                            <Link to="/games">Games</Link>
                        </li>
                    </ul>

                    <hr />

                    <Routes>
                        <Route exact path="/" element={ <HomePage />} />
                        <Route path="/lobby" element={ <LobbyPage />} />
                        <Route path="/players" element={ <PlayersPage /> } />
                        <Route path="/games" element={ <GameListPage /> } >
                            <Route path=":name" element={ <GameDetailsPage /> } />
                        </Route>
                        <Route
                          path="*"
                          element={
                            <main style={{ padding: "1rem" }}>
                              <p>There's nothing here!</p>
                            </main>
                          }
                        />
                    </Routes>
                </div>
            </Router>
//        </AuthProvider>
    );
}