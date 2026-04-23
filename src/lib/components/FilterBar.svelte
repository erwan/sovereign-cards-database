<script lang="ts">
  import type { CardEntry } from '$lib/decks-content';
  import StatFilter from './StatFilter.svelte';

  interface Filters {
    search: string;
    costs: string[];
    type: string;
    secondaryType: string;
    health: string[];
    attack: string[];
    armor: string[];
  }

  interface Props {
    filters: Filters;
    allCards?: CardEntry[];
    validSecondaryTypesByType?: Record<string, string[]>;
    searchPlaceholder?: string;
  }

  let {
    filters = $bindable(),
    allCards = [],
    validSecondaryTypesByType = {},
    searchPlaceholder = 'Search cards...',
  }: Props = $props();

  function getAvailableCosts(): string[] {
    if (!allCards.length) return ['0', '1', '2', '3', '4', '5', '6', '7', 'X'];
    const costsSet = new Set<string>();
    for (const card of allCards) {
      if (!card.cost) continue;
      if (filters.type && card.type !== filters.type) continue;
      if (filters.secondaryType) {
        const types = (card as CardEntry).type_secondary ?? [];
        if (types.length > 0 && !types.includes(filters.secondaryType)) continue;
      }
      costsSet.add(String(card.cost));
    }
    const costs = [...costsSet];
    costs.sort((a, b) => {
      const oa = a === 'X' ? 10 : parseInt(a, 10);
      const ob = b === 'X' ? 10 : parseInt(b, 10);
      return oa - ob;
    });
    return costs.length > 0 ? costs : ['0', '1', '2', '3', '4', '5', '6', '7', 'X'];
  }

  function getAvailableSecondaryTypes(): string[] {
    return validSecondaryTypesByType[filters.type] ?? validSecondaryTypesByType[''] ?? [];
  }

  function getAvailableStats(field: 'health' | 'attack' | 'armor'): string[] {
    if (!allCards.length) return ['0', '1', '2', '3', '4', '5', '6', '7', '8'];
    const statsSet = new Set<string>();
    for (const card of allCards) {
      if (card.type !== 'unit') continue;
      const val = card[field];
      if (val === undefined || val === null) continue;
      statsSet.add(String(val));
    }
    const stats = [...statsSet];
    stats.sort((a, b) => parseInt(a) - parseInt(b));
    return stats.length > 0 ? stats : ['0', '1', '2', '3', '4', '5', '6', '7', '8'];
  }

  let availableCosts = $derived(getAvailableCosts());
  let availableSecondaryTypes = $derived(getAvailableSecondaryTypes());
  let availableHealth = $derived(getAvailableStats('health'));
  let availableAttack = $derived(getAvailableStats('attack'));
  let availableArmor = $derived(getAvailableStats('armor'));

  let hasActiveFilters = $derived(
    !!(
      filters.search ||
      filters.costs.length > 0 ||
      filters.type ||
      filters.secondaryType ||
      filters.health.length > 0 ||
      filters.attack.length > 0 ||
      filters.armor.length > 0
    )
  );

  let showUnitFilters = $derived(filters.type === 'unit');

  $effect(() => {
    // Clear invalid costs when type/secondaryType changes
    const available = availableCosts;
    const invalid = filters.costs.filter((c) => !available.includes(c));
    if (invalid.length > 0) {
      filters.costs = filters.costs.filter((c) => available.includes(c));
    }
  });

  $effect(() => {
    // Clear secondary type if not valid for current primary type
    if (filters.type && filters.secondaryType) {
      const available = availableSecondaryTypes;
      if (!available.includes(filters.secondaryType)) {
        filters.secondaryType = '';
      }
    }
  });

  $effect(() => {
    // Clear unit-specific filters when type changes away from 'unit'
    if (filters.type !== 'unit') {
      filters.health = [];
      filters.attack = [];
      filters.armor = [];
    }
  });

  function clearFilters() {
    filters.search = '';
    filters.costs = [];
    filters.type = '';
    filters.secondaryType = '';
    filters.health = [];
    filters.attack = [];
    filters.armor = [];
  }
</script>

<div class="filter-bar">
  <div class="filter-group filter-group--search">
    <label for="search" class="filter-label">Search</label>
    <div class="filter-search-wrap">
      <input
        type="text"
        id="search"
        bind:value={filters.search}
        placeholder={searchPlaceholder}
        class="filter-input filter-input--search"
        autocomplete="off"
      />
      {#if filters.search.length > 0}
        <button
          type="button"
          class="filter-search-clear"
          onclick={() => (filters.search = '')}
          aria-label="Clear search"
        >
          <span aria-hidden="true">×</span>
        </button>
      {/if}
    </div>
  </div>

  <div class="filter-group filter-group--cost">
    <StatFilter
      label="Cost"
      bind:values={filters.costs}
      availableOptions={availableCosts}
      allLabel="All costs"
      sortNumeric={true}
    />
  </div>

  <div class="filter-group">
    <label for="type" class="filter-label">Type</label>
    <select bind:value={filters.type} id="type" class="filter-select">
      <option value="">Any Type</option>
      <option value="unit">Unit</option>
      <option value="colony">Colony</option>
      <option value="augment">Augment</option>
      <option value="reflex">Reflex</option>
    </select>
  </div>

  <div class="filter-group">
    <label for="secondaryType" class="filter-label">Secondary Type</label>
    <select
      bind:value={filters.secondaryType}
      id="secondaryType"
      class="filter-select"
      disabled={filters.type === 'reflex' || availableSecondaryTypes.length === 0}
    >
      <option value="">Any Secondary</option>
      {#each availableSecondaryTypes as st}
        <option value={st}>{st.charAt(0).toUpperCase() + st.slice(1)}</option>
      {/each}
    </select>
  </div>

  <div class="filter-group filter-group--actions">
    <span class="filter-label filter-label--spacer" aria-hidden="true">&nbsp;</span>
    <button
      type="button"
      onclick={clearFilters}
      class="filter-btn filter-btn--clear"
      disabled={!hasActiveFilters}
    >
      Clear Filters
    </button>
  </div>

  <div class="filter-group filter-group--break" aria-hidden="true"></div>

  {#if showUnitFilters}
    <div class="filter-group filter-group--unit-stats">
      <StatFilter
        label="Health"
        bind:values={filters.health}
        availableOptions={availableHealth}
        allLabel="All health"
        sortNumeric={true}
      />
    </div>

    <div class="filter-group filter-group--unit-stats">
      <StatFilter
        label="Attack"
        bind:values={filters.attack}
        availableOptions={availableAttack}
        allLabel="All attack"
        sortNumeric={true}
      />
    </div>

    <div class="filter-group filter-group--unit-stats">
      <StatFilter
        label="Armor"
        bind:values={filters.armor}
        availableOptions={availableArmor}
        allLabel="All armor"
        sortNumeric={true}
      />
    </div>
  {/if}
</div>