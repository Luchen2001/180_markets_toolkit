import React, { useState, useEffect } from 'react';
import { Form, Button, Alert, Container, Table, InputGroup, Toast, Spinner } from 'react-bootstrap';

export default function Cashflow() {
  const serverURL = 'http://localhost:8000';
  const [cap, setCap] = useState(200);
  const [cashflowStatus, setCashflowStatus] = useState('');
  const [isDownloadAvailable, setIsDownloadAvailable] = useState(false);
  const [cashflowData, setCashflowData] = useState([]);
  const [cashflowInput, setCashflowInput] = useState({
    document_date: '',
    url: '',
    header: '',
    cash_flow: '',
    debt:'',
    dollar_sign: '',
  });
  const [updateMessage, setUpdateMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [showSection, setShowSection] = useState(false);

  const handleGenerateCashflow = async () => {
    const adjustedCap = cap * 1000000;

    if (cap < 1 || cap > 300) {
      alert('Please enter valid values for Market Cap and Liquidity Calculation Days.');
      return;
    }

    try {
      let response = await fetch(`${serverURL}/cashflow/${adjustedCap}/`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      } else {
        console.log('Cashflow calculation initiated.');
      }
    } catch (error) {
      console.error('There was a problem with the fetch operation: ', error);
    }
  };

  const handleDownloadTemplate = () => {
    window.location.href = `${serverURL}/download/cashflow`;
  };

  const fetchCashflowStatus = async () => {
    try {
      let response = await fetch(`${serverURL}/cashflow/status`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      } else {
        const data = await response.json();
        setCashflowStatus(data.msg);
        if (data.msg === 'cashflow template and database is ready') {
          setIsDownloadAvailable(true);
        } else {
          setIsDownloadAvailable(false);
        }
      }
    } catch (error) {
      console.error('There was a problem with the fetch operation: ', error);
    }
  };

  const fetchCashflowData = async () => {
    try {
      setLoading(true);
      let response = await fetch(`${serverURL}/database/stocks/cashflow`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      } else {
        const data = await response.json();
        const cashflowValues = Object.values(data);
        const checkCashflows = cashflowValues.filter((cashflow) => cashflow.cash_flow === 'check');
        const notCheckCashflows = cashflowValues.filter((cashflow) => cashflow.cash_flow !== 'check');
        checkCashflows.sort((a, b) => a.cap - b.cap);
        notCheckCashflows.sort((a, b) => a.cap - b.cap);
        const mergedCashflows = [...checkCashflows, ...notCheckCashflows];
        // store the data to localStorage
        localStorage.setItem('cashflowData', JSON.stringify(mergedCashflows));
        setCashflowData(mergedCashflows);
        setLoading(false);
      }
    } catch (error) {
      console.error('There was a problem with the fetch operation: ', error);
      setLoading(false);
    }
  };
  

  const handleUpdateCashflow = async () => {
    try {
      const response = await fetch(`${serverURL}/database/stocks/update_cashflow/${cashflowInput.code}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(cashflowInput),
      });
  
      if (response.ok) {
        const data = await response.json();
        setUpdateMessage(`Cashflow of ${cashflowInput.code} has been updated.`);
        // clear the form after successful submission
        setCashflowInput({
          document_date: '',
          url: '',
          header: '',
          cash_flow: '',
          debt: '',
          dollar_sign: '',
        });
      } else {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      console.error('There was a problem with the fetch operation: ', error);
    }
  };
  

  useEffect(() => {
    //const cachedData = false
    const cachedData = localStorage.getItem('cashflowData');
    if (cachedData) {
      setCashflowData(JSON.parse(cachedData));
      setLoading(false);
    } else {
      fetchCashflowData();
    }
  
    const interval = setInterval(() => {
      fetchCashflowStatus();
    }, 500);
  
    return () => clearInterval(interval);
  }, []);
  

  const handleToggleSection = () => {
    setShowSection(!showSection);
  };

  return (
    <Container style={{ display: 'flex', paddingTop: '1vh' }}>
      <Button
        onClick={fetchCashflowData}
        variant="outline-success"
        size="sm"
        style={{
          position: 'fixed', top: '1vh', right: '1vh', margin: '10px'
        }}>
        Refresh
      </Button>
      <div className="container mt-1">
        <Button
          variant="outline-secondary"
          style={{ marginTop: '20px' }}
          onClick={handleToggleSection}
        >
          {showSection ? 'Hide Section' : 'Show Section'}
        </Button>
        {showSection && (<Form>
          <Form.Group className="mb-3" controlId="formMarketCap">
            <Form.Label>Market Cap (millions):</Form.Label>
            <Form.Control
              style={{ width: '500px' }}
              type="number"
              min="1"
              max="100"
              value={cap}
              onChange={(e) => setCap(e.target.value)}
            />
          </Form.Group>

          <Button variant="primary" onClick={handleGenerateCashflow}>
            Update Cashflow
          </Button>

          <Alert variant="info" style={{ marginTop: '20px', maxWidth: '500px' }}>
            {cashflowStatus}
          </Alert>

          {isDownloadAvailable && (
            <Button variant="primary" style={{ marginTop: '20px' }} onClick={handleDownloadTemplate}>
              Download Template
            </Button>
          )}
        </Form>
        )}





        <Form style={{ marginTop: '20px', display: 'flex', flexWrap: 'wrap' }}>
          <InputGroup>
            <Form.Control
              style={{ width: '100px', marginRight: '10px' }}
              type="text"
              placeholder="Code"
              value={cashflowInput.code}
              onChange={(e) => setCashflowInput({ ...cashflowInput, code: e.target.value })}
            />
            <Form.Control
              style={{ width: '100px', marginRight: '10px' }}
              type="date"
              placeholder="Date"
              value={cashflowInput.document_date}
              onChange={(e) => setCashflowInput({ ...cashflowInput, document_date: e.target.value })}
            />
            <Form.Control
              style={{ width: '100px', marginRight: '10px' }}
              type="text"
              placeholder="URL"
              value={cashflowInput.url}
              onChange={(e) => setCashflowInput({ ...cashflowInput, url: e.target.value })}
            />
            <Form.Control
              style={{ width: '200px', marginRight: '10px' }}
              type="text"
              placeholder="Header"
              value={cashflowInput.header}
              onChange={(e) => setCashflowInput({ ...cashflowInput, header: e.target.value })}
            />
            <Form.Control
              style={{ width: '200px', marginRight: '10px' }}
              type="text"
              placeholder="Cash Flow"
              value={cashflowInput.cash_flow}
              onChange={(e) => setCashflowInput({ ...cashflowInput, cash_flow: e.target.value })}
            />
            <Form.Control
              style={{ width: '200px', marginRight: '10px' }}
              type="text"
              placeholder="Debt"
              value={cashflowInput.debt}
              onChange={(e) => setCashflowInput({ ...cashflowInput, debt: e.target.value })}
            />
            <Form.Control
              style={{ width: '80px', marginRight: '10px' }}
              type="text"
              placeholder="$ Sign"
              value={cashflowInput.dollar_sign}
              onChange={(e) => setCashflowInput({ ...cashflowInput, dollar_sign: e.target.value })}
            />
            <Button variant="primary" onClick={handleUpdateCashflow}>
              Update Cashflow
            </Button>
          </InputGroup>
        </Form>


        {loading ? (
          <div className="text-center" style={{ paddingTop: '10vh' }}>
            <Spinner animation="border" variant="primary" />
            <p>Loading...</p>
          </div>
        ) : (
          <div style={{ overflow: 'auto', height: '600px' }}>
            <Table striped bordered hover style={{ marginTop: '20px' }}>
              <thead>
                <tr>
                  <th>Stock Code</th>
                  <th>Name</th>
                  <th>Cap</th>
                  <th>Document Date</th>
                  <th>URL</th>
                  <th>Header</th>
                  <th>Cash Flow</th>
                  <th>Debt</th>
                  <th>Dollar Sign</th>
                </tr>
              </thead>
              <tbody>
                {cashflowData.map((cashflow) => (
                  <tr key={cashflow.stock_code}>
                    <td>{cashflow.stock_code}</td>
                    <td>{cashflow.name}</td>
                    <td>{(cashflow.cap / 1000000).toFixed(2)}M</td>
                    <td>{cashflow.document_date}</td>
                    <td>
                      <Button variant="primary" onClick={() => window.open(cashflow.url, '_blank')}>
                        View
                      </Button>
                    </td>
                    <td>{cashflow.header}</td>
                    <td>{cashflow.cash_flow}</td>
                    <td>{cashflow.debt}</td>
                    <td>{cashflow.dollar_sign}</td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </div>
        )}


        <Toast
          show={updateMessage !== ''}
          onClose={() => setUpdateMessage('')}
          style={{
            position: 'fixed',
            top: '80px',
            right: '20px',
          }}
          delay={3000}
          autohide
        >
          <Toast.Body>{updateMessage}</Toast.Body>
        </Toast>
      </div>
    </Container>
  );
}
