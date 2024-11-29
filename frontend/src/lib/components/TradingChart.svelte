<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { createChart, ColorType, UTCTimestamp } from 'lightweight-charts';
    import { marketData, selectedSymbol } from '$lib/stores/trading';

    export let width = '100%';
    export let height = '100%';

    let chartContainer: HTMLElement;
    let chart: any;
    let candlestickSeries: any;
    let volumeSeries: any;

    // Subscribe to market data updates
    $: if (candlestickSeries && $marketData[$selectedSymbol]) {
        const data = $marketData[$selectedSymbol];
        candlestickSeries.update({
            time: data.timestamp as UTCTimestamp,
            open: data.open,
            high: data.high,
            low: data.low,
            close: data.close
        });
        
        volumeSeries.update({
            time: data.timestamp as UTCTimestamp,
            value: data.volume
        });
    }

    onMount(() => {
        chart = createChart(chartContainer, {
            width: chartContainer.clientWidth,
            height: chartContainer.clientHeight,
            layout: {
                background: { type: ColorType.Solid, color: '#1E1E1E' },
                textColor: '#DDD',
            },
            grid: {
                vertLines: { color: '#2B2B2B' },
                horzLines: { color: '#2B2B2B' },
            },
            crosshair: {
                mode: 0
            },
            rightPriceScale: {
                borderColor: '#2B2B2B',
            },
            timeScale: {
                borderColor: '#2B2B2B',
                timeVisible: true,
            },
        });

        candlestickSeries = chart.addCandlestickSeries({
            upColor: '#26a69a',
            downColor: '#ef5350',
            borderVisible: false,
            wickUpColor: '#26a69a',
            wickDownColor: '#ef5350'
        });

        volumeSeries = chart.addHistogramSeries({
            color: '#26a69a',
            priceFormat: {
                type: 'volume',
            },
            priceScaleId: '',
            scaleMargins: {
                top: 0.8,
                bottom: 0,
            },
        });

        // Handle resize
        const resizeObserver = new ResizeObserver(entries => {
            if (entries.length === 0 || !chart) return;
            const newRect = entries[0].contentRect;
            chart.applyOptions({ width: newRect.width, height: newRect.height });
        });

        resizeObserver.observe(chartContainer);

        return () => {
            resizeObserver.disconnect();
            if (chart) {
                chart.remove();
            }
        };
    });

    onDestroy(() => {
        if (chart) {
            chart.remove();
        }
    });
</script>

<div class="chart-container" bind:this={chartContainer} style="width: {width}; height: {height};">
</div>

<style>
    .chart-container {
        position: relative;
    }
</style>