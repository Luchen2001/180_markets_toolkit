import React, { useState, useEffect } from "react";
import { Button, Form, Spinner, Alert, InputGroup, FormControl, Container, Row, Col, ToggleButton } from "react-bootstrap";
import { serverURL } from './config';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';


export default function Placement() {
    const [selectedFile, setSelectedFile] = useState();
    const [status, setStatus] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [fileType, setFileType] = useState("csv");
    const [showHelp, setShowHelp] = useState(false);

    const [code, setCode] = useState('');
    const [price, setPrice] = useState('');
    const [strike, setStrike] = useState('');
    const [ttm, setTtm] = useState('');
    const [ratio, setRatio] = useState('');
    const [date, setDate] = useState('');
    const [discount, setDiscount] = useState('');
    const [amt, setAmt] = useState('');
    const [hasOption, setHasOption] = useState("Yes");

    const [dataList, setDataList] = useState({});
    const [selectedCode, setSelectedCode] = useState('');
    const [selectedDate, setSelectedDate] = useState(null);

    const [deals, setDeals] = useState({});

    const handleAddDiagram = async () => {
        try {
            let response = await fetch(`${serverURL}/placement/${selectedCode}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            } else {
                const data = await response.json();
                console.log(code)
                setDataList({
                    ...dataList,
                    [selectedCode]: data
                });
                let keys = Object.keys(data);
                setSelectedDate(keys[0])

            }

        } catch (error) {
            console.error('There was a problem with the fetch operation: ', error);
        }
    }

    useEffect(() => {
        if (selectedDate !== null) {
            console.log(selectedDate)
            console.log(dataList)
            console.log(dataList[selectedCode][selectedDate]['record'])
        }

    }, [selectedDate])

    useEffect(() => {
        const fetchData = async () => {
            try {
                let response = await fetch(`${serverURL}/placement_deals`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                } else {
                    let data = await response.json();
                    setDeals(data);
                }
            } catch (error) {
                console.error('There was an error!', error);
            }
        };
        fetchData();
    }, []);

    const handleUploadPlacement = async () => {
        try {
            let postData = {
                code: code,
                price: price,
                date: date,
                discount: discount,
                amt: amt,
                option: hasOption ? {
                    strike: strike,
                    ttm: ttm,
                    ratio: ratio
                } : null
            };
            const response = await fetch(`${serverURL}/update_placement`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(postData),
            });

            if (response.ok) {
                const data = await response.json();
                //setUpdateMessage(`Cashflow of ${cashflowInput.code} has been updated.`);
                // clear the form after successful submission

            } else {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
        } catch (error) {
            console.error('There was a problem with the fetch operation: ', error);
        }
    };

    /*
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

    function Legacy(){
        return (
            <>

                <Col>
                    <div class="container mt-5">
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
            </>
        )
    }
    */





    const MyChart = ({ imgData }) => {


        const data = imgData.map(item => ({
            date: item.close_date,
            return: item.return,
            actualReturn: item.actual_return
        }));

        return (
            <LineChart
                width={1300}
                height={300}
                data={data}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="actualReturn" stroke="#82ca9d" />
                <Line type="monotone" dataKey="return" stroke="#8884d8" activeDot={{ r: 8 }} />
            </LineChart>
        );
    };







    return (
        <Container style={{ display: "flex", height: "100vh", paddingTop: "2vh" }}>
            <Row style={{ flex: 1 }}>
                <Col>
                    <h2>Black Scholes Modle</h2>
                    <Form style={{ marginTop: '20px', display: 'flex', flexWrap: 'wrap' }}>
                        <InputGroup>
                            <Form.Control
                                style={{ width: '40px', marginRight: '5px' }}
                                type="text"
                                placeholder="Code"
                                value={code}
                                onChange={(e) => setCode(e.target.value)}
                            />
                            <Form.Control
                                style={{ width: '100px', marginRight: '5px' }}
                                type="text"
                                placeholder="Cap Raise Price"
                                value={price}
                                onChange={(e) => setPrice(e.target.value)}
                            />
                            <Form.Control
                                style={{ width: '100px', marginRight: '5px' }}
                                type="date"
                                placeholder="Date"
                                value={date}
                                onChange={(e) => setDate(e.target.value)}
                            />
                            <Form.Control
                                style={{ width: '100px', marginRight: '5px' }}
                                type="text"
                                placeholder="Discount"
                                value={discount}
                                onChange={(e) => setDiscount(e.target.value)}
                            />
                            <Form.Control
                                style={{ width: '100px', marginRight: '5px' }}
                                type="text"
                                placeholder="Raised Amount"
                                value={amt}
                                onChange={(e) => setAmt(e.target.value)}
                            />
                            <Form.Control
                                as="select"
                                style={{ width: '30px', marginRight: '5px' }}
                                value={hasOption}
                                onChange={(e) => setHasOption(e.target.value)}
                            >
                                <option value="Yes">Yes</option>
                                <option value="No">No</option>
                            </Form.Control>
                            {
                                hasOption == "Yes" ?
                                    <>
                                        <Form.Control
                                            style={{ width: '100px', marginRight: '5px' }}
                                            type="text"
                                            placeholder="Strike Price"
                                            value={strike}
                                            onChange={(e) => setStrike(e.target.value)}
                                        />
                                        <Form.Control
                                            style={{ width: '100px', marginRight: '5px' }}
                                            type="text"
                                            placeholder="Maturity (Yrs)"
                                            value={ttm}
                                            onChange={(e) => setTtm(e.target.value)}
                                        />
                                        <Form.Control
                                            style={{ width: '100px', marginRight: '5px' }}
                                            type="text"
                                            placeholder="Ratio"
                                            value={ratio}
                                            onChange={(e) => setRatio(e.target.value)}
                                        />
                                    </> :
                                    null
                            }
                            <Button variant="primary" onClick={handleUploadPlacement}>
                                Generate Return
                            </Button>
                        </InputGroup>
                    </Form>
                    <Form style={{ width: '200px', margin: '5px' }}>
                        <InputGroup>
                            <Form.Control
                                style={{ width: '40px', marginRight: '5px' }}
                                type="text"
                                placeholder="Code"
                                value={selectedCode}
                                onChange={(e) => setSelectedCode(e.target.value)}
                            />
                            <Button variant="primary" onClick={handleAddDiagram}>
                                Add
                            </Button>
                        </InputGroup>
                    </Form>
                    {selectedDate !== null && selectedCode.length == 3 ?
                        <div >
                            <div style={{ display: "flex", flexDirection: "row" }}>
                                <p style={{ marginRight: "20px" }}>Offered Price: {dataList[selectedCode][selectedDate]["raised_price"]}</p>
                                <p style={{ marginRight: "20px" }}>Discount: {dataList[selectedCode][selectedDate]["discount"]}</p>
                                <p style={{ marginRight: "20px" }}>Raise Amount: {dataList[selectedCode][selectedDate]["raised_amount"]}</p>
                                <p style={{ marginRight: "20px" }}>Strike Price: {dataList[selectedCode][selectedDate]["option"]['strike']}</p>
                                <p style={{ marginRight: "20px" }}>TimeToMaturity: {dataList[selectedCode][selectedDate]["option"]['ttm']}</p>
                                <p style={{ marginRight: "20px" }}> Ratio: {dataList[selectedCode][selectedDate]["option"]['ratio']}</p>
                            </div>

                            <MyChart imgData={[...dataList[selectedCode][selectedDate]["record"]].reverse()} />
                        </div>
                        : null}
                    <div>
                        {Object.entries(deals).map(([date, codes]) => (
                            <div key={date}>
                                <h4>{date}</h4>
                                {Object.entries(codes).map(([code, days]) => (
                                    <div key={code}>
                                        <h5>{code}</h5>
                                        {Object.entries(days).map(([day, details]) => (
                                            <p key={day}>
                                                {day}: {details ? details.actual_return : "N/A"}
                                            </p>
                                        ))}
                                    </div>
                                ))}
                            </div>
                        ))}
                    </div>
                </Col>
            </Row>
        </Container>

    );
}
