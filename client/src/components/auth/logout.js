// Log Out component
import AuthService from "../../services/auth.service";

function LogOut() {
    AuthService.logOut();
}

export default LogOut;