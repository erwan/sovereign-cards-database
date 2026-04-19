<script lang="ts">
  import '../styles/global.css';
  import '../styles/faction-layout.css';
  import '../styles/faction-detail.css';
  import '../styles/filter-bar.css';
  import '../styles/home.css';
  import type { Snippet } from 'svelte';

  let { children }: { children: Snippet } = $props();
</script>

<svelte:head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="" />
  <link
    href="https://fonts.googleapis.com/css2?family=Lato:wght@400;600;700&display=swap"
    rel="stylesheet"
  />
</svelte:head>

{@render children()}

<footer class="site-footer">
  <p>
    This is a non-official, fan-made website. All rights to Sovereign: Fall of Wormwood belong to
    <a href="https://www.fallofwormwood.com/" target="_blank" rel="noopener noreferrer">
      Ixion Gameworks
    </a>.
  </p>
</footer>
