<script lang="ts">
  import { lightbox } from '$lib/stores';

  let dialog = $state<HTMLDialogElement | null>(null);

  $effect(() => {
    if (!dialog) return;
    if ($lightbox) {
      dialog.showModal();
    } else if (dialog.open) {
      dialog.close();
    }
  });

  function handleClose() {
    lightbox.set(null);
  }

  function handleBackdropClick(e: MouseEvent) {
    if (e.target === dialog) lightbox.set(null);
  }
</script>

<dialog
  bind:this={dialog}
  class="card-lightbox"
  aria-modal="true"
  aria-label={$lightbox ? `Full card: ${$lightbox.name}` : 'Card view'}
  onclose={handleClose}
  onclick={handleBackdropClick}
>
  <div class="card-lightbox-panel">
    <form method="dialog" class="card-lightbox-close-wrap">
      <button type="submit" class="card-lightbox-close">Close</button>
    </form>
    {#if $lightbox}
      <img class="card-lightbox-img" src={$lightbox.src} alt={$lightbox.name} />
    {/if}
  </div>
</dialog>
