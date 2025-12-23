'use server';

import { RecognizePillFromImageOutput } from '@/ai/flows/pill-recognition-from-image';
import { suggestFoodAlternatives as suggestFoodAlternativesFlow, SuggestFoodAlternativesOutput } from '@/ai/flows/suggest-food-alternatives';

const FASTAPI_ENDPOINT = "http://localhost:8000/predict"; // FastAPI 서버 주소/엔드포인트

// Mocked AI pill recognition
async function recognizePillFromImageFlow(input: { photoDataUri: string }): Promise<RecognizePillFromImageOutput> {

    console.log("Sending request to FastAPI for image inference...");

    try {
        // Data URI parsing
        const matches = input.photoDataUri.match(/^data:([A-Za-z-+\/]+);base64,(.+)$/);

        if (!matches || matches.length !== 3) {
            throw new Error("Invalid data URI format received");
        }

        const mimeType = matches[1];
        const base64Data = matches[2];
        const buffer = Buffer.from(base64Data, 'base64');

        // Create Blob and FormData for upload
        const blob = new Blob([buffer], { type: mimeType });
        const formData = new FormData();
        formData.append("file", blob, "image.jpg");

        // Send request to FastAPI
        const response = await fetch(FASTAPI_ENDPOINT, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorBody = await response.text();
            throw new Error(`FastAPI request failed with status ${response.status}: ${errorBody}`);
        }

        const data = await response.json();

        // Return structured data matching the interface
        console.log("FastAPI Response Data:", JSON.stringify(data, null, 2));
        return {
            pills: data.pills || []
        };

    } catch (error) {
        console.error("Error during pill recognition flow:", error);
        throw error;
    }

}


export async function handlePillRecognition(photoDataUri: string): Promise<RecognizePillFromImageOutput> {
    try {
        const result = await recognizePillFromImageFlow({ photoDataUri });
        return result;
    } catch (error) {
        console.error("Error in pill recognition:", error);
        throw new Error("Failed to recognize pill. Please try again with a clearer image.");
    }
}

export async function getFoodAlternatives(pillName: string): Promise<SuggestFoodAlternativesOutput> {
    try {
        const result = await suggestFoodAlternativesFlow({ pillName });
        return result;
    } catch (error) {
        console.error("Error getting food alternatives:", error);
        throw new Error("Failed to suggest food alternatives.");
    }
}
