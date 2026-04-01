import { defineCollection } from "astro:content";
import { DeckSchema } from "./decks/schema";

export const collections = {
  decks: defineCollection({
    type: "content",
    schema: DeckSchema,
  }),
};