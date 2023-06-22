import React, { useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";

export default function Calculator() {
  const [bidPrice, setBidPrice] = useState("");
  const [bidVolume, setBidVolume] = useState("");
  const [bidPrice2, setBidPrice2] = useState("");
  const [bidVolume2, setBidVolume2] = useState("");
  const [askPrice, setAskPrice] = useState("");
  const [askVolume, setAskVolume] = useState("");
  const [askPrice2, setAskPrice2] = useState("");
  const [askVolume2, setAskVolume2] = useState("");

  return (
    <div className="container">
      <div className="row">
        <div className="col">
          <h2>Bid</h2>
          <div className="form-group row">
            <label htmlFor="bidPrice" className="col-sm-4 col-form-label">
              Price:
            </label>
            <div className="col-sm-8">
              <input
                type="text"
                className="form-control"
                id="bidPrice"
                value={bidPrice}
                onChange={(e) => setBidPrice(e.target.value)}
              />
            </div>
            <label htmlFor="bidVolume" className="col-sm-4 col-form-label">
              Volume:
            </label>
            <div className="col-sm-8">
              <input
                type="text"
                className="form-control"
                id="bidVolume"
                value={bidVolume}
                onChange={(e) => setBidVolume(e.target.value)}
              />
            </div>
          </div>
          <div className="form-group row">
            <label htmlFor="bidPrice2" className="col-sm-4 col-form-label">
              Price 2:
            </label>
            <div className="col-sm-8">
              <input
                type="text"
                className="form-control"
                id="bidPrice2"
                value={bidPrice2}
                onChange={(e) => setBidPrice2(e.target.value)}
              />
            </div>
            <label htmlFor="bidVolume2" className="col-sm-4 col-form-label">
              Volume 2:
            </label>
            <div className="col-sm-8">
              <input
                type="text"
                className="form-control"
                id="bidVolume2"
                value={bidVolume2}
                onChange={(e) => setBidVolume2(e.target.value)}
              />
            </div>
          </div>
        </div>
        <div className="col">
          <h2>Ask</h2>
          <div className="form-group row">
            <label htmlFor="askPrice" className="col-sm-4 col-form-label">
              Price:
            </label>
            <div className="col-sm-8">
              <input
                type="text"
                className="form-control"
                id="askPrice"
                value={askPrice}
                onChange={(e) => setAskPrice(e.target.value)}
              />
            </div>
            <label htmlFor="askVolume" className="col-sm-4 col-form-label">
              Volume:
            </label>
            <div className="col-sm-8">
              <input
                type="text"
                className="form-control"
                id="askVolume"
                value={askVolume}
                onChange={(e) => setAskVolume(e.target.value)}
              />
            </div>
          </div>
          <div className="form-group row">
            <label htmlFor="askPrice2" className="col-sm-4 col-form-label">
              Price 2:
            </label>
            <div className="col-sm-8">
              <input
                type="text"
                className="form-control"
                id="askPrice2"
                value={askPrice2}
                onChange={(e) => setAskPrice2(e.target.value)}
              />
            </div>
            <label htmlFor="askVolume2" className="col-sm-4 col-form-label">
              Volume 2:
            </label>
            <div className="col-sm-8">
              <input
                type="text"
                className="form-control"
                id="askVolume2"
                value={askVolume2}
                onChange={(e) => setAskVolume2(e.target.value)}
              />
            </div>
          </div>
        </div>
      </div>
      <div className="row">
        <div className="col text-center">
          <button className="btn btn-primary">Calculate</button>
        </div>
      </div>
      <div className="row">
        <div className="col">
          <h2>Result</h2>
          <p>Bid 1: {bidPrice * bidVolume}</p>
          <p>Bid 2: {bidPrice2 * bidVolume2}</p>
          <p>Ask 1: {askPrice * askVolume}</p>
          <p>Ask 2: {askPrice2 * askVolume2}</p>
        </div>
      </div>
    </div>
  );
}
