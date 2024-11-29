import { writable } from 'svelte/store';

// Types
export interface MarketData {
    [symbol: string]: {
        price: number;
        volume: number;
        high: number;
        low: number;
        open: number;
        close: number;
        timestamp: number;
    };
}

export interface Position {
    symbol: string;
    quantity: number;
    entryPrice: number;
    currentPrice: number;
    pnl: number;
    pnlPercent: number;
}

export interface Order {
    id: string;
    symbol: string;
    side: 'buy' | 'sell';
    type: 'market' | 'limit' | 'stop';
    quantity: number;
    price?: number;
    status: 'pending' | 'filled' | 'cancelled';
    timestamp: number;
}

export interface Portfolio {
    totalValue: number;
    cashBalance: number;
    dayPnL: number;
    positions: Position[];
}

// Create stores
export const marketData = writable<MarketData>({});
export const portfolio = writable<Portfolio>({
    totalValue: 0,
    cashBalance: 0,
    dayPnL: 0,
    positions: []
});
export const orders = writable<Order[]>([]);

// Selected symbol store
export const selectedSymbol = writable<string>('AAPL');