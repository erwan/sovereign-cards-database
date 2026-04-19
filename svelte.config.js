import adapter from '@sveltejs/adapter-static';

/** @type {import('@sveltejs/kit').Config} */
export default {
  kit: {
    adapter: adapter({ pages: 'dist', assets: 'dist' }),
    paths: {
      base: process.env.NODE_ENV === 'production' ? '/sovereign-cards-database' : '',
    },
  },
};
