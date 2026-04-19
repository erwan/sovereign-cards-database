<script lang="ts">
  import SiteGitHubLink from '$lib/components/SiteGitHubLink.svelte';
  import { base } from '$app/paths';

  let { data } = $props();
</script>

<svelte:head>
  <title>Sovereign Cards Database</title>
</svelte:head>

<main class="home">
  <div class="home-header">
    <h1>Sovereign: Fall of Wormwood</h1>
    <SiteGitHubLink />
  </div>
  <p class="lede">Cards database by faction. Choose a deck to browse card names and types.</p>
  <ul class="deck-grid">
    {#each data.decks as deck}
      <li>
        <a class="deck-link" href="{base}/factions/{deck.slug}">
          <img
            class="deck-cover"
            src="{base}/cards/{deck.slug}/cover.jpg"
            alt={deck.displayName}
            width="280"
            height="392"
            loading="lazy"
          />
        </a>
      </li>
    {/each}
  </ul>
  <div class="global-cta">
    <a class="cta-button" href="{base}/cards">Browse All Cards</a>
    <p class="cta-description">Search and filter cards across all factions</p>
  </div>
</main>
