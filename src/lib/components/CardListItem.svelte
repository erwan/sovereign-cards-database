<script lang="ts">
  import { lightbox } from '$lib/stores';
  import { cardBlockTypeLabel, type CardEntry } from '$lib/decks-content';

  interface Props {
    card: CardEntry;
    imageSrc: string;
    view?: 'list' | 'gallery';
    typeLabel?: string;
    priority?: boolean;
  }

  let { card, imageSrc, view = 'gallery', typeLabel = undefined, priority = false }: Props = $props();

  const displayTypeLabel = $derived(typeLabel ?? cardBlockTypeLabel(card));
  const isList = $derived(view === 'list');

  function open() {
    lightbox.set({ src: imageSrc, name: card.name });
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      open();
    }
  }
</script>

<li>
  <!-- svelte-ignore a11y_no_noninteractive_tabindex -->
  <div
    class="card-item"
    data-full-src={imageSrc}
    data-card-name={card.name}
    data-card-cost={String(card.cost)}
    role={isList ? 'button' : undefined}
    tabindex={isList ? 0 : undefined}
    aria-label={isList ? `View full card: ${card.name}, cost ${card.cost}` : undefined}
    onclick={isList ? open : undefined}
    onkeydown={isList ? handleKeydown : undefined}
  >
    <img
      class="card-thumb"
      src={imageSrc}
      alt={isList ? '' : card.name}
      width="120"
      height="168"
      loading={priority ? 'eager' : 'lazy'}
      fetchpriority={priority ? 'high' : undefined}
    />
    <div class="card-meta">
      <span class="card-name">{card.name}</span>
      <span class="card-type">{displayTypeLabel}</span>
      <span
        class="card-cost"
        class:card-cost--reflex={card.type === 'reflex'}
        aria-hidden="true"
      >
        {card.cost}
      </span>
    </div>
  </div>
</li>
