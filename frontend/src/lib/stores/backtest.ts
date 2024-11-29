import { writable } from 'svelte/store';

export interface BacktestResult {
    totalReturn: number;
    sharpeRatio: number;
    maxDrawdown: number;
    winRate: number;
    trades: BacktestTrade[];
    equityCurve: EquityPoint[];
}

export interface BacktestTrade {
    timestamp: number;
    symbol: string;
    side: 'long' | 'short';
    entryPrice: number;
    exitPrice: number;
    pnl: number;
    pnlPercent: number;
    duration: number;
}

export interface EquityPoint {
    timestamp: number;
    value: number;
    drawdown: number;
}

export const backtestResults = writable<BacktestResult | null>(null);
export const isBacktesting = writable<boolean>(false);