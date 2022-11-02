// Rooms service
import axios from "axios";
import authHeader from "./auth-header";


// FIXME: hardcoded url
const API_URL = 'http://localhost:8888/api/v1/rooms';

class RoomService {
    getAllPublicRooms() {
        return axios.get(API_URL);
    }
    updateRoom(room_id) {
        const data = {};
        return axios.put(`${API_URL}/${room_id}`, data, {
            headers: authHeader()
        });
    }
    getRoom(room_id) {
        return axios.get(`${API_URL}/${room_id}`);
    }
}

export default new RoomService();