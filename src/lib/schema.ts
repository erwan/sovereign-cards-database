import { z } from "zod";

const CARD_SECONDARY_TYPES = new Set<string>([
  'unknown',
  'antigrav',
  'unit',
  'facility',
  'human',
  'xeno',
  'chimera',
  'aciereys',
  'mech',
  'reflex',
  'synth',
]);

const CARD_TYPES = new Set<string>(['unknown', 'unit', 'reflex', 'augment', 'colony']);

export const CardEntrySchema = z.object({
  image: z.string().min(1),
  name: z.string().min(1),
  type: z.enum([...CARD_TYPES] as [string, ...string[]]),
  cost: z.union([
    z.string().length(1).regex(/^[0-8Xx]$/),
    z.number().int().min(0).max(8).transform(String),
  ]),
  type_secondary: z.array(z.enum([...CARD_SECONDARY_TYPES] as [string, ...string[]])).optional(),
  attack: z.number().int().min(0).optional(),
  armor: z.number().int().min(0).optional(),
  health: z.number().int().min(0).optional(),
  card_effect: z.string().optional(),
});

export const DeckSchema = z.object({
  name: z.string().optional(),
  description: z.string().optional(),
  cards: z.array(CardEntrySchema),
});

export type CardEntry = z.infer<typeof CardEntrySchema>;
export type Deck = z.infer<typeof DeckSchema> & { slug: string; displayName: string };