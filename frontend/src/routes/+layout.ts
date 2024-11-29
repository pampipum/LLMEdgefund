import { wsService } from '$lib/services/websocket';
import type { LayoutLoad } from './$types';
import { browser } from '$app/environment';

export const load: LayoutLoad = async () => {
    // Only connect WebSocket in browser environment
    if (browser) {
        wsService.connect();
    }

    return {
        // Return any data needed globally
    };
};
