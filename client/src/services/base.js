import axios from "axios"
import authHeader from "./auth-header";

export const apiV1 = axios.create({
    baseURL: process.env.REACT_APP_SERVER_ROOT,
    headers: authHeader(),
});

// defining a custom error handler for all APIs
const errorHandler = (error) => {
    const statusCode = error.response?.status

    // logging only errors that are not 401
    if (statusCode && statusCode !== 401) {
        console.error(error)
    }

    return Promise.reject(error)
}

// registering the custom error handler to the
// "api" axios instance
apiV1.interceptors.response.use(undefined, (error) => {
    return errorHandler(error)
})