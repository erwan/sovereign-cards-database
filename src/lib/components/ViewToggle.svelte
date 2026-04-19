<script lang="ts">
  import { viewPreference } from '$lib/stores';
</script>

<div class="deck-view-toolbar" role="group" aria-label="Display mode">
  <div class="deck-view-switch" role="presentation">
    <input
      type="radio"
      class="deck-view-input"
      name="deck-view-mode"
      id="deck-view-list"
      value="list"
      checked={$viewPreference === 'list'}
      onchange={() => viewPreference.set('list')}
    />
    <label class="deck-view-option" for="deck-view-list">List</label>
    <input
      type="radio"
      class="deck-view-input"
      name="deck-view-mode"
      id="deck-view-gallery"
      value="gallery"
      checked={$viewPreference === 'gallery'}
      onchange={() => viewPreference.set('gallery')}
    />
    <label class="deck-view-option" for="deck-view-gallery">Cards</label>
  </div>
</div>
