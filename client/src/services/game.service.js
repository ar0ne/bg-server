// Game service
import axios from "axios";

import authHeader from "./auth-header";


// FIXME: hardcoded url
const API_URL = 'http://localhost:8888/api/v1/games';

class GameService {
    getAll() {
        return axios.get(API_URL);
    }
    getDetails(game_name) {
        return axios.get(`${API_URL}/${game_name}`);
    }
    createNewGame(game_id) {
        // FIXME: do we want to let setup room size and participants at creation
        return axios.post(`${API_URL}/${game_id}/rooms`, null, {
            headers: authHeader()
        });
    }
}

export default new GameService();