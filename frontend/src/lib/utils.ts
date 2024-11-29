import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

// Combine Tailwind classes safely
export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

// Format currency
export function formatCurrency(value: number): string {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

// Format percentage
export function formatPercent(value: number): string {
    return new Intl.NumberFormat('en-US', {
        style: 'percent',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value / 100);
}

// Format large numbers
export function formatNumber(value: number): string {
    return new Intl.NumberFormat('en-US').format(value);
}

// Format date
export function formatDate(date: Date | number): string {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(typeof date === 'number' ? new Date(date) : date);
}

// Calculate percentage change
export function calculatePercentChange(current: number, previous: number): number {
    if (previous === 0) return 0;
    return ((current - previous) / Math.abs(previous)) * 100;
}

// Parse number with fallback
export function parseNumber(value: string, fallback: number = 0): number {
    const parsed = parseFloat(value);
    return isNaN(parsed) ? fallback : parsed;
}

// Debounce function
export function debounce<T extends (...args: any[]) => any>(
    func: T,
    wait: number
): (...args: Parameters<T>) => void {
    let timeout: NodeJS.Timeout;
    return (...args: Parameters<T>) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}

// Throttle function
export function throttle<T extends (...args: any[]) => any>(
    func: T,
    limit: number
): (...args: Parameters<T>) => void {
    let inThrottle: boolean = false;
    return (...args: Parameters<T>) => {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => (inThrottle = false), limit);
        }
    };
}
