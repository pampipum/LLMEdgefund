<script lang="ts">
  import { onMount } from 'svelte';
  import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "$lib/components/ui/card";
  import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "$lib/components/ui/table";
  import { Button } from "$lib/components/ui/button";
  import { api } from "$lib/services/api";
  import { wsService } from "$lib/services/websocket";
  import { portfolio } from "$lib/stores/trading";
  import TradingChart from "$lib/components/TradingChart.svelte";

  let selectedPosition: any = null;

  async function loadPortfolioData() {
    try {
      const response = await api.getPortfolio();
      if (response.success) {
        portfolio.set(response.data);
      }
    } catch (error) {
      console.error('Failed to load portfolio data:', error);
    }
  }

  async function handleClosePosition(symbol: string) {
    try {
      const position = $portfolio.positions.find(p => p.symbol === symbol);
      if (!position) return;

      const response = await api.placeOrder({
        symbol,
        type: 'market',
        side: position.quantity > 0 ? 'sell' : 'buy',
        quantity: Math.abs(position.quantity)
      });

      if (!response.success) {
        alert(`Failed to close position: ${response.error}`);
      }
    } catch (error) {
      console.error('Failed to close position:', error);
      alert('Failed to close position. Please try again.');
    }
  }

  onMount(() => {
    loadPortfolioData();
    wsService.connect();

    // Subscribe to all position symbols
    if ($portfolio.positions) {
      const symbols = $portfolio.positions.map(p => p.symbol);
      wsService.subscribe(symbols);
    }

    return () => {
      wsService.disconnect();
    };
  });

  // Helper function to format currency
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  // Helper function to format percentage
  const formatPercent = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value / 100);
  };
</script>

<div class="space-y-6">
  <h1 class="text-3xl font-bold">Portfolio</h1>

  <!-- Summary Cards -->
  <div class="grid gap-4 md:grid-cols-3">
    <Card>
      <CardHeader>
        <CardTitle>Total Value</CardTitle>
        <CardDescription>Current portfolio value</CardDescription>
      </CardHeader>
      <CardContent>
        <div class="text-2xl font-bold">{formatCurrency($portfolio.totalValue)}</div>
        <p class="text-xs text-muted-foreground">Including cash balance</p>
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>Today's P/L</CardTitle>
        <CardDescription>Unrealized gains/losses</CardDescription>
      </CardHeader>
      <CardContent>
        <div class="text-2xl font-bold" class:text-green-600={$portfolio.dayPnL >= 0} class:text-red-600={$portfolio.dayPnL < 0}>
          {formatCurrency($portfolio.dayPnL)}
        </div>
        <p class="text-xs text-muted-foreground">Today's change</p>
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>Cash Balance</CardTitle>
        <CardDescription>Available for trading</CardDescription>
      </CardHeader>
      <CardContent>
        <div class="text-2xl font-bold">{formatCurrency($portfolio.cashBalance)}</div>
        <p class="text-xs text-muted-foreground">
          {formatPercent(($portfolio.cashBalance / $portfolio.totalValue) * 100)} of portfolio
        </p>
      </CardContent>
    </Card>
  </div>

  <!-- Positions Table -->
  <Card>
    <CardHeader>
      <CardTitle>Open Positions</CardTitle>
      <CardDescription>Currently held positions</CardDescription>
    </CardHeader>
    <CardContent>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Symbol</TableHead>
            <TableHead>Quantity</TableHead>
            <TableHead>Entry Price</TableHead>
            <TableHead>Current Price</TableHead>
            <TableHead>P/L</TableHead>
            <TableHead>P/L %</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {#if $portfolio.positions && $portfolio.positions.length > 0}
            {#each $portfolio.positions as position}
              <TableRow>
                <TableCell class="font-medium">{position.symbol}</TableCell>
                <TableCell>{position.quantity}</TableCell>
                <TableCell>{formatCurrency(position.entryPrice)}</TableCell>
                <TableCell>{formatCurrency(position.currentPrice)}</TableCell>
                <TableCell>
                  <span class:text-green-600={position.pnl >= 0} class:text-red-600={position.pnl < 0}>
                    {formatCurrency(position.pnl)}
                  </span>
                </TableCell>
                <TableCell>
                  <span class:text-green-600={position.pnlPercent >= 0} class:text-red-600={position.pnlPercent < 0}>
                    {formatPercent(position.pnlPercent)}
                  </span>
                </TableCell>
                <TableCell>
                  <div class="space-x-2">
                    <Button size="sm" on:click={() => selectedPosition = position}>Chart</Button>
                    <Button size="sm" variant="destructive" on:click={() => handleClosePosition(position.symbol)}>Close</Button>
                  </div>
                </TableCell>
              </TableRow>
            {/each}
          {:else}
            <TableRow>
              <TableCell colspan="7" class="text-center text-muted-foreground">
                No open positions
              </TableCell>
            </TableRow>
          {/if}
        </TableBody>
      </Table>
    </CardContent>
  </Card>

  <!-- Chart for selected position -->
  {#if selectedPosition}
    <Card>
      <CardHeader>
        <CardTitle>{selectedPosition.symbol} Chart</CardTitle>
        <CardDescription>Position Details</CardDescription>
      </CardHeader>
      <CardContent>
        <div class="h-[400px]">
          <TradingChart symbol={selectedPosition.symbol} />
        </div>
      </CardContent>
    </Card>
  {/if}
</div>