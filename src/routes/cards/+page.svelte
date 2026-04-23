<script lang="ts">
  import CardLightbox from '$lib/components/CardLightbox.svelte';
  import CardList from '$lib/components/CardList.svelte';
  import FactionPageLayout from '$lib/components/FactionPageLayout.svelte';
  import FilterBar from '$lib/components/FilterBar.svelte';
  import ViewToggle from '$lib/components/ViewToggle.svelte';
  import { compareCardsByCostThenName, compareCardsByNameThenCost, cardBlockTypeLabel } from '$lib/decks-content';
  import { viewPreference } from '$lib/stores';
  import { browser } from '$app/environment';
  import { base } from '$app/paths';
  import type { CardWithFaction } from './+page.server';

  let { data } = $props();

  let filters = $state({
    search: '',
    titleOnly: false,
    costs: [] as string[],
    type: '',
    secondaryType: '',
    health: [] as string[],
    attack: [] as string[],
    armor: [] as string[],
    keyword: [] as string[],
  });

  let sortBy = $state<'cost' | 'name'>(
    browser ? ((localStorage.getItem('sovereign-cards-sort') === 'name' ? 'name' : 'cost')) : 'cost'
  );

  $effect(() => {
    if (browser) localStorage.setItem('sovereign-cards-sort', sortBy);
  });

  let filteredCards = $derived.by(() => {
    const { search, titleOnly, costs, type, secondaryType, health, attack, armor, keyword } = filters;
    let result = data.allCards.filter((card: CardWithFaction) => {
      if (search) {
        const nameMatch = card.name.toLowerCase().includes(search.toLowerCase());
        const effectMatch = card.card_effect?.toLowerCase().includes(search.toLowerCase());
        if (!titleOnly ? (!nameMatch && !effectMatch) : !nameMatch) return false;
      }
      if (costs.length > 0 && !costs.includes(String(card.cost))) return false;
      if (type && card.type !== type) return false;
      if (secondaryType && !card.type_secondary?.includes(secondaryType)) return false;
      if (type === 'unit') {
        if (keyword.length > 0 && !keyword.some(k => card.card_effect?.toLowerCase().includes(k.toLowerCase()))) return false;
        if (health.length > 0 && !(card.health !== undefined && health.includes(String(card.health)))) return false;
        if (attack.length > 0 && !(card.attack !== undefined && attack.includes(String(card.attack)))) return false;
        if (armor.length > 0 && !(card.armor !== undefined && armor.includes(String(card.armor)))) return false;
      }
      return true;
    });

    const cmp = sortBy === 'name' ? compareCardsByNameThenCost : compareCardsByCostThenName;
    return [...result].sort(cmp);
  });

  function fullTypeLabel(card: CardWithFaction): string {
    const secondary = cardBlockTypeLabel(card);
    return secondary ? `${card.type} — ${secondary}` : card.type;
  }
</script>

<svelte:head>
  <title>All Cards | Sovereign Cards Database</title>
</svelte:head>

<FactionPageLayout>
  {#snippet headerActions()}
    <ViewToggle />
  {/snippet}

  <header class="page-header">
    <h1>All Cards</h1>
    <p class="page-subtitle">Browse and filter cards from all factions</p>
  </header>

  <FilterBar
    bind:filters
    allCards={data.allCards}
    validSecondaryTypesByType={data.validSecondaryTypesByType}
  />

  <div class="faction-detail all-cards-detail" data-deck-view={$viewPreference}>
    <CardList
      cards={filteredCards}
      totalCount={data.allCards.length}
      bind:sortBy
      view={$viewPreference}
      getImageSrc={(card: CardWithFaction) => `${base}/cards/${card.factionSlug}/${card.image}`}
      getTypeLabel={fullTypeLabel}
    />
    <CardLightbox />
  </div>
</FactionPageLayout>

<style>
  .page-header {
    margin-bottom: 1.25rem;
    text-align: left;
  }

  .page-header h1,
  .page-subtitle {
    font-size: clamp(1.5rem, 2.5vw, 1.85rem);
    line-height: 1.35;
  }

  .page-header h1 {
    font-weight: 600;
    margin: 0 0 0.35rem 0;
    color: var(--text-primary);
  }

  .page-subtitle {
    margin: 0;
    font-weight: 400;
    color: var(--text-muted);
  }
</style>
