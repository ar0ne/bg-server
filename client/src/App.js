import React from "react";
import {
    BrowserRouter as Router,
    Routes,
    Route,
    Link
} from "react-router-dom";

// import Game from './regicide';
import HomePage from "./home";
import GamesPage from "./games";
import PlayersPage from "./players"


export default function App() {
    return (
        <Router>
            <div>
                <ul>
                    <li>
                        <Link to="/">Home</Link>
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
                    <Route exact path="/" element={ <HomePage />}/>
                    <Route path="/players" element={<PlayersPage />}/>
                    <Route path="/games" element={<GamesPage />}/>
                </Routes>
            </div>
        </Router>
    );
}