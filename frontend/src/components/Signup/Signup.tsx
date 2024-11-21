import React, { useState } from "react";
import {Link, useNavigate} from "react-router-dom";
import "./Signup.css";

interface SignupProps {
  setIsAuthenticated: (value: boolean) => void;
}

const Signup: React.FC<SignupProps> = ({ setIsAuthenticated }) => {
  const [username, setUsername] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [message, setMessage] = useState<string>("");
  const navigate = useNavigate();

  const handleSignup = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const response = await fetch("http://localhost:5000/prajitura/signup", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, email, password }),
    });

    const data = await response.json();

    if (response.ok) {
      localStorage.setItem("isAuthenticated", "true");
      setIsAuthenticated(true);
      navigate("/prajitura/index");
    } else {
      setMessage(data.message);
    }
  };

  return (
    <div className="signup-container">
      <div className="header">
        <h2>Sign Up</h2>
      </div>

      <form onSubmit={handleSignup}>
        <div>
          <label>Username:</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Email:</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Password:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">Sign Up</button>
      </form>
      {message && <p className="error">{message}</p>}
      <p>
        Already a member? <Link to="/prajitura/login">Login</Link>
      </p>
    </div>
  );
};

export default Signup;
