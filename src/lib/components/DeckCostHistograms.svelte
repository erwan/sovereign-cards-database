<script lang="ts">
  import { buildCostHistogram, DISPLAY_TYPE_ORDER, typeSectionHeading, type CardEntry, type Deck } from '$lib/decks-content';

  let { deck }: { deck: Deck } = $props();

  const sections = DISPLAY_TYPE_ORDER.map((type) => {
    const cards = deck.cards.filter((c: CardEntry) => c.type === type);
    if (cards.length === 0) return null;
    const { bins } = buildCostHistogram(cards);
    const title = `${typeSectionHeading(type)} (${cards.length})`;
    const summary = bins
      .filter((b) => b.count > 0)
      .map((b) => `${b.count} at cost ${b.label}`)
      .join(', ');
    return { type, title, bins, summary };
  }).filter((row): row is NonNullable<typeof row> => row !== null);

  const histogramScaleMax = Math.max(
    1,
    ...sections.flatMap((s) => s.bins.map((b) => b.count))
  );
</script>

{#if sections.length > 0}
  <section class="deck-cost-histograms" aria-labelledby="deck-cost-histograms-heading">
    <details class="deck-cost-histograms-details" open>
      <summary class="deck-cost-histograms-summary">
        <span id="deck-cost-histograms-heading" class="deck-cost-histograms-heading">
          Deck Statistics
        </span>
      </summary>
      <div class="deck-cost-histograms-grid">
        {#each sections as { type, title, bins, summary }}
          <div class="deck-histogram">
            <div class="deck-histogram-chart" role="img" aria-label="{title}: {summary}">
              <div class="deck-histogram-bars">
                {#each bins as bin}
                  {@const stackFill = bin.count / histogramScaleMax}
                  {@const valueTip = `${bin.count} ${bin.count === 1 ? 'card' : 'cards'} at cost ${bin.label}`}
                  <div class="deck-histogram-cell" title={valueTip}>
                    <div class="deck-histogram-bar-track" aria-hidden="true">
                      <div class="deck-histogram-bar-stack" style="--stack-fill: {stackFill}; --count: {bin.count}"></div>
                    </div>
                    <span class="deck-histogram-axis-label">{bin.label}</span>
                  </div>
                {/each}
              </div>
            </div>
            <h3 class="deck-histogram-title">
              <a href="#type-{type}">{title}</a>
            </h3>
          </div>
        {/each}
      </div>
    </details>
  </section>
{/if}
