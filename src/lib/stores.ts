import { writable } from 'svelte/store';
import { browser } from '$app/environment';

function viewStore() {
  const saved = browser ? localStorage.getItem('sovereign-deck-display') : null;
  const initial: 'list' | 'gallery' = saved === 'list' ? 'list' : 'gallery';
  const { subscribe, set } = writable<'list' | 'gallery'>(initial);
  return {
    subscribe,
    set(v: 'list' | 'gallery') {
      if (browser) localStorage.setItem('sovereign-deck-display', v);
      set(v);
    },
  };
}

export const viewPreference = viewStore();

export const lightbox = writable<{ src: string; name: string } | null>(null);
