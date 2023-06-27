import React, { useEffect, useState } from "react";
import { Spinner, Table, Form, Button } from "react-bootstrap";

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
    EMA_amount: true,
    cashflow: true,
    industry: true,
    EV: true
  });
  const [maxMarketCap, setMaxMarketCap] = useState(200000000);

  useEffect(() => {
    //const cachedStocks = localStorage.getItem('stocks');
    const cachedStocks = false
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

  const filteredStocks = stocks.filter(stock => stock.cap <= maxMarketCap);

  const sortStocks = () => {
    if (rankingCriteria === "cashflow") {
      let validStocks = stocks.filter(stock => !(stock.cashflow === null || stock.cashflow === 'N/A' || stock.cashflow === 'check'));
      let invalidStocks = stocks.filter(stock => (stock.cashflow === null || stock.cashflow === 'N/A' || stock.cashflow === 'check'));

      validStocks.sort((a, b) => b.cashflow - a.cashflow);

      setStocks([...validStocks, ...invalidStocks]);
    } else if (rankingCriteria === "score") {
      const sortedStocks = [...stocks];
      sortedStocks.sort((a, b) => b.liquidity_score - a.liquidity_score);
      setStocks(sortedStocks);
    } else if (rankingCriteria === "marketCap") {
      const sortedStocks = [...stocks];
      sortedStocks.sort((a, b) => b.cap - a.cap);
      setStocks(sortedStocks);
    }
  };



  // Helper function to format cashflow
  const formatCashflow = (value) => {
    if (value === null || value === 'check' || value === 'N/A') {
      return 'N/A';
    } else if (value >= 1000000) {
      return (value / 1000000).toFixed(2) + 'M';
    } else if (value >= 1000) {
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

  return (
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
      <div style={{ display: 'flex' }}>
        <label htmlFor="rankingCriteria" style={{ paddingRight: '1vw' }}>Ranking Criteria:</label>
        <select
          id="rankingCriteria"
          value={rankingCriteria}
          onChange={handleRankingCriteriaChange}
        >
          <option value="score">Score</option>
          <option value="marketCap">Market Cap</option>
          <option value="cashflow">Cashflow</option>
        </select>
        <Button onClick={sortStocks} variant="outline-secondary" size="sm">Sort</Button>
      </div>
      <div style={{ display: 'flex' }}>
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

      <div className="d-flex align-items-center justify-content-start" >
        {Object.keys(columnVisibility).map(column => (
          <Form.Check
            type="checkbox"
            id={column}
            label={column.charAt(0).toUpperCase() + column.slice(1)}
            checked={columnVisibility[column]}
            onChange={() => toggleColumnVisibility(column)}
            className="mr-3"
            style={{ paddingRight: '3vw' }}
          />
        ))}
      </div>

      {loading ? (
        <div className="text-center" style={{ paddingTop: '10vh' }}>
          <Spinner animation="border" variant="primary" />
          <p>Loading...</p>
        </div>
      ) : (
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
              {columnVisibility.EV && <th>Shell value</th>}
              
              {columnVisibility.industry && <th>Industry</th>}
              
            </tr>
          </thead>
          <tbody>
            {filteredStocks.map((stock) => (
              <tr key={stock.stock_code}>
                {columnVisibility.code && <td>{stock.stock_code}</td>}
                {columnVisibility.name && <td>{stock.name}</td>}
                {columnVisibility.price && <td>{stock.price}</td>}
                {columnVisibility.marketCap && <td>{(stock.cap / 1000000).toFixed(2)}M</td>}
                {columnVisibility.liquidityScore && <td>{stock.liquidity_score}</td>}
                {columnVisibility.EMA_amount && <td>{stock.EMA_amount}</td>}
                {columnVisibility.cashflow && <td>{formatCashflow(stock.cashflow)}</td>}
                {columnVisibility.EV && <td>{stock.EV}</td>}
                {columnVisibility.industry && <td>{stock.industry}</td>}
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </div>
  );
}
