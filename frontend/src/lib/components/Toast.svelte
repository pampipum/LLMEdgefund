<script lang="ts">
    import { errorStore } from '$lib/stores/error';
    import { fly } from 'svelte/transition';
    import { Alert, AlertDescription } from "$lib/components/ui/alert";
    import { X } from 'lucide-svelte';

    function getAlertVariant(type: 'error' | 'warning' | 'info') {
        switch (type) {
            case 'error':
                return 'destructive';
            case 'warning':
                return 'warning';
            case 'info':
                return 'info';
            default:
                return 'default';
        }
    }
</script>

{#if $errorStore}
    <div class="fixed bottom-4 right-4 z-50"
         transition:fly={{ y: 50, duration: 200 }}>
        <Alert variant={getAlertVariant($errorStore.type)} class="w-96">
            <AlertDescription>{$errorStore.message}</AlertDescription>
            <button
                class="absolute right-2 top-2 rounded-full p-1 transition-colors hover:bg-muted"
                on:click={() => errorStore.clear()}
            >
                <X class="h-4 w-4" />
            </button>
        </Alert>
    </div>
{/if}