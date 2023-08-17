import React, { useState, useEffect } from "react";
import { Button, Form, Spinner, Alert, InputGroup, FormControl, Container, Row, Col, ToggleButton } from "react-bootstrap";
import { serverURL } from './config';



export default function Placement() {
    const [baseDay, setBaseDay] = useState([])
    const [baseDays, setBaseDays] = useState([30])
    const [selectedFile, setSelectedFile] = useState();
    const [isLoading, setIsLoading] = useState(false);
    const [status, setStatus] = useState("");
    const [finished, setFinised] = useState(true);

    const handleFileUpload = async (e) => {
        setFinised(false)
        setSelectedFile(e.target.files[0]);
    };

    const handleDownload = () => {
        window.location.href = `${serverURL}/placement/download/deals`;
        setFinised(true)
    };

    const handleDeleteDay = (index) => {
        setBaseDays(baseDays.filter((_, i) => i !== index));
    };

    const handleUpload = async () => {
        setIsLoading(true);
        const formData = new FormData();
        formData.append('file', selectedFile);
        await fetch(`${serverURL}/upload_placement`, {
            method: 'POST',
            body: formData,
        });

        await fetch(`${serverURL}/placement/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ day_list: baseDays })
        });
        setIsLoading(false);
    };

    const fetchStatus = async () => {
        try {
          let response = await fetch(`${serverURL}/placement/status`);
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          } else {
            const data = await response.json();
            setStatus(data.msg);
          }
        } catch (error) {
          console.error('There was a problem with the fetch operation: ', error);
        }
      }
    
      useEffect(() => {
        if (!finished) { // Only set up the interval if not finished
          const interval = setInterval(() => {
            fetchStatus();
          }, 500);
      
          return () => clearInterval(interval); // Clear the interval when the component unmounts or when finished becomes true
        }
      }, [finished]);

    return (
        <Container style={{ display: "flex", height: "10vh", paddingTop: "2vh" }}>
            <Row style={{ flex: 1 }}>

                <Form >
                    <Form.Group style={{ marginTop: '20px', marginBottom: '50px', display: 'flex', flexWrap: 'wrap' }}>
                        <Form.Label>Select the days of calculation</Form.Label>
                        <InputGroup>
                            <Form.Control
                                style={{ maxWidth: '200px', marginRight: '5px' }}
                                type="number"
                                placeholder="Days"
                                value={baseDay}
                                onChange={(e) => setBaseDay(e.target.value)}
                            />
                            <Button variant="primary" onClick={() => setBaseDays([...baseDays, parseInt(baseDay)])}>
                                Add Day
                            </Button>
                        </InputGroup>
                    </Form.Group>
                </Form>
                <Row style={{ flex: 1 }}>
                    {baseDays.map((day, index) => {
                        return (
                            <div style={{ marginBottom: '20px', marginLeft: '20px', marginRight: '20px', display: 'flex', alignItems: 'center', border: '1px solid #ccc', padding: '10px', width: "200px", borderRadius: "20px" }}>
                                <div style={{ padding: '10px' }}>
                                    {day} days
                                </div>
                                <Button variant="danger" style={{ borderRadius: "50px", width: "80px", height: "40px" }} onClick={() => handleDeleteDay(index)}>
                                    Delete
                                </Button>
                            </div>
                        )
                    })}
                </Row>
                <Form >
                    <Form.Group style={{ marginTop: '20px', display: 'flex', flexWrap: 'wrap' }}>
                        <Form.Label>Upload File</Form.Label>
                        <InputGroup className="mb-3">
                            <FormControl
                                type="file"
                                onChange={handleFileUpload}
                                style={{ maxWidth: "500px" }}
                            />
                            <Button variant="primary" onClick={handleUpload} disabled={!selectedFile || isLoading} className="mr-2">
                                {isLoading ? <Spinner animation="border" size="sm" /> : "Upload"}
                            </Button>
                        </InputGroup>
                    </Form.Group>
                </Form>
                <div>
                <Alert variant="info" style={{ maxWidth: "500px",}}>
                    Status: {status}
                </Alert>
                <Button variant="primary" onClick={handleDownload} style={{maxWidth:'200px'}}>
                    Download
                </Button>
                </div>
               
                
            </Row>
        </Container>

    );
}
