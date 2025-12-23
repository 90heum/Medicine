"use client";

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlarmClock } from 'lucide-react';

// Corresponds to 8am, 12pm, 6pm
const DOSE_TIMES_IN_HOURS = [8, 12, 18];

const getNextDoseDate = (now: Date) => {
    for (const hour of DOSE_TIMES_IN_HOURS) {
        const doseTime = new Date(now);
        doseTime.setHours(hour, 0, 0, 0);
        if (doseTime.getTime() > now.getTime()) {
            return doseTime;
        }
    }
    // If all doses for today are past, return the first dose of tomorrow
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(DOSE_TIMES_IN_HOURS[0], 0, 0, 0);
    return tomorrow;
};

const formatTimeLeft = (milliseconds: number) => {
    if (milliseconds <= 0) return "00:00:00";

    const totalSeconds = Math.floor(milliseconds / 1000);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    const pad = (num: number) => num.toString().padStart(2, '0');

    return `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
};


export function NextDoseCountdown() {
    const [nextDose, setNextDose] = useState<Date | null>(null);
    const [timeLeft, setTimeLeft] = useState<number>(0);

    useEffect(() => {
        // This effect runs once on mount to set the initial next dose time.
        // It should only run on the client.
        const now = new Date();
        setNextDose(getNextDoseDate(now));
    }, []);

    useEffect(() => {
        // This effect runs when `nextDose` changes and sets up the interval.
        if (!nextDose) return;

        const calculateTimeLeft = () => {
            const now = new Date();
            const difference = nextDose.getTime() - now.getTime();
            setTimeLeft(difference);

            // If the time is up, find the next dose time
            if (difference <= 0) {
                setNextDose(getNextDoseDate(now));
            }
        };

        calculateTimeLeft(); // Initial calculation
        const timer = setInterval(calculateTimeLeft, 1000);

        return () => clearInterval(timer);
    }, [nextDose]);

    return (
        <Card className="shadow-md">
            <CardHeader className="p-4">
                <CardTitle className="flex items-center gap-2 font-headline text-lg">
                    <AlarmClock className="w-5 h-5 text-primary" />
                    다음 복용까지 남은 시간
                </CardTitle>
            </CardHeader>
            <CardContent className="p-4 pt-0 text-center">
                {timeLeft > 0 ? (
                    <div className="text-4xl font-bold font-mono tracking-widest text-foreground">
                        {formatTimeLeft(timeLeft)}
                    </div>
                ) : (
                    <div className="text-2xl font-bold text-accent animate-pulse">
                        복용 시간입니다!
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
