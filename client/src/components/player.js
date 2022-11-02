// Player profile page component
import { Component } from "react";
import UserService from "../services/user.service";
import AuthService from "../services/auth.service";
import EventBus from "../common/EventBus";
import { withRouter } from "../common/with-router";

class PlayerProfilePage extends Component {
    constructor(props) {
        super(props);
        this.state = {
            user_id: "",
            username: "",
            nickname: "",
            email: "",
            date_joined: "",
        };
    }

    componentDidMount() {
        const user = AuthService.getCurrentUser();
        if (!user) {
            // let it render first and only then redirect
            return setTimeout(() => this.props.router.navigate("/login", { replace: true }), 5);
        }

        UserService.getPublicDetails(user.user_id).then(
            response => {
                const { name, nickname, email, date_joined } = response;
                this.setState({ username: name, nickname, email, date_joined});
            },
            error => {
                console.log("unable to fetch user profile");
                console.log(
                    (error.response &&
                     error.response.data &&
                     error.response.data.error &&
                     error.response.data.error.message) ||
                    error.message ||
                    error.toString()
                );
                if (error.response && error.response.status === 401) {
                    EventBus.dispatch("logout");
                }
            }
        )
    }

    render() {
        const { username, email, nickname, date_joined } = this.state;
        return (
            <div>
                <h1>Players page</h1>
                <p><b>Username: </b>{ username }</p>
                <p><b>Nickname: </b>{ nickname }</p>
                <p><b>Email: </b>{ email }</p>
                <p><b>Joined: </b>{ date_joined }</p>
            </div>
        )
    }
}

export default withRouter(PlayerProfilePage);