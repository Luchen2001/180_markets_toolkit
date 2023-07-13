import React, { useEffect, useState } from "react";
import { Spinner, Table, Form, Button } from "react-bootstrap";
import { saveAs } from 'file-saver';


export default function Liquidity() {
  const [stocks, setStocks] = useState([]);
  const [rankingCriteria, setRankingCriteria] = useState("score");
  const [loading, setLoading] = useState(true);
  const [columnVisibility, setColumnVisibility] = useState({
    code: true,
    name: true,
    price: true,
    marketCap: true,
    liquidityScore: true,
    EMA_amount: false,
    cashflow: true,
    EV: true,
    debt: true,
    price_today: true,
    volume_today: true,
    volume: true,
    volume_5d: false,
    amount_today: false,
    amount: false,
    amount_5d: false,
    industry: true,
    isMining: false,
    commodities: true,
  });
  const [maxMarketCap, setMaxMarketCap] = useState(200000000);
  const [column, setcolumn] = useState(false);
  const [showMiningOnly, setShowMiningOnly] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  const handleSearchTermChange = (event) => {
    setSearchTerm(event.target.value.toLowerCase()); // Convert to lowercase for case insensitive search
  };

  const handleColumnChange = () => {
    setcolumn(!column)
  }

  const toggleShowMiningOnly = () => {
    setShowMiningOnly(prevState => !prevState);
  }

  useEffect(() => {

    const cachedStocks = localStorage.getItem('stocks');
    //const cachedStocks = false

    if (cachedStocks) {
      setStocks(JSON.parse(cachedStocks));
      setLoading(false);
    } else {
      fetchStocks();
    }
  }, []);

  const fetchStocks = async () => {
    try {
      setLoading(true);
      const response = await fetch("http://localhost:8000/database/stocks");
      const data = await response.json();
      setStocks(data);
      localStorage.setItem('stocks', JSON.stringify(data));  // Store data in localStorage
      setLoading(false);
    } catch (error) {
      console.error("Error fetching stocks:", error);
      setLoading(false);
    }
  };


  const handleRankingCriteriaChange = (event) => {
    setRankingCriteria(event.target.value);
  };

  const handleMaxMarketCapChange = (event) => {
    setMaxMarketCap(Number(event.target.value) * 1000000);
  };

  const filteredStocks = stocks.filter(stock => stock.cap <= maxMarketCap && (!showMiningOnly || (showMiningOnly && stock.isMining)));

  const searchedStocks = filteredStocks.filter(stock =>
    (stock.industry && stock.industry.toLowerCase().includes(searchTerm)) ||
    (stock.commodities && stock.commodities.toLowerCase().includes(searchTerm))
  );

  const sortStocks = () => {
    if (rankingCriteria === "cashflow") {
      let validStocks = stocks.filter(stock => !(stock.cashflow === null || stock.cashflow === 'N/A' || stock.cashflow === 'check'));
      let invalidStocks = stocks.filter(stock => (stock.cashflow === null || stock.cashflow === 'N/A' || stock.cashflow === 'check'));

      validStocks.sort((a, b) => a.cashflow - b.cashflow);

      setStocks([...validStocks, ...invalidStocks]);
    } else if (rankingCriteria === "score") {
      const sortedStocks = [...stocks];
      sortedStocks.sort((a, b) => b.liquidity_score - a.liquidity_score);
      setStocks(sortedStocks);
    } else if (rankingCriteria === "marketCap") {
      const sortedStocks = [...stocks];
      sortedStocks.sort((a, b) => a.cap - b.cap);
      setStocks(sortedStocks);
    } else if (rankingCriteria === "ev") {
      let validStocks = stocks.filter(stock => !(stock.EV === 'N/A'));
      let invalidStocks = stocks.filter(stock => stock.EV === 'N/A');

      validStocks.sort((a, b) => a.EV - b.EV);

      setStocks([...validStocks, ...invalidStocks]);
    } else if (rankingCriteria === "volumeToday") {
      let validStocks = stocks.filter(stock => !(stock.volume_today === null));
      let invalidStocks = stocks.filter(stock => (stock.volume_today === null));

      validStocks.sort((a, b) => b.volume_today - a.volume_today);

      setStocks([...validStocks, ...invalidStocks]);
    } else if (rankingCriteria === "volumeYesterday") {
      let validStocks = stocks.filter(stock => !(stock.volume === null || stock.volume === 'N/A' || stock.volume === 'check'));
      let invalidStocks = stocks.filter(stock => (stock.volume === null || stock.volume === 'N/A' || stock.volume === 'check'));

      validStocks.sort((a, b) => b.volume - a.volume);

      setStocks([...validStocks, ...invalidStocks]);
    } else if (rankingCriteria === "amountToday") {
      let validStocks = stocks.filter(stock => !(stock.amount_today === null));
      let invalidStocks = stocks.filter(stock => (stock.amount_today === null));

      validStocks.sort((a, b) => b.amount_today - a.amount_today);

      setStocks([...validStocks, ...invalidStocks]);
    }
  };



  // Helper function to format cashflow
  const formatCashflow = (value) => {
    if (value === null || value === 'check' || value === 'N/A') {
      return 'N/A';
    } else if (value >= 1000000) {
      return (value / 1000000).toFixed(2) + 'M';
    } else if (value <= -1000000) {
      return (value / 1000000).toFixed(2) + 'M';
    } else if (value >= 1000) {
      return (value / 1000).toFixed(2) + 'K';
    } else if (value <= -1000) {
      return (value / 1000).toFixed(2) + 'K';
    } else {
      return value.toString();
    }
  };


  const toggleColumnVisibility = (column) => {
    setColumnVisibility(prevVisibility => ({
      ...prevVisibility,
      [column]: !prevVisibility[column]
    }));
  };

  const downloadCSV = () => {
    // Generate CSV data
    const csvData = generateCSV(filteredStocks);

    // Create a blob of the data
    const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });

    // Save the file to the user's machine
    saveAs(blob, 'stocks.csv');
  }

  const generateCSV = (data) => {
    // Convert cap to M units and round to 2 decimals for CSV
    // Convert cashflow and EV with formatCashflow function
    data = data.map(stock => {
      let newStock = { ...stock };

      if (newStock.cap !== null && newStock.cap !== 'N/A' && newStock.cap !== 'check') {
        newStock.cap = formatCashflow(newStock.cap); // convert to M and round to 2 decimal places
      }

      if (newStock.cashflow !== null && newStock.cashflow !== 'N/A' && newStock.cashflow !== 'check') {
        newStock.cashflow = formatCashflow(newStock.cashflow);
      }

      if (newStock.EV !== null && newStock.EV !== 'N/A') {
        newStock.EV = formatCashflow(newStock.EV);
      }

      // Remove columns where columnVisibility is false
      for (const column in columnVisibility) {
        if (!columnVisibility[column]) {
          delete newStock[column];
        }
      }

      return newStock;
    });

    const replacer = (key, value) => value === null ? '' : value;
    const header = Object.keys(data[0]);
    let csv = data.map(row => header.map(fieldName => JSON.stringify(row[fieldName], replacer)).join(','));
    csv.unshift(header.join(','));
    csv = csv.join('\r\n');
    return csv;
  }






  return (
    <>
      <div className="container mt-1">
        <Button
          onClick={fetchStocks}
          variant="outline-success"
          size="sm"
          style={{
            position: 'fixed', top: '1vh', right: '1vh', margin: '10px'
          }}>
          Refresh
        </Button>

        <div className='d-flex align-items-center' >
          <Button
            variant="outline-secondary"
            style={{ marginRight: '40px' }}
            onClick={handleColumnChange}
            size="sm"
          >
            {column ? 'Hide Columns Filter' : 'Show Columns Filter'}
          </Button>
          <div style={{ display: 'flex', marginRight: '40px' }}>
            <label htmlFor="rankingCriteria" style={{ paddingRight: '1vw' }}>Ranking Criteria:</label>
            <select
              id="rankingCriteria"
              value={rankingCriteria}
              onChange={handleRankingCriteriaChange}
            >
              <option value="score">Score</option>
              <option value="marketCap">Market Cap</option>
              <option value="cashflow">Cashflow</option>
              <option value="ev">Shell Value</option>
              <option value="volumeToday">Today Volume</option>
              <option value="volumeYesterday">Yesterday Volume</option>
              <option value="amountToday">Today Amount</option>
            </select>
            <Button onClick={sortStocks} variant="outline-secondary" size="sm">Sort</Button>
          </div>
          <div style={{ display: 'flex', marginRight: '40px' }}>
            <label htmlFor="maxMarketCap" style={{ paddingRight: '1vw' }}>Max Market Cap (M): {maxMarketCap / 1000000} M</label>
            <input
              type="range"
              id="maxMarketCap"
              value={maxMarketCap / 1000000} // convert the number back to a string
              onChange={handleMaxMarketCapChange}
              min="0"
              max="210"
              step="5"
            />
          </div>

          <div style={{ marginRight: '40px' }}>
            <label htmlFor="showMiningOnly">Mining Companies: </label>
            <input type="checkbox" id="showMiningOnly" checked={showMiningOnly} onChange={toggleShowMiningOnly} />
          </div>

          <Button
            onClick={downloadCSV}
            variant="outline-success"
            size="sm"
            style={{ marginRight: '40px' }}
          >
            Download CSV
          </Button>
        </div>
        <div>
          <label htmlFor="searchTerm" style={{ marginTop: '10px' }}>Search:</label>
          <input
            type="text"
            id="searchTerm"
            value={searchTerm}
            onChange={handleSearchTermChange}
          />
        </div>
        {column && <div className="align-items-center justify-content-start" >
          {Object.keys(columnVisibility).map(column => (
            <Form.Check
              type="checkbox"
              id={column}
              label={column.charAt(0).toUpperCase() + column.slice(1)}
              checked={columnVisibility[column]}
              onChange={() => toggleColumnVisibility(column)}
              className="mr-3"
              style={{ paddingRight: '1vw' }}
            />
          ))}
        </div>}
      </div>
      {loading ? (
        <div className="text-center" style={{ paddingTop: '10vh' }}>
          <Spinner animation="border" variant="primary" />
          <p>Loading...</p>
        </div>
      ) : (
        <div style={{ marginLeft: '30px', marginRight: '30px' }}>
          <Table striped bordered hover style={{ marginTop: '20px' }}>
            <thead>
              <tr>
                {columnVisibility.code && <th>Code</th>}
                {columnVisibility.name && <th>Name</th>}
                {columnVisibility.price && <th>Closed Price</th>}
                {columnVisibility.marketCap && <th>Market Cap (M)</th>}
                {columnVisibility.liquidityScore && <th>Liquidity Score</th>}
                {columnVisibility.EMA_amount && <th>EMA Amount</th>}
                {columnVisibility.cashflow && <th>Cashflow</th>}
                {columnVisibility.debt && <th>debt</th>}
                {columnVisibility.EV && <th>Shell value</th>}
                {columnVisibility.price_today && <th>price_today</th>}
                {columnVisibility.volume_today && <th>Today Volume</th>}
                {columnVisibility.volume && <th>Yesterday Volume</th>}
                {columnVisibility.volume_5d && <th>Past 5 days Volume</th>}
                {columnVisibility.amount_today && <th>Today Amount</th>}
                {columnVisibility.amount && <th>Yesterday Amount</th>}
                {columnVisibility.amount_5d && <th>Past 5 days Amount</th>}
                {columnVisibility.industry && <th>Industry</th>}
                {columnVisibility.isMining && <th>isMining</th>}
                {columnVisibility.commodities && <th>Commodities</th>}

              </tr>
            </thead>
            <tbody>
              {searchedStocks.map((stock) => (
                <tr key={stock.stock_code}>
                  {columnVisibility.code && <td>{stock.stock_code}</td>}
                  {columnVisibility.name && <td>{stock.name}</td>}
                  {columnVisibility.price && <td>{stock.price}</td>}
                  {columnVisibility.marketCap && <td>{(stock.cap / 1000000).toFixed(2)}M</td>}
                  {columnVisibility.liquidityScore && <td>{stock.liquidity_score}</td>}
                  {columnVisibility.EMA_amount && <td>{stock.EMA_amount}</td>}
                  {columnVisibility.cashflow && <td>{formatCashflow(stock.cashflow)}</td>}
                  {columnVisibility.debt && <td>{formatCashflow(stock.debt)}</td>}
                  {columnVisibility.EV && <td>{formatCashflow(stock.EV)}</td>}
                  {columnVisibility.price_today && <td>{stock.price_today}</td>}
                  {columnVisibility.volume_today && <td>{stock.volume_today}</td>}
                  {columnVisibility.volume && <td>{stock.volume}</td>}
                  {columnVisibility.volume_5d && <td>{stock.volume_5d}</td>}
                  {columnVisibility.amount_today && <td>{stock.amount_today}</td>}
                  {columnVisibility.amount && <td>{stock.amount}</td>}
                  {columnVisibility.amount_5d && <td>{stock.amount_5d}</td>}
                  {columnVisibility.industry && <td>{stock.industry}</td>}
                  {columnVisibility.isMining && <td>{stock.isMining ? "yes" : "not"}</td>}
                  {columnVisibility.commodities && <td>{stock.commodities}</td>}
                  <td>
                    <Button
                      onClick={() => window.open(`https://stocknessmonster.com/widgets/471720501658ddff/stock-full#${stock.stock_code}`, '_blank')}
                      size="sm"
                      variant="outline-info"
                    >
                      View
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </div>
      )}

    </>
  );
}
