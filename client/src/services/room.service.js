// Rooms service

import axios from "axios";


// FIXME: hardcoded url
const API_URL = 'http://localhost:8080/api/v1/rooms';

class RoomService {
    getAllPublicRooms() {
        return axios.get(API_URL + "/");
    }
}


export default new RoomService();