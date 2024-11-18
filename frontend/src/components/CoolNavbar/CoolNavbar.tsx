//import React from "react";
import "./CoolNavbar.css";
import { Navbar, Container, Nav, NavDropdown } from "react-bootstrap";

const CoolNavbar = () => {
  return (
    <Navbar id="cool-navbar">
      <Container>
        <Navbar.Brand href="/home">
          <img
            alt="Web Crawler logo"
            src="/Web Crawler.jpg"
            width={60}
            height={40}
            className="d-inline-block align-top logo-navbar"
          />
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link href="/home">Home</Nav.Link>
            <Nav.Link href="/link">Link</Nav.Link>
            <NavDropdown title="Dropdown" id="basic-nav-dropdown">
              <NavDropdown.Item href="/action/3.1">Action</NavDropdown.Item>
              <NavDropdown.Item href="/action/3.2">
                Another action
              </NavDropdown.Item>
              <NavDropdown.Item href="/action/3.3">Something</NavDropdown.Item>
              <NavDropdown.Divider />
              <NavDropdown.Item href="/action/3.4">
                Separated link
              </NavDropdown.Item>
            </NavDropdown>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default CoolNavbar;
