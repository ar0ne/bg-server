// User service
import { apiV1 } from "./base";

import EventBus from "../common/EventBus";

const PATH = "/players";

class UserService {
    async getPublicDetails(user_id) {
        const response = apiV1.request({
            url: `${PATH}/${user_id}`,
            method: "GET",
        }, error => {
            if (error && error.response && error.response.status === 401) {
                EventBus.dispatch("logout");
            }
        });
        return (await response).data?.player;
    }
}

export default new UserService();