<script lang="ts">
  import SiteGitHubLink from '$lib/components/SiteGitHubLink.svelte';
  import { asset, resolve } from '$app/paths';
  import type { Asset } from '$app/types';

  let { data } = $props();
</script>

<svelte:head>
  <title>Sovereign Cards Database</title>
  <link rel="preload" as="image" href={asset(`/cards/${data.decks[0].slug}/cover.jpg` as Asset)} />
</svelte:head>

<main class="home">
  <div class="home-header">
    <h1>Sovereign: Fall of Wormwood</h1>
    <SiteGitHubLink />
  </div>
  <p class="lede">Cards database by faction. Choose a deck to browse card names and types.</p>
  <ul class="deck-grid">
    {#each data.decks as deck, i}
      <li>
        <a class="deck-link" href={resolve(`/factions/${deck.slug}`)}>
          <img
            class="deck-cover"
            src={asset(`/cards/${deck.slug}/cover.jpg` as Asset)}
            alt={deck.displayName}
            width="280"
            height="392"
            fetchpriority={i === 0 ? 'high' : undefined}
          />
        </a>
      </li>
    {/each}
  </ul>
  <div class="global-cta">
    <a class="cta-button" href={resolve('/cards')}>Browse All Cards</a>
    <p class="cta-description">Search and filter cards across all factions</p>
  </div>
</main>
