import { writable } from 'svelte/store';

interface ErrorState {
    message: string;
    type: 'error' | 'warning' | 'info';
    timestamp: number;
}

function createErrorStore() {
    const { subscribe, set } = writable<ErrorState | null>(null);

    return {
        subscribe,
        showError: (message: string) => {
            set({
                message,
                type: 'error',
                timestamp: Date.now()
            });
            setTimeout(() => set(null), 5000);
        },
        showWarning: (message: string) => {
            set({
                message,
                type: 'warning',
                timestamp: Date.now()
            });
            setTimeout(() => set(null), 5000);
        },
        showInfo: (message: string) => {
            set({
                message,
                type: 'info',
                timestamp: Date.now()
            });
            setTimeout(() => set(null), 5000);
        },
        clear: () => set(null)
    };
}

export const errorStore = createErrorStore();