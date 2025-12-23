'use server';

/**
 * @fileOverview Recognizes a pill from an image and provides information about it.
 *
 * - recognizePillFromImage - A function that handles the pill recognition process.
 * - RecognizePillFromImageInput - The input type for the recognizePillFromImage function.
 * - RecognizePillFromImageOutput - The return type for the recognizePillFromImage function.
 */

import { ai } from '@/ai/genkit';
import { z } from 'genkit';

const RecognizePillFromImageInputSchema = z.object({
  photoDataUri: z
    .string()
    .describe(
      "A photo of a pill, as a data URI that must include a MIME type and use Base64 encoding. Expected format: 'data:<mimetype>;base64,<encoded_data>'."
    ),
});
export type RecognizePillFromImageInput = z.infer<typeof RecognizePillFromImageInputSchema>;

const PillInfoSchema = z.object({
  pillName: z.string().describe('The name of the pill.'),
  box: z.array(z.number()).describe('Bounding box coordinates [x1, y1, x2, y2]'),
});

const RecognizePillFromImageOutputSchema = z.object({
  pills: z.array(PillInfoSchema).describe('An array of detected pills from the image.')
});
export type RecognizePillFromImageOutput = z.infer<typeof RecognizePillFromImageOutputSchema>;

export async function recognizePillFromImage(input: RecognizePillFromImageInput): Promise<RecognizePillFromImageOutput> {
  return recognizePillFromImageFlow(input);
}

const prompt = ai.definePrompt({
  name: 'recognizePillFromImagePrompt',
  input: { schema: RecognizePillFromImageInputSchema },
  output: { schema: RecognizePillFromImageOutputSchema },
  prompt: `You are an AI assistant specialized in identifying one or more pills from an image and providing relevant information for each.

  Analyze the provided image and for each pill you identify, extract the following information:
  - Pill Name: The name of the pill. If multiple pills are visible, identify each one.

  Provide the information in a structured format as an array of detected pills.

  Image: {{media url=photoDataUri}}`,
});

const recognizePillFromImageFlow = ai.defineFlow(
  {
    name: 'recognizePillFromImageFlow',
    inputSchema: RecognizePillFromImageInputSchema,
    outputSchema: RecognizePillFromImageOutputSchema,
  },
  async input => {
    const { output } = await prompt(input);
    return output!;
  }
);
