<script lang="ts">
  import type { CardEntry } from '$lib/decks-content';

  interface Filters {
    search: string;
    costs: string[];
    type: string;
    secondaryType: string;
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

  let costDropdownOpen = $state(false);

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

  let availableCosts = $derived(getAvailableCosts());
  let availableSecondaryTypes = $derived(getAvailableSecondaryTypes());

  let costTriggerLabel = $derived(
    filters.costs.length === 0
      ? 'All costs'
      : [...filters.costs]
          .sort((a, b) => (a === 'X' ? 10 : parseInt(a)) - (b === 'X' ? 10 : parseInt(b)))
          .join(', ')
  );

  let hasActiveFilters = $derived(
    !!(filters.search || filters.costs.length > 0 || filters.type || filters.secondaryType)
  );

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

  function closeCostDropdown(e: FocusEvent) {
    if (!(e.currentTarget as HTMLElement).contains(e.relatedTarget as Node)) {
      costDropdownOpen = false;
    }
  }

  function handleCostKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') costDropdownOpen = false;
  }

  function setOnlyCost(cv: string) {
    filters.costs = [cv];
  }

  function clearCostSelection() {
    filters.costs = [];
  }

  function clearFilters() {
    filters.search = '';
    filters.costs = [];
    filters.type = '';
    filters.secondaryType = '';
  }
</script>

<svelte:window onkeydown={handleCostKeydown} />

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
    <span class="filter-label" id="filter-cost-heading">Cost</span>
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div
      class="filter-cost-dropdown"
      onfocusout={closeCostDropdown}
    >
      <button
        type="button"
        class="filter-cost-trigger"
        aria-haspopup="true"
        aria-expanded={costDropdownOpen}
        aria-label="Filter by cost, current: {costTriggerLabel}"
        onclick={() => (costDropdownOpen = !costDropdownOpen)}
      >
        <span class="filter-cost-trigger-text">{costTriggerLabel}</span>
        <span class="filter-cost-trigger-chevron" aria-hidden="true"></span>
      </button>
      {#if costDropdownOpen}
        <div class="filter-cost-panel" role="group" aria-label="Cost values">
          {#each availableCosts as cv}
            <div class="filter-cost-option">
              <label class="filter-cost-option-check">
                <input
                  type="checkbox"
                  value={cv}
                  bind:group={filters.costs}
                />
                <span class="filter-cost-option-label">{cv}</span>
              </label>
              <button
                type="button"
                class="filter-cost-only-btn"
                onclick={() => setOnlyCost(cv)}
                aria-label="Show only cost {cv}"
              >
                Only
              </button>
            </div>
          {/each}
          <div class="filter-cost-panel-footer">
            <button type="button" class="filter-cost-foot-btn" onclick={clearCostSelection}>
              Clear
            </button>
          </div>
        </div>
      {/if}
    </div>
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
</div>
