<script lang="ts">
  import SiteGitHubLink from './SiteGitHubLink.svelte';
  import { resolve } from '$app/paths';
  import type { Snippet } from 'svelte';

  let { children, headerActions }: { children: Snippet; headerActions?: Snippet } = $props();
</script>

<main class="faction-main">
  <div class="faction-header">
    <div class="faction-header-start">
      <nav class="faction-nav">
        <a href={resolve('/')}>← Home</a>
      </nav>
      {#if headerActions}
        {@render headerActions()}
      {/if}
    </div>
    <SiteGitHubLink />
  </div>
  {@render children()}
</main>
