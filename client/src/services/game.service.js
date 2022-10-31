// Game service
import axios from "axios";


// FIXME: hardcoded url
const API_URL = 'http://localhost:8888/api/v1/games';

class GameService {
    getAll() {
        return axios.get(API_URL + "/");
    }
    getDetails(name) {
        return axios.get(API_URL + "/" + name);
    }
}


export default new GameService();