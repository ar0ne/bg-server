// User service
import axios from "axios";

import authHeader from "./auth-header";
import EventBus from "../common/EventBus";

// FIXME: hardcoded url
const API_URL = "http://localhost:8888/api/v1/players";

class UserService {
    getPublicDetails(user_id) {
        return axios.get(API_URL + "/" + user_id, {
            headers: authHeader()
        }).then(response => {
            return response.data;
        }, error => {
            if (error && error.response && error.response.status === 401) {
                EventBus.dispatch("logout");
            }
        })
    }
}

export default new UserService();