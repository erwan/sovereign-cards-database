<script lang="ts">
  import CardLightbox from '$lib/components/CardLightbox.svelte';
  import CardListItem from '$lib/components/CardListItem.svelte';
  import DeckCostHistograms from '$lib/components/DeckCostHistograms.svelte';
  import DeckHeader from '$lib/components/DeckHeader.svelte';
  import FactionPageLayout from '$lib/components/FactionPageLayout.svelte';
  import ViewToggle from '$lib/components/ViewToggle.svelte';
  import { DISPLAY_TYPE_ORDER, compareCardsByCostThenName, typeSectionHeading, type CardEntry } from '$lib/decks-content';
  import { viewPreference } from '$lib/stores';
  import { base } from '$app/paths';

  let { data } = $props();
  let deck = $derived(data.deck);
  let assetPrefix = $derived(`${base}/cards/${deck.slug}/`);
</script>

<svelte:head>
  <title>{deck.displayName} — Sovereign Cards</title>
</svelte:head>

<FactionPageLayout>
  {#snippet headerActions()}
    <ViewToggle />
  {/snippet}

  <div class="faction-detail" data-deck-view={$viewPreference}>
    <DeckHeader {deck} coverSrc="{assetPrefix}leader.jpg" />
    <DeckCostHistograms {deck} />
    {#each DISPLAY_TYPE_ORDER as type}
      {@const sectionCards = deck.cards
        .filter((c: CardEntry) => c.type === type)
        .sort(compareCardsByCostThenName)}
      {#if sectionCards.length > 0}
        <section class="card-type-section" aria-labelledby="type-{type}">
          <h2 class="card-type-heading" id="type-{type}">{typeSectionHeading(type)}</h2>
          <ul class="card-list">
            {#each sectionCards as card}
              <CardListItem
                {card}
                imageSrc="{assetPrefix}{card.image}"
                view={$viewPreference}
              />
            {/each}
          </ul>
        </section>
      {/if}
    {/each}
    <CardLightbox />
  </div>
</FactionPageLayout>
