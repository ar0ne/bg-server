// Sing Up component
import { Component } from "react";
import AuthService from "../../services/auth.service";

import Form from "react-validation/build/form";
import Input from "react-validation/build/input";
import CheckButton from "react-validation/build/button";
import required from "./utils";

import { withRouter } from "../../common/with-router";


class SignUp extends Component {

    constructor(props) {
        super(props);
        this.handleSignUp = this.handleSignUp.bind(this);
        this.onChangeUsername = this.onChangeUsername.bind(this);
        this.onChangeEmail = this.onChangeEmail.bind(this);
        this.onChangePassword = this.onChangePassword.bind(this);
        this.state = {
            username: "",
            email: "",
            password: "",
            message: "",
            isLoading: false,
        }
    }

    handleSignUp(e) {
        e.preventDefault();
        this.setState({
            message: "",
            isLoading: true
        })

        this.form.validateAll();

        if (this.checkBtn.context._errors.length === 0) {
            AuthService.signUp(
                this.state.username, this.state.email, this.state.password
            ).then(() => {
                this.props.router.navigate("/login");
                window.location.reload();
            },
            error => {
               const resMessage =
                   (error.response &&
                   error.response.data &&
                   error.response.data.error &&
                   error.response.data.error.message) ||
                   error.message ||
                   error.toString();

                   this.setState({
                       loading: false,
                       message: resMessage
                   });
            })
        } else {
            this.setState({
                loading: false
            });
        }

    }

    onChangeUsername(e) {
        this.setState({
            username: e.target.value
        })
    }

    onChangeEmail(e) {
        this.setState({
            email: e.target.value
        })
    }

    onChangePassword(e) {
        this.setState({
            password: e.target.value
        })
    }


    render() {
        return (
            <div>
                <p>Sign Up</p>
                <Form
                    onSubmit={this.handleSignUp}
                    ref={c => {
                        this.form = c;
                    }}
                >
                    <div>
                        <label htmlFor="username">Username</label>
                        <Input
                            type="text"
                            name="username"
                            value={this.state.username}
                            onChange={this.onChangeUsername}
                            validations={[required]}
                        />
                    </div>
                    <div>
                        <label htmlFor="email">Email</label>
                        <Input
                            type="email"
                            name="email"
                            value={this.state.email}
                            onChange={this.onChangeEmail}
                            validations={[required]}
                        />
                    </div>
                    <div>
                        <label htmlFor="password">Password</label>
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
                            <span>Send</span>
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

export default withRouter(SignUp);