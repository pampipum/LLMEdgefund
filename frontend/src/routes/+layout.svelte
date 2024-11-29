<script>
  import '../app.css';
</script>

<div class="min-h-screen bg-gray-100">
  <nav class="bg-white shadow-lg">
    <div class="max-w-7xl mx-auto px-4">
      <div class="flex justify-between h-16">
        <div class="flex">
          <div class="flex-shrink-0 flex items-center">
            <span class="text-xl font-bold">Edge Fund</span>
          </div>
          <div class="ml-6 flex space-x-8">
            <a href="/" class="inline-flex items-center px-1 pt-1 text-gray-900">Home</a>
            <a href="/backtest" class="inline-flex items-center px-1 pt-1 text-gray-900">Backtest</a>
          </div>
        </div>
      </div>
    </div>
  </nav>

  <main>
    <slot />
  </main>
</div>