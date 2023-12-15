import { apiV1 } from "./base";
const PATH = "/auth";
const TOKEN_KEY = "user"

class AuthService {
    async logIn(username, password) {
        const response = apiV1.request({
            url: `${PATH}/login`, 
            data: {
                "name": username,
                password
            },
            method: "POST",
        });
        const data = (await response).data;
        if (data.token) {
            localStorage.setItem(TOKEN_KEY, JSON.stringify(data));
        }
        return data;
    }

    logOut() {
        localStorage.removeItem(TOKEN_KEY);
    }

    async signUp(username, email, password) {
        const response = apiV1.request({
            url: `${PATH}/sign-up`, 
            data: {
                username,
                email,
                password
            },
            method: "POST"
        });
        return (await response).data;
    }

    getCurrentUser() {
        return JSON.parse(localStorage.getItem(TOKEN_KEY));
    }
}

export default new AuthService();