import React, { useEffect, useState } from "react";
import { Spinner } from "react-bootstrap";

export default function Liquidity() {
  const [stocks, setStocks] = useState([]);
  const [rankingCriteria, setRankingCriteria] = useState("score");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStocks();
  }, []);

  const fetchStocks = async () => {
    try {
      const response = await fetch("http://localhost:8000/database/stocks");
      const data = await response.json();
      setStocks(data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching stocks:", error);
      setLoading(false);
    }
  };

  const handleRankingCriteriaChange = (event) => {
    setRankingCriteria(event.target.value);
  };

  const sortStocks = () => {
    const sortedStocks = [...stocks];

    if (rankingCriteria === "score") {
      sortedStocks.sort((a, b) => b.liquidity_score - a.liquidity_score);
    } else if (rankingCriteria === "marketCap") {
      sortedStocks.sort((a, b) => b.cap - a.cap);
    }

    setStocks(sortedStocks);
  };

  return (
    <div>
      <div>
        <label htmlFor="rankingCriteria">Ranking Criteria:</label>
        <select
          id="rankingCriteria"
          value={rankingCriteria}
          onChange={handleRankingCriteriaChange}
        >
          <option value="score">Score</option>
          <option value="marketCap">Market Cap</option>
        </select>
        <button onClick={sortStocks}>Sort</button>
      </div>
      {loading ? (
        <div className="text-center">
          <Spinner animation="border" variant="primary" />
          <p>Loading...</p>
        </div>
      ) : (
        <table className="table">
        <thead>
          <tr>
            <th>Code</th>
            <th>Name</th>
            <th>Closed Price</th>
            <th>Market Cap (M)</th>
            <th>Liquidity Score</th>
            <th>EMA Amount</th>
            <th>Industry</th>
          </tr>
        </thead>
        <tbody>
          {stocks.map((stock) => (
            <tr key={stock.stock_code}>
              <td>{stock.stock_code}</td>
              <td>{stock.name}</td>
              <td>{stock.price}</td>
              <td>{(stock.cap / 1000000).toFixed(2)}</td>
              <td>{stock.liquidity_score}</td>
              <td>{stock.EMA_amount}</td>
              <td>{stock.industry}</td>
            </tr>
          ))}
        </tbody>
      </table>
      )}
    </div>
  );
}
