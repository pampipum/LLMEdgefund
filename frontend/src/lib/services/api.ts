const API_BASE_URL = 'http://localhost:8000';

type ApiResponse<T> = {
    success: boolean;
    data?: T;
    error?: string;
};

async function handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    if (!response.ok) {
        const error = await response.text();
        return { success: false, error };
    }
    const data = await response.json();
    return { success: true, data };
}

export const api = {
    // Market Data
    async getMarketData(symbol: string, timeframe: string = '1d'): Promise<ApiResponse<any>> {
        const response = await fetch(`${API_BASE_URL}/market-data/${symbol}?timeframe=${timeframe}`);
        return handleResponse(response);
    },

    // Trading
    async placeOrder(orderData: any): Promise<ApiResponse<any>> {
        const response = await fetch(`${API_BASE_URL}/orders`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(orderData),
        });
        return handleResponse(response);
    },

    async getOrders(): Promise<ApiResponse<any>> {
        const response = await fetch(`${API_BASE_URL}/orders`);
        return handleResponse(response);
    },

    async cancelOrder(orderId: string): Promise<ApiResponse<any>> {
        const response = await fetch(`${API_BASE_URL}/orders/${orderId}`, {
            method: 'DELETE',
        });
        return handleResponse(response);
    },

    // Portfolio
    async getPortfolio(): Promise<ApiResponse<any>> {
        const response = await fetch(`${API_BASE_URL}/portfolio`);
        return handleResponse(response);
    },

    async getPositions(): Promise<ApiResponse<any>> {
        const response = await fetch(`${API_BASE_URL}/positions`);
        return handleResponse(response);
    },

    // Backtesting
    async runBacktest(strategyConfig: any): Promise<ApiResponse<any>> {
        const response = await fetch(`${API_BASE_URL}/backtest`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(strategyConfig),
        });
        return handleResponse(response);
    },

    // Account
    async getAccountInfo(): Promise<ApiResponse<any>> {
        const response = await fetch(`${API_BASE_URL}/account`);
        return handleResponse(response);
    }
};