import React, { useEffect, useState, createContext, useContext } from "react";
import { serverURL } from './config';

const StocksContext = createContext();

export function useStocks() {
  return useContext(StocksContext);
}

export function StocksProvider({ children }) {
  const [stocks, setStocks] = useState([]);

  useEffect(() => {
    const fetchStocks = async () => {
      try {
        const response = await fetch(`${serverURL}/database/stocks`);
        const data = await response.json();
        setStocks(data);
      } catch (error) {
        console.error("Error fetching stocks:", error);
      }
    };

    if (stocks.length === 0) {
      fetchStocks();
    }
  }, [stocks]);

  return (
    <StocksContext.Provider value={[stocks, setStocks]}>
      {children}
    </StocksContext.Provider>
  );
}
