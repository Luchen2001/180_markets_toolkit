import React from "react";
import { Container, Card, Button } from "react-bootstrap";

export default function Home() {
    return (
        <Container>
            <Card className="mt-5">
                <Card.Header as="h2">180 Markets Pty Ltd Project</Card.Header>
                <Card.Body>
                    <Card.Text>
                        Simple website application built for 180 Markets Pty Ltd with the following features:
                        <ol>
                            <li>Crawling the cash flow based on market cap and derive the liquidity score based on the course of sale.</li>
                            <li>Tracking the placement performance done by the company by tracking the stock price over time.</li>
                        </ol>
                        Two ASX endpoints have been used for querying the cashflow announcements and price information: 
                        <ul>
                            <li><a href="https://www.asx.com.au/asx/1/share/MCL/prices?interval=daily&count=255" target="_blank" rel="noopener noreferrer">Prices</a></li>
                            <li><a href="https://www.asx.com.au/asx/1/company/ZEU/announcements?count=20&market_sensitive=false" target="_blank" rel="noopener noreferrer">Announcements</a></li>
                        </ul>
                    </Card.Text>
                    <Button variant="primary" href="https://github.com/Luchen2001/180_markets_toolkit" target="_blank" rel="noopener noreferrer">View Code on Github</Button>
                </Card.Body>
            </Card>
        </Container>
    )
}
