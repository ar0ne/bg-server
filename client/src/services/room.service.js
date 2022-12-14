// Rooms service
import axios from "axios";
import authHeader from "./auth-header";


// FIXME: hardcoded url
const API_URL = 'http://localhost:8888/api/v1/rooms';

class RoomService {
    getAllPublicRooms() {
        return axios.get(API_URL);
    }
    getRoom(room_id) {
        return axios.get(`${API_URL}/${room_id}`, {
            headers: authHeader()
        });
    }
    getRoomData(room_id) {
        return axios.get(`${API_URL}/${room_id}/data`, {
            headers: authHeader()
        });
    }
    changeRoomSize(room_id, size) {
        return this.updateRoom(room_id, {size: size});
    }
    cancelRoom(room_id) {
        return this.updateRoom(room_id, {room_state: "CANCELED"});
    }
    startRoom(room_id) {
        return this.updateRoom(room_id, {room_state: "STARTED"});
    }
    updateRoom(room_id, data) {
        return axios.put(`${API_URL}/${room_id}`, data, {
            headers: authHeader()
        });
    }
    addParticipant(room_id, user_id) {
        return axios.post(`${API_URL}/${room_id}/players`, {
            user_id
        }, {
            headers: authHeader()
        });
    }
    removeParticipant(room_id, user_id) {
        return axios.delete(`${API_URL}/${room_id}/players/${user_id}`, {
            headers: authHeader()
        });
    }
}

export default new RoomService();