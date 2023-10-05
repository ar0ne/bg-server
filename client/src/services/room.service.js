// Rooms service
import axios from "axios";
import authHeader from "./auth-header";


// FIXME: hardcoded url
const API_URL = 'http://localhost:8888/api/v1/rooms';

const RoomStatus = {
    CREATED: 0,
    STARTED: 1,
    CANCELED: 2,
    FINISHED: 3,
    ABANDONED: 4,
};

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
        return this.updateRoom(room_id, {status: RoomStatus.CANCELED});
    }
    startRoom(room_id) {
        return this.updateRoom(room_id, {status: RoomStatus.STARTED});
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
    getRoomStatus(room_status) {
        switch(room_status) {
            case RoomStatus.CREATED:
                return "Created"
            case RoomStatus.STARTED:
                return "Started"
            case RoomStatus.CANCELED:
                return "Canceled"
            case RoomStatus.FINISHED:
                return "Finished"
            case RoomStatus.ABANDONED:
                return "Abandoned"
            default:
                return "Unknown"
        }
    }
    isCreated(room) {
        return room && room.status === RoomStatus.CREATED;
    }
    isStarted(room) {
        return room && room.status === RoomStatus.STARTED;
    }
    isCanceled(room) {
        return room && room.status == RoomStatus.CANCELED;
    }
};

export default new RoomService();