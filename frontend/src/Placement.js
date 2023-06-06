import React, { useState, useEffect } from "react";
import { Button, Form, Spinner, Alert, InputGroup, FormControl, Container, Row, Col, ToggleButton } from "react-bootstrap";


const serverURL = 'http://localhost:8000';

export default function Placement() {
    const [selectedFile, setSelectedFile] = useState();
    const [status, setStatus] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [fileType, setFileType] = useState("csv");
    const [showHelp, setShowHelp] = useState(false);


    useEffect(() => {
        const interval = setInterval(() => {
            fetch(`${serverURL}/placement/status`)
                .then(response => response.json())
                .then(data => setStatus(data.msg));
        }, 200);
        return () => clearInterval(interval);
    }, []);

    const handleFileUpload = async (e) => {
        setSelectedFile(e.target.files[0]);
    };

    const handleUpload = async () => {
        setIsLoading(true);
        const formData = new FormData();
        formData.append('file', selectedFile);
        await fetch(`${serverURL}/upload_placement`, {
            method: 'POST',
            body: formData,
        });
        await fetch(`${serverURL}/placement/generate`);
        setIsLoading(false);
    };

    const handleDownload = () => {
        window.location.href = `${serverURL}/download/placement/${fileType}`;
    };

    const handleChangeFileType = (e) => {
        setFileType(e.target.value);
    };

    const handleToggleHelp = () => {
        setShowHelp(!showHelp);
    };
    
    const handleDownloadExample = () => {
        window.location.href = `${serverURL}/download/example`;
    };

    return (
        <Container style={{ display: "flex", height: "100vh", paddingTop: "2vh" }}>
            <Row style={{ flex: 1 }}>
            <Col>
                    <div  class="container mt-5">
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
                            

                            <Form.Group className="mt-4">
                                <Form.Label>File Type</Form.Label>
                                <Form.Control as="select" value={fileType} onChange={handleChangeFileType} style={{ maxWidth: "500px" }}>
                                    <option value="csv">CSV</option>
                                    <option value="json">JSON</option>
                                </Form.Control>
                            </Form.Group>

                        </Form>
                        <Button variant="primary" onClick={handleDownload} className="mt-4">
                            Download
                        </Button>
                        <Alert variant="info" style={{ maxWidth: "500px", marginTop: "20px" }}>
                            Status: {status}
                        </Alert>
                    </div>
                    <div style={{ paddingTop: "5px", paddingBottom: "5px" }}>
                <ToggleButton
                    id="toggle-check"
                    type="checkbox"
                    variant="outline-primary"
                    checked={showHelp}
                    value="1"
                    onChange={handleToggleHelp}
                >
                    Help
                </ToggleButton>
            </div>
                </Col>

                {showHelp && (
                    <Col>
                        <div class="container mt-5">
                        
                            <h3>User Guide</h3>
                            <Button variant="info" onClick={handleDownloadExample}>Download Example Input File</Button>
                            <div>
                            <Form.Text className="text-muted">
                                Download the template file for reviewing the format.
                            </Form.Text>

                            </div>
                           
                            <div class="card mt-4">
                                <div class="card-header">
                                    <h4>Case 1 - Creating New Placement Tracking File</h4>
                                </div>
                                <div class="card-body">
                                    <ol>
                                        <li>In an Excel file, enter the header as "Company name", "Placement Date", "Code", "Placement price", "Type". Ensure that the Placement Date is in the format of year-month-date.</li>
                                        <li>Save the Excel file as CSV file type.</li>
                                        <li>Click on 'Choose file' on the right and upload the file.</li>
                                        <li>After backend finishes updating, click on "Download".</li>
                                    </ol>
                                </div>
                            </div>
                            <div class="card mt-4">
                                <div class="card-header">
                                    <h4>Case 2 - Updating the Existing Placement Tracking File</h4>
                                </div>
                                <div class="card-body">
                                    <ol>
                                        <li>Copy the downloaded CSV file into Excel.</li>
                                        <li>Add new placement information below the current created rows.</li>
                                        <li>Save it as CSV file.</li>
                                        <li>Upload it again and download the updated file.</li>
                                    </ol>
                                </div>
                            </div>
                        </div>
                    </Col>
                )}
            </Row>
           
        </Container>

    );
}
