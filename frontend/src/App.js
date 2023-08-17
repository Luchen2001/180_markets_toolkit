import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { Navbar, Nav } from 'react-bootstrap';

import Home from './Home';
import Cashflow from './Cashflow';
import Placement from './Placement';
import Liquidity from './Liquidity';
import Admin from './Admin';
import logo from './180logo.png'
import './App.css'; // Import the CSS file
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  return (
    <Router>
      <div>
        <Navbar bg="light" expand="lg" style={{ display: "flex",  paddingLeft:"2vw"}}>
          <Navbar.Brand as={NavLink} to="/" style={{fontSize: "4vh"}}>
            <img src={logo} alt="180 Logo" style={{ width: "4vh", height: "4vh", margin: "1vh"}} />
            180 Markets Toolkit
          </Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="ml-auto" style={{fontSize: "3vh"}}> {/* Use ml-auto class to center the links */}
              <Nav.Link as={NavLink} to="/" className="nav-link" >Home</Nav.Link>
              <Nav.Link as={NavLink} to="/admin" className="nav-link" >Admin</Nav.Link>
              <Nav.Link as={NavLink} to="/placement" className="nav-link">Placement</Nav.Link>
              <Nav.Link as={NavLink} to="/cashflow" className="nav-link" >Cashflow</Nav.Link>
              <Nav.Link as={NavLink} to="/stocks" className="nav-link">Stocks</Nav.Link>
            </Nav>
          </Navbar.Collapse>
        </Navbar>

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/admin" element={<Admin />} />
          <Route path="/placement" element={<Placement />} />
          <Route path="/cashflow" element={<Cashflow />} />
          <Route path="/stocks" element={<Liquidity />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
