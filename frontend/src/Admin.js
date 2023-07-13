import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Button, Form, Spinner, Alert, InputGroup, FormControl, Container, Row, Col, ToggleButton } from "react-bootstrap";

const BASE_URL = "http://localhost:8000";

const Admin = () => {
  const [databaseStatus, setDatabaseStatus] = useState("");
  const [selectedFile, setSelectedFile] = useState();
  const [isLoading, setIsLoading] = useState(false);

  const fetchDatabaseStatus = async () => {
    try {
      let response = await fetch(`${BASE_URL}/database/status`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      } else {
        const data = await response.json();
        setDatabaseStatus(data.msg);
      }
    } catch (error) {
      console.error('There was a problem with the fetch operation: ', error);
    }
  }

  useEffect(() => {
    const interval = setInterval(() => {
      fetchDatabaseStatus();
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleFileUpload = async (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    setIsLoading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    await fetch(`${BASE_URL}/upload_hubspot`, {
      method: 'POST',
      body: formData,
    });
    setIsLoading(false);
  };


  const updateGeneralInfo = () => {
    axios.get(`${BASE_URL}/update_database/general_info`)
      .then(() => {
        window.alert('General info updated');
      })
      .catch(error => {
        window.alert('Error updating general info: ' + error);
      });
  };

  const updateMarketInfo = () => {
    axios.get(`${BASE_URL}/update_database/market_info`)
      .then(() => {
        window.alert('Market info updated');
      })
      .catch(error => {
        window.alert('Error updating market info: ' + error);
      });
  };

  const updateLiquidityCOS = () => {
    axios.get(`${BASE_URL}/update_database/liquidity_cos`)
      .then(() => {
        window.alert('Liquidity Course Of Sales updated');
      })
      .catch(error => {
        window.alert('Error updating Liquidity Course Of Sales: ' + error);
      });
  };

  const updateMiningComp = () => {
    axios.get(`${BASE_URL}/update_database/mining_comp`)
      .then(() => {
        window.alert('Mining companies list updated');
      })
      .catch(error => {
        window.alert('Error updating Mining companies list: ' + error);
      });
  };

  const newDayUpdate = () => {
    axios.get(`${BASE_URL}/update_database/new_day_update`)
      .then(() => {
        window.alert('Start to update all data in the datebase');
      })
      .catch(error => {
        window.alert('Error updating Mining companies list: ' + error);
      });
  };

  const realtimeLiquidityUpdate = () => {
    axios.get(`${BASE_URL}/update_database/realtime_liquidity_update`)
      .then(() => {
        window.alert('Start to update real-time liquidity scores');
      })
      .catch(error => {
        window.alert('Error updating Mining companies list: ' + error);
      });
  };

  const rebootDatabase = () => {
    const confirmed = window.confirm('Are you sure you want to reboot the database? This action cannot be undone.');

    if (confirmed) {
      axios.get(`${BASE_URL}/reboot_database`)
        .then(() => {
          window.alert('Database rebooted');
        })
        .catch(error => {
          window.alert('Error rebooting database: ' + error);
        });
    }
  };

  return (
    <div className="container mt-5">
      <div className="row mt-4">
        <div className="col">
          <Alert variant="info" style={{ maxWidth: "500px", marginTop: "20px" }}>
            Database Status: {databaseStatus}
          </Alert>

        </div>
      </div>
      <div className="row mt-4">
        <div className="col">
          <button className="btn btn-success" onClick={newDayUpdate}>
            New Day Update
          </button>
        </div>
        <div className="col">
          <button className="btn btn-success" onClick={realtimeLiquidityUpdate}>
            Real Time Liquidity Update
          </button>
        </div>
      </div>
      <div className="row mt-4">
        <div className="col">
          <button className="btn btn-primary" onClick={updateGeneralInfo}>
            Update General Info (Volume)
          </button>
        </div>
        <div className="col">
          <button className="btn btn-primary" onClick={updateMarketInfo}>
            Update Market Info (Price)
          </button>
        </div>
        <div className="col">
          <button className="btn btn-primary" onClick={updateLiquidityCOS}>
            Update Liquidity
          </button>
        </div>
        <div className="col">
          <button className="btn btn-primary" onClick={updateMiningComp}>
            Update Mining Company List
          </button>
        </div>
      </div>
      <div className="row mt-4">
        <div className="col">
          <button
            className="btn btn-danger"
            onClick={rebootDatabase}
          >
            Reboot Database
          </button>
        </div>
      </div>

      <div className="container mt-5">
        <h3>Hubspot Management</h3>
        <Form>
        <Form.Group>
          <Form.Label>Upload File</Form.Label>
          <InputGroup className="mb-3">
            <FormControl
              type="file"
              onChange={handleFileUpload}
              style={{ maxWidth: "500px" }}
            />
          </InputGroup>
          <Button variant="primary" onClick={handleUpload} disabled={!selectedFile || isLoading} className="mr-2">
            {isLoading ? <Spinner animation="border" size="sm" /> : "Upload"}
          </Button>
        </Form.Group>
      </Form>
      </div>
      
    </div>
  );
};

export default Admin;
