import axios from "axios";

// FIXME: hardocded url
const API_URL = "http://localhost:8888/api/v1/auth";
const TOKEN_KEY = "user"

class AuthService {
    login(user, password) {
        return axios.post(API_URL + "/login", {
            username, password
        })
        .then(response => {
            if (response.data.accessToken) {
                localStorage.setItem(TOKEN_KEY, JSON.stringify(response.data));
            }
            return response.data;
        })
    }

    logout() {
        localStorage.removeItem(TOKEN_KEY);
    }

    signup(username, email, password) {
        return axios.post(API_URL + "/sign-up", {
            username,
            email,
            password
        })
    }

    getCurrentUser() {
        return JSON.parse(localStorage.getItem(TOKEN_KEY));
    }
}

export default new AuthService();