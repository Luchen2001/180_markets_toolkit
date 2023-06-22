import React, { useEffect, useState } from 'react';
import axios from 'axios';

const BASE_URL = "http://localhost:8000";

const Admin = () => {
  const [databaseStatus, setDatabaseStatus] = useState("");

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
      <h1>Admin</h1>
      <div className="row mt-4">
        <div className="col">
          <p>Database Status: {databaseStatus}</p>
        </div>
      </div>
      <div className="row mt-4">
        <div className="col">
          <button className="btn btn-primary" onClick={updateGeneralInfo}>
            Update General Info
          </button>
        </div>
        <div className="col">
          <button className="btn btn-primary" onClick={updateMarketInfo}>
            Update Market Info
          </button>
        </div>
        <div className="col">
          <button className="btn btn-primary" onClick={updateLiquidityCOS}>
            Update Liquidity Course of Sales
          </button>
        </div>
        <div className="col">
          <button
            className="btn btn-danger"
            onClick={rebootDatabase}
          >
            Reboot Database
          </button>
        </div>
      </div>
    </div>
  );
};

export default Admin;
