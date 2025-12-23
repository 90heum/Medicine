'use server';

/**
 * @fileOverview Suggests food alternatives based on the pill's active ingredients.
 *
 * - suggestFoodAlternatives - A function that suggests food alternatives.
 * - SuggestFoodAlternativesInput - The input type for the suggestFoodAlternatives function.
 * - SuggestFoodAlternativesOutput - The return type for the suggestFoodAlternatives function.
 */

import { ai } from '@/ai/genkit';
import { z } from 'genkit';

const SuggestFoodAlternativesInputSchema = z.object({
  pillName: z.string().describe('The name of the pill.'),
});
export type SuggestFoodAlternativesInput = z.infer<
  typeof SuggestFoodAlternativesInputSchema
>;

const FoodAlternativeSchema = z.object({
  ingredient: z.string().describe('The active ingredient.'),
  foods: z.array(z.string()).describe('A list of food alternatives for the ingredient.'),
});

const SuggestFoodAlternativesOutputSchema = z.object({
  purpose: z.string().describe('The purpose or efficacy of the pill.'),
  foodAlternatives: z
    .array(FoodAlternativeSchema)
    .describe(
      'An array of objects, where each object contains an active ingredient and its corresponding food alternatives.'
    ),
  reasoning: z.string().describe('The reasoning behind the suggestions.'),
});
export type SuggestFoodAlternativesOutput = z.infer<
  typeof SuggestFoodAlternativesOutputSchema
>;

export async function suggestFoodAlternatives(
  input: SuggestFoodAlternativesInput
): Promise<SuggestFoodAlternativesOutput> {
  return suggestFoodAlternativesFlow(input);
}

const prompt = ai.definePrompt({
  name: 'suggestFoodAlternativesPrompt',
  input: { schema: SuggestFoodAlternativesInputSchema },
  output: { schema: SuggestFoodAlternativesOutputSchema },
  prompt: `당신은 알약의 활성 성분을 기반으로 음식 대체재를 제안하는 영양사입니다.
  또한 알약의 복용 목적도 설명해줍니다.

  주어진 알약 이름을 바탕으로, 먼저 그 알약의 주요 목적과 활성 성분을 파악하세요.
  그 후, 각 활성 성분을 대체할 수 있는 음식을 제안하세요.

  알약 이름: {{pillName}}

  반드시 한국어로 답변해 주세요.
  응답 형식은 다음 세 가지 필드를 가진 JSON 객체여야 합니다: purpose, foodAlternatives, reasoning.

  foodAlternatives 필드는 객체들의 배열이어야 하며, 각 객체는 다음 두 필드를 가져야 합니다:
  - "ingredient": 활성 성분 이름 (예: "Ibuprofen").
  - "foods": 음식 대체재들의 배열 (예: ["강황", "생강"]).

  reasoning 필드에는 제안의 근거를 설명하세요.
  `,
  // 당신은 영양사이며, 알약의 활성 성분을 기반으로 음식 대체재를 제안합니다.
  // 또한 알약의 목적도 함께 제공합니다.

  // 다음 알약 이름이 주어졌을 때, 먼저 해당 알약의 주요 목적과 활성 성분을 식별하세요.
  // 그런 다음 각 활성 성분에 대한 음식 대체재를 제안하세요.

  // Pill Name: {{pillName}}

  // 응답 형식은 JSON 객체여야 하며, 다음 세 가지 필드를 포함해야 합니다:
  // - purpose
  // - foodAlternatives
  // - reasoning

  // foodAlternatives 필드는 객체들의 배열이어야 합니다.  
  // 각 객체는 아래 두 가지 필드를 반드시 포함해야 합니다:
  // - "ingredient": 활성 성분의 이름 (예: "Ibuprofen")
  // - "foods": 해당 성분을 대체할 수 있는 음식들의 문자열 배열 (예: ["Turmeric", "Ginger"])

  // reasoning 필드에는 제안한 음식 선택의 논리적 근거를 설명해야 합니다.

});

const suggestFoodAlternativesFlow = ai.defineFlow(
  {
    name: 'suggestFoodAlternativesFlow',
    inputSchema: SuggestFoodAlternativesInputSchema,
    outputSchema: SuggestFoodAlternativesOutputSchema,
  },
  async input => {
    const { output } = await prompt(input);
    return output!;
  }
);
