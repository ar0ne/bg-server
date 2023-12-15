// Rooms service
import { apiV1 } from "./base";

const PATH = "/rooms";

const RoomStatus = {
    CREATED: 0,
    STARTED: 1,
    CANCELED: 2,
    FINISHED: 3,
    ABANDONED: 4,
};

class RoomService {
    async getAllPublicRooms() {
        const response = apiV1.request({
            url: PATH,
            method: "GET",
        });
        return (await response).data?.results;
    }
    async getRoom(room_id) {
        const response =  apiV1.request({
            url: `${PATH}/${room_id}`,
            method: "GET",
        });
        return (await response).data?.data;
    }
    async getRoomData(room_id) {
        const response =  apiV1.request({
            url: `${PATH}/${room_id}/data`, 
            method: "GET",
        });
        return (await response).data?.data;
    }
    async createTurnData(room_id, data) {
        const response = apiV1.request({
            url: `${PATH}/${room_id}/turn`, 
            data: data,
            method: "POST",
        });
        return (await response).data?.data;
    }
    async changeRoomSize(room_id, size) {
        return this.updateRoom(room_id, {size: size});
    }
    async cancelRoom(room_id) {
        return this.updateRoom(room_id, {status: RoomStatus.CANCELED});
    }
    async startRoom(room_id) {
        return this.updateRoom(room_id, {status: RoomStatus.STARTED});
    }
    async updateRoom(room_id, data) {
        const response = apiV1.request({
            url: `${PATH}/${room_id}`,
            data: data,
            method: "PUT",
        });
        return (await response).data?.data;
    }
    async addParticipant(room_id, user_id) {
        const response = apiV1.request({
            url: `${PATH}/${room_id}/players`, 
            data: {user_id},
            method: "POST",
        });
        return (await response).data?.data;
    }
    async removeParticipant(room_id, user_id) {
        const response = apiV1.request({
            url: `${PATH}/${room_id}/players/${user_id}`, 
            method: "DELETE",
        });
        // empty response
        return (await response).data;
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
        return room && room.status === RoomStatus.CANCELED;
    }
};

export default new RoomService();