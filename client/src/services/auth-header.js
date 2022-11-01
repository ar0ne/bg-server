const TOKEN_KEY = "user"

export default function authHeader() {
  const user = JSON.parse(localStorage.getItem(TOKEN_KEY));

  if (user && user.token) {
     return { Authorization: user.token };
  } else {
    return {};
  }
}