<script lang="ts">
  import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "$lib/components/ui/card";
  import { Input } from "$lib/components/ui/input";
  import { Label } from "$lib/components/ui/label";
  import { Button } from "$lib/components/ui/button";
  import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "$lib/components/ui/select";
  import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "$lib/components/ui/table";
</script>

<div class="space-y-6">
  <h1 class="text-3xl font-bold">Analysis</h1>

  <!-- Strategy Backtest Section -->
  <Card>
    <CardHeader>
      <CardTitle>Strategy Backtester</CardTitle>
      <CardDescription>Test your trading strategies with historical data</CardDescription>
    </CardHeader>
    <CardContent>
      <form class="space-y-4">
        <div class="grid gap-4 md:grid-cols-2">
          <div class="space-y-2">
            <Label>Strategy</Label>
            <Select>
              <SelectTrigger>
                <SelectValue placeholder="Select strategy" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ma-crossover">Moving Average Crossover</SelectItem>
                <SelectItem value="mean-reversion">Mean Reversion</SelectItem>
                <SelectItem value="breakout">Breakout</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div class="space-y-2">
            <Label>Symbol</Label>
            <Input placeholder="Enter symbol..." />
          </div>

          <div class="space-y-2">
            <Label>Start Date</Label>
            <Input type="date" />
          </div>

          <div class="space-y-2">
            <Label>End Date</Label>
            <Input type="date" />
          </div>
        </div>

        <Button>Run Backtest</Button>
      </form>
    </CardContent>
  </Card>

  <!-- Backtest Results -->
  <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
    <Card>
      <CardHeader>
        <CardTitle>Total Return</CardTitle>
      </CardHeader>
      <CardContent>
        <div class="text-2xl font-bold text-green-600">+45.2%</div>
        <p class="text-xs text-muted-foreground">Annualized: 15.4%</p>
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>Sharpe Ratio</CardTitle>
      </CardHeader>
      <CardContent>
        <div class="text-2xl font-bold">1.85</div>
        <p class="text-xs text-muted-foreground">Risk-adjusted return</p>
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>Max Drawdown</CardTitle>
      </CardHeader>
      <CardContent>
        <div class="text-2xl font-bold text-red-600">-12.5%</div>
        <p class="text-xs text-muted-foreground">Duration: 45 days</p>
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>Win Rate</CardTitle>
      </CardHeader>
      <CardContent>
        <div class="text-2xl font-bold">65.8%</div>
        <p class="text-xs text-muted-foreground">158 of 240 trades</p>
      </CardContent>
    </Card>
  </div>

  <!-- Performance Chart -->
  <Card>
    <CardHeader>
      <CardTitle>Backtest Performance</CardTitle>
      <CardDescription>Strategy performance vs. Benchmark</CardDescription>
    </CardHeader>
    <CardContent>
      <div class="h-[400px] flex items-center justify-center border rounded">
        Performance chart placeholder - Will integrate real chart library
      </div>
    </CardContent>
  </Card>

  <!-- Trade List -->
  <Card>
    <CardHeader>
      <CardTitle>Trade History</CardTitle>
      <CardDescription>Individual trade results</CardDescription>
    </CardHeader>
    <CardContent>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Date</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Entry Price</TableHead>
            <TableHead>Exit Price</TableHead>
            <TableHead>P/L</TableHead>
            <TableHead>Duration</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {#each Array(5) as _}
            <TableRow>
              <TableCell>2024-03-15</TableCell>
              <TableCell>Long</TableCell>
              <TableCell>$150.25</TableCell>
              <TableCell>$155.50</TableCell>
              <TableCell class="text-green-600">+3.49%</TableCell>
              <TableCell>3d 5h</TableCell>
            </TableRow>
          {/each}
        </TableBody>
      </Table>
    </CardContent>
  </Card>
</div>
