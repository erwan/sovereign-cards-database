<script lang="ts">
  interface Props {
    label: string;
    values: string[];
    availableOptions: string[];
    allLabel?: string;
    sortNumeric?: boolean;
  }

  let {
    label,
    values = $bindable(),
    availableOptions,
    allLabel = 'All',
    sortNumeric = true,
  }: Props = $props();

  let dropdownOpen = $state(false);

  let triggerLabel = $derived(
    values.length === 0
      ? allLabel
      : [...values]
          .sort((a, b) => {
            if (!sortNumeric) return a.localeCompare(b);
            const oa = a === 'X' ? 10 : parseInt(a, 10);
            const ob = b === 'X' ? 10 : parseInt(b, 10);
            return oa - ob;
          })
          .join(', ')
  );

  function closeDropdown(e: FocusEvent) {
    if (!(e.currentTarget as HTMLElement).contains(e.relatedTarget as Node)) {
      dropdownOpen = false;
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') dropdownOpen = false;
  }

  function setOnly(value: string) {
    values = [value];
  }

  function clearSelection() {
    values = [];
  }
</script>

<svelte:window onkeydown={handleKeydown} />

<span class="filter-label" id="filter-{label}-heading">{label}</span>
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
  class="filter-cost-dropdown"
  onfocusout={closeDropdown}
>
  <button
    type="button"
    class="filter-cost-trigger"
    aria-haspopup="true"
    aria-expanded={dropdownOpen}
    aria-label="Filter by {label.toLowerCase()}, current: {triggerLabel}"
    onclick={() => (dropdownOpen = !dropdownOpen)}
  >
    <span class="filter-cost-trigger-text">{triggerLabel}</span>
    <span class="filter-cost-trigger-chevron" aria-hidden="true"></span>
  </button>
  {#if dropdownOpen}
    <div class="filter-cost-panel" role="group" aria-label="{label} values">
      {#each availableOptions as opt}
        <div class="filter-cost-option">
          <label
            class="filter-cost-option-check"
            onmousedown={(e) => e.preventDefault()}
            onclick={(e) => {
              if ((e.target as HTMLElement).tagName === 'INPUT') return;
              e.preventDefault();
              values = values.includes(opt) ? values.filter(v => v !== opt) : [...values, opt];
            }}
          >
            <input
              type="checkbox"
              checked={values.includes(opt)}
              onchange={() => values = values.includes(opt) ? values.filter(v => v !== opt) : [...values, opt]}
            />
            <span class="filter-cost-option-label">{opt}</span>
          </label>
          <button
            type="button"
            class="filter-cost-only-btn"
            onclick={(e) => { e.stopPropagation(); setOnly(opt); }}
            aria-label="Show only {label.toLowerCase()} {opt}"
          >
            Only
          </button>
        </div>
      {/each}
      <div class="filter-cost-panel-footer">
        <button type="button" class="filter-cost-foot-btn" onclick={clearSelection}>
          Clear
        </button>
      </div>
    </div>
  {/if}
</div>