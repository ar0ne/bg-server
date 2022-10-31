// Log Out component
import AuthService from "../../services/auth.service";

function LogOut() {
    AuthService.logOut();
    window.location.href = "/";
}

export default LogOut;