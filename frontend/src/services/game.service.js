import { apiV1 } from "./base";

const PATH = "/games";

class GameService {
    async getAll() {
        const response = apiV1.request({
            url: PATH,
            method: "GET",
        });
        return (await response).data?.results;
    }
    async getDetails(game_name) {
        const response = apiV1.request({
            url: `${PATH}/${game_name}`,
            method: "GET",
        });
        return (await response).data?.data;
    }
    async createNewGame(game_id) {
        // FIXME: do we want to let setup room size and participants at creation
        const response = apiV1.request({
            url: `${PATH}/${game_id}/rooms`, 
            method: "POST",
        });
        return (await response).data?.data;
    }
}

export default new GameService();