import { writable } from 'svelte/store';
import { get } from 'svelte/store';
import { marketData, portfolio, orders } from '../stores/trading';

interface WebSocketState {
    connected: boolean;
    lastMessage: any | null;
}

export class WebSocketService {
    private ws: WebSocket | null = null;
    private reconnectAttempts = 0;
    private maxReconnectAttempts = 5;
    private reconnectTimeout = 1000;
    private store = writable<WebSocketState>({
        connected: false,
        lastMessage: null
    });

    constructor(private url: string = 'ws://localhost:8000/ws') {}

    subscribe(run: (value: WebSocketState) => void) {
        return this.store.subscribe(run);
    }

    connect() {
        try {
            this.ws = new WebSocket(this.url);
            this.setupEventListeners();
        } catch (error) {
            console.error('WebSocket connection error:', error);
            this.handleReconnect();
        }
    }

    private setupEventListeners() {
        if (!this.ws) return;

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.store.update(state => ({ ...state, connected: true }));
            this.reconnectAttempts = 0;
            this.reconnectTimeout = 1000;
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.store.update(state => ({ ...state, connected: false }));
            this.handleReconnect();
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.store.update(state => ({ ...state, connected: false }));
        };

        this.ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                this.store.update(state => ({ ...state, lastMessage: message }));
                this.handleMessage(message);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };
    }

    private handleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectTimeout);

            this.reconnectTimeout *= 2;
        } else {
            console.error('Max reconnection attempts reached');
        }
    }

    private handleMessage(message: any) {
        switch (message.type) {
            case 'MARKET_DATA':
                marketData.update(data => ({
                    ...data,
                    [message.symbol]: message.data
                }));
                break;
            
            case 'PORTFOLIO_UPDATE':
                portfolio.set(message.data);
                break;

            case 'ORDER_UPDATE':
                orders.update(currentOrders => {
                    const index = currentOrders.findIndex(o => o.id === message.data.id);
                    if (index >= 0) {
                        const updatedOrders = [...currentOrders];
                        updatedOrders[index] = message.data;
                        return updatedOrders;
                    }
                    return [...currentOrders, message.data];
                });
                break;

            default:
                console.warn('Unknown message type:', message.type);
        }
    }

    subscribeToSymbols(symbols: string[] = []) {
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'SUBSCRIBE',
                symbols
            }));
        }
    }

    unsubscribeFromSymbols(symbols: string[] = []) {
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'UNSUBSCRIBE',
                symbols
            }));
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
            this.store.update(state => ({ ...state, connected: false }));
        }
    }
}

// Create and export a singleton instance
export const wsService = new WebSocketService();