<script lang="ts">
  import { onMount } from 'svelte';
  import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "$lib/components/ui/card";
  import { Input } from "$lib/components/ui/input";
  import { Label } from "$lib/components/ui/label";
  import { Button } from "$lib/components/ui/button";
  import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "$lib/components/ui/select";
  import TradingChart from "$lib/components/TradingChart.svelte";
  import { api } from "$lib/services/api";
  import { wsService } from "$lib/services/websocket";
  import { marketData, orders, selectedSymbol } from "$lib/stores/trading";
  import { errorStore } from "$lib/stores/error";

  let symbol = "AAPL";
  let orderType = "market";
  let side = "buy";
  let quantity = 0;
  let price = 0;

  // Form validation
  $: isValidOrder = symbol && quantity > 0 && 
    (orderType === 'market' || (orderType !== 'market' && price > 0));

  async function handleSubmitOrder() {
    if (!isValidOrder) return;

    try {
      const response = await api.placeOrder({
        symbol,
        type: orderType,
        side,
        quantity,
        price: orderType !== 'market' ? price : undefined
      });

      if (response.success) {
        errorStore.showInfo('Order placed successfully');
        // Clear form
        quantity = 0;
        price = 0;
      } else {
        errorStore.showError(`Order failed: ${response.error}`);
      }
    } catch (error) {
      console.error('Order submission error:', error);
      errorStore.showError('Failed to submit order. Please try again.');
    }
  }

  async function handleCancelOrder(orderId: string) {
    try {
      const response = await api.cancelOrder(orderId);
      if (response.success) {
        errorStore.showInfo('Order cancelled successfully');
      } else {
        errorStore.showError(`Failed to cancel order: ${response.error}`);
      }
    } catch (error) {
      console.error('Order cancellation error:', error);
      errorStore.showError('Failed to cancel order. Please try again.');
    }
  }

  onMount(async () => {
    // Connect WebSocket
    wsService.connect();
    
    // Subscribe to current symbol
    wsService.subscribeToSymbols([symbol]);

    // Load initial orders
    const ordersResponse = await api.getOrders();
    if (ordersResponse.success) {
      orders.set(ordersResponse.data);
    }

    return () => {
      wsService.disconnect();
    };
  });

  // Update WebSocket subscription when symbol changes
  $: if (symbol) {
    selectedSymbol.set(symbol);
    wsService.subscribeToSymbols([symbol]);
  }

  // Subscribe to WebSocket state
  let wsState = { connected: false };
  wsService.subscribe(state => {
    wsState = state;
  });
</script>

<div class="space-y-4">
  <h1 class="text-3xl font-bold">Trading</h1>

  <div class="grid gap-4 lg:grid-cols-3">
    <!-- Chart Section -->
    <div class="lg:col-span-2">
      <Card>
        <CardHeader>
          <CardTitle>{symbol}</CardTitle>
          <CardDescription>
            {#if $marketData[symbol]}
              Last Price: ${$marketData[symbol].price?.toFixed(2)}
            {/if}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div class="h-[500px]">
            <TradingChart />
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Order Entry -->
    <div>
      <Card>
        <CardHeader>
          <CardTitle>Place Order</CardTitle>
          <CardDescription>Enter your trade details</CardDescription>
        </CardHeader>
        <CardContent>
          <form class="space-y-4" on:submit|preventDefault={handleSubmitOrder}>
            <div class="space-y-2">
              <Label for="symbol">Symbol</Label>
              <Input 
                id="symbol" 
                bind:value={symbol} 
                placeholder="Enter symbol..." 
              />
            </div>

            <div class="space-y-2">
              <Label>Order Type</Label>
              <Select bind:value={orderType}>
                <SelectTrigger>
                  <SelectValue placeholder="Select order type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="market">Market</SelectItem>
                  <SelectItem value="limit">Limit</SelectItem>
                  <SelectItem value="stop">Stop</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div class="space-y-2">
              <Label>Side</Label>
              <Select bind:value={side}>
                <SelectTrigger>
                  <SelectValue placeholder="Select side" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="buy">Buy</SelectItem>
                  <SelectItem value="sell">Sell</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div class="space-y-2">
              <Label for="quantity">Quantity</Label>
              <Input 
                id="quantity" 
                type="number" 
                bind:value={quantity} 
                min="0" 
                step="1"
                placeholder="Enter quantity..." 
              />
            </div>

            {#if orderType !== 'market'}
              <div class="space-y-2">
                <Label for="price">Price</Label>
                <Input 
                  id="price" 
                  type="number" 
                  bind:value={price} 
                  min="0" 
                  step="0.01" 
                  placeholder="Enter price..." 
                />
              </div>
            {/if}

            <Button 
              class="w-full" 
              type="submit" 
              disabled={!isValidOrder || !wsState.connected}
            >
              {wsState.connected ? 'Place Order' : 'Waiting for connection...'}
            </Button>
          </form>
        </CardContent>
      </Card>

      <!-- Open Orders -->
      <Card class="mt-4">
        <CardHeader>
          <CardTitle>Open Orders</CardTitle>
          <CardDescription>{$orders.length} Active Orders</CardDescription>
        </CardHeader>
        <CardContent>
          <div class="space-y-2">
            {#if $orders.length === 0}
              <p class="text-muted-foreground text-center py-4">No open orders</p>
            {:else}
              {#each $orders as order}
                <div class="flex justify-between items-center p-2 rounded hover:bg-muted">
                  <div>
                    <div class="font-medium">{order.symbol}</div>
                    <div class="text-sm text-muted-foreground">
                      {order.side.charAt(0).toUpperCase() + order.side.slice(1)} 
                      {order.type.charAt(0).toUpperCase() + order.type.slice(1)} 
                      @ {order.price ? `$${order.price}` : 'Market'}
                    </div>
                    <div class="text-xs text-muted-foreground">
                      {order.quantity} shares
                    </div>
                  </div>
                  <Button 
                    variant="destructive" 
                    size="sm"
                    on:click={() => handleCancelOrder(order.id)}
                    disabled={!wsState.connected}
                  >
                    Cancel
                  </Button>
                </div>
              {/each}
            {/if}
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</div>