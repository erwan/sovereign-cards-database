<script lang="ts">
  import '@fontsource/lato/latin-400.css';
  import '@fontsource/lato/latin-700.css';
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
