export const playNotificationSound = () => {
    try {
        const AudioContext = window.AudioContext || (window as any).webkitAudioContext;
        if (!AudioContext) return;

        const ctx = new AudioContext();

        // Function to play a single tone
        const playTone = (freq: number, startTime: number, duration: number) => {
            const oscillator = ctx.createOscillator();
            const gainNode = ctx.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(ctx.destination);

            oscillator.type = 'sine';
            oscillator.frequency.value = freq;

            // Envelope
            gainNode.gain.setValueAtTime(0, startTime);
            gainNode.gain.linearRampToValueAtTime(0.3, startTime + 0.05); // Attack
            gainNode.gain.exponentialRampToValueAtTime(0.01, startTime + duration); // Decay

            oscillator.start(startTime);
            oscillator.stop(startTime + duration);
        };

        const now = ctx.currentTime;
        // --- 첫 번째 연주 ---
        // 1. C5
        playTone(523.25, now, 0.15);

        // 2. E5
        playTone(659.25, now + 0.15, 0.15);

        // 3. G5 (마무리)
        playTone(783.99, now + 0.30, 0.30);

        // --- 두 번째 반복 ---
        // 4. C5 (잠시 후 다시 시작)
        playTone(523.25, now + 0.80, 0.15);

        // 5. G5 (재차 마무리)
        playTone(783.99, now + 0.95, 0.40);

    } catch (e) {
        console.error("Failed to play notification sound", e);
    }
};
