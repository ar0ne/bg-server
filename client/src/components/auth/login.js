// Log In component
import { Component } from "react";
import AuthService from "../../services/auth.service";

import Form from "react-validation/build/form";
import Input from "react-validation/build/input";
import CheckButton from "react-validation/build/button";

import { withRouter } from "../common/with-router";

const required = value => {
    if (!value) {
        return (
            <div>
                This field is required!
            </div>
        )
    }
}

class Login extends Component {

    constructor(props) {
        super(props);
        this.handleLogin = this.handleLogin.bind(this);
        this.onChangeUsername = this.onChangeUsername.bind(this);
        this.onChangePassword = this.onChangePassword.bind(this);

        this.state = {
            username: "",
            password: "",
            message: "",
            isLoading: false,
        }
    }

    onChangeUsername(e) {
        this.setState({
            username: e.target.value
        })
    }

    onChangePassword(e) {
        this.setState({
            password: e.target.value
        })
    }

    handleLogin(e) {
        e.preventDefault();
        this.setState({
            message: "",
            isLoading: true,
        })

        this.form.validateAll();

        if (this.checkBtn.context._errors.length === 0) {
            AuthService.login(this.state.username, this.state.password).then(
                () => {
                    this.props.router.navigate("/profile");
                    window.location.reload();
                },
                error => {
                    const resMessage =
                        (error.response &&
                         error.response.data &&
                         error.response.data.message) ||
                         error.message ||
                         error.toString();

                    this.setState({
                        loading: false,
                        message: resMessage
                    });
                }
            );
        } else {
            this.setState({
                loading: false
            });
        }
    }

    render() {
        return (
            <div>
                <Form
                    onSubmit={this.handleLogin}
                    ref={c => {
                        this.form = c;
                    }}
                >
                    <div>
                        <Input
                            type="text"
                            name="username"
                            value={this.state.username}
                            onChange={this.onChangeUsername}
                            validations={[required]}
                        />
                    </div>
                    <div>
                        <Input
                            type="password"
                            name="password"
                            value={this.state.password}
                            onChange={this.onChangePassword}
                            validations={[required]}
                        />
                    </div>
                    <div>
                        <button
                            disabled={this.state.loading}
                        >
                            <span>Login</span>
                        </button>
                    </div>

                    {this.state.message && (
                        <div className="form-group">
                            <div className="alert alert-danger" role="alert">
                              {this.state.message}
                            </div>
                        </div>
                    )}
                    <CheckButton
                        style={{ display: "none" }}
                        ref={c => {
                            this.checkBtn = c;
                        }}
                    />
                </Form>
            </div>
        )
    }
}

export default withRouter(Login);