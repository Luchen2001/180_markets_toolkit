import React, { useState, useEffect } from 'react';
import { Form, Button, Alert, Container } from 'react-bootstrap';

export default function Cashflow() {
    const serverURL = 'http://localhost:8000';
    const [cap, setCap] = useState(6);
    const [day, setDay] = useState(20);
    const [cashflowStatus, setCashflowStatus] = useState('');
    const [isDownloadAvailable, setIsDownloadAvailable] = useState(false);

    const handleGenerateCashflow = async () => {
        const adjustedCap = cap * 1000000;

        if (day < 1 || day > 200 || cap < 1 || cap > 100) {
            alert('Please enter valid values for Market Cap and Liquidity Calculation Days.');
            return;
        }

        try {
            let response = await fetch(`${serverURL}/cashflow/${adjustedCap}/${day}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            } else {
                console.log('Cashflow calculation initiated.');
            }
        } catch (error) {
            console.error('There was a problem with the fetch operation: ', error);
        }
    }

    const handleDownloadTemplate = () => {
        window.location.href = `${serverURL}/download/cashflow`;
    }

    const fetchCashflowStatus = async () => {
        try {
            let response = await fetch(`${serverURL}/cashflow/status`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            } else {
                const data = await response.json();
                setCashflowStatus(data.msg);
                if (data.msg === 'cashflow template is ready') {
                    setIsDownloadAvailable(true);
                } else {
                    setIsDownloadAvailable(false)
                }
            }
        } catch (error) {
            console.error('There was a problem with the fetch operation: ', error);
        }
    }

    useEffect(() => {
        const interval = setInterval(() => {
            fetchCashflowStatus();
        }, 500);
        return () => clearInterval(interval);
    }, []);

    return (
        <Container style={{ display: "flex", height: "100vh", paddingTop:"2vh"}}>
            <div  class="container mt-5">
            <Form>
                <Form.Group className="mb-3" controlId="formMarketCap">
                    <Form.Label>Market Cap (millions):</Form.Label>
                    <Form.Control style={{ width: "500px" }} type="number" min="1" max="100" value={cap} onChange={(e) => setCap(e.target.value)} />
                </Form.Group>

                <Form.Group className="mb-3" controlId="formLiquidityCalculationDays">
                    <Form.Label>Liquidity Calculation Days:</Form.Label>
                    <Form.Control style={{ width: "500px" }} type="number" min="1" max="200" value={day} onChange={(e) => setDay(e.target.value)} />
                </Form.Group>

                <Button variant="primary" onClick={handleGenerateCashflow}>
                    Generate Cashflow
                </Button>

                <Alert variant='info' style={{ marginTop: "20px", maxWidth: "500px"}}>
                    {cashflowStatus}
                </Alert>

                {isDownloadAvailable && 
                    <Button variant="primary" style={{ marginTop: "20px" }} onClick={handleDownloadTemplate}>
                        Download Template
                    </Button>
                }
            </Form>
            </div>
        </Container>
    )
}
