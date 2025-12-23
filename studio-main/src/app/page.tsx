"use client";

import { PillRecognizer } from "@/components/pillpal/pill-recognizer";
import { MedicationTracker } from "@/components/pillpal/medication-tracker";
import { PeriodSetter } from "@/components/pillpal/period-setter";
import { ReminderHandler } from "@/components/pillpal/reminder-handler";
import { MedicationCalendar } from "@/components/pillpal/medication-calendar";
import { Pill } from 'lucide-react';
import { useState } from "react";
import { DateRange } from "react-day-picker";
import { NextDoseCountdown } from "@/components/pillpal/next-dose-countdown";

export default function Home() {
  const [schedule, setSchedule] = useState<DateRange | undefined>(undefined);
  const [showCalendar, setShowCalendar] = useState(false);
  const [tempSchedule, setTempSchedule] = useState<DateRange | undefined>(undefined);
  const [reminderTrigger, setReminderTrigger] = useState(0);

  const handleSaveSchedule = () => {
    setSchedule(tempSchedule);
    setShowCalendar(true);
  };

  const handleReminder = () => {
    setReminderTrigger(prev => prev + 1);
  };

  return (
    <>
      <div className="flex flex-col items-center min-h-screen p-4 sm:p-6 md:p-8">
        <main className="w-full max-w-md mx-auto flex flex-col gap-8">
          <header className="flex flex-col items-center text-center">
            <div className="bg-primary/20 p-3 rounded-full mb-4">
              <Pill className="w-8 h-8 text-primary" />
            </div>
            <h1 className="text-4xl font-bold font-headline text-foreground">
              복약 도우미
            </h1>
            <p className="text-muted-foreground mt-2">
              당신만을 위한 개인 복약 안내 도우미.
            </p>
          </header>

          <PillRecognizer reminderTrigger={reminderTrigger} />

          <div className="w-full space-y-8">
            <NextDoseCountdown />
            <ReminderHandler onReminder={handleReminder} />
            <div>
              <h2 className="text-2xl font-bold font-headline mb-4">복약 일정</h2>
              <PeriodSetter onDateChange={setTempSchedule} />
              <MedicationTracker onSave={handleSaveSchedule} />
              {showCalendar && schedule && <MedicationCalendar schedule={schedule} />}
            </div>
          </div>

        </main>
      </div>
    </>
  );
}
