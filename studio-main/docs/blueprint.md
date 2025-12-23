# **App Name**: PillPal

## Core Features:

- Pill Recognition: Upload a photo of a pill, and an AI model identifies the pill, providing information like name, purpose, contraindications, and active ingredients.
- Food Alternative Suggestion Tool: Based on the pill's active ingredients, the application will suggest food alternatives. The user can tap on an ingredient to see a detailed list of food options. Powered by a reasoning tool for deciding how to present options to the user.
- Pill Information Display: Display all information about the pill, including name, purpose/efficacy, contraindicated drugs, and active ingredients, in a clean, user-friendly list format.
- Daily Medication Tracking: Implement a system to track daily medication intake with slots for morning, noon, and evening.  Include individual check buttons for each slot, as well as a 'check all' option.
- Medication Period Setting: Allow users to set the start and end dates for their medication schedule.
- Reminder Notifications: Show reminder popups for each intake time (morning, noon, evening) to notify the user to take their medication.
- Image Upload Endpoint: FastAPI endpoint to handle image uploads for AI inference. Manages AI inference and returns data.

## Style Guidelines:

- Primary color: Light blue (#7EC8E3) to convey a sense of calm and health.
- Background color: Very light blue (#E0F7FA), a heavily desaturated version of the primary.
- Accent color: A light green (#90EE90), for positive confirmations such as marking a dose as taken, creating visual contrast, and an association with health and nature.
- Body and headline font: 'PT Sans', a humanist sans-serif, for a balance of modern readability and approachability.
- Use clear and easily recognizable icons for medication times, settings, and food alternatives.
- Design a responsive layout that adapts to various screen sizes for mobile web use.
- Use subtle animations for transitions and interactions, such as marking a dose as taken or displaying food alternative information.