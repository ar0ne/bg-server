import axios from "axios";

// FIXME: hardcoded url
const API_URL = `${process.env.REACT_APP_SERVER_ROOT}/auth`;
const TOKEN_KEY = "user"

class AuthService {
    logIn(username, password) {
        return axios.post(API_URL + "/login", {
            "name": username,
            password
        })
        .then(response => {
            if (response.data.token) {
                localStorage.setItem(TOKEN_KEY, JSON.stringify(response.data));
            }
            return response.data;
        })
    }

    logOut() {
        localStorage.removeItem(TOKEN_KEY);
    }

    signUp(username, email, password) {
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