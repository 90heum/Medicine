"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Calendar } from "@/components/ui/calendar";
import { DateRange } from "react-day-picker";

export function MedicationCalendar({ schedule }: { schedule: DateRange }) {
  return (
    <Card className="shadow-md mt-4">
      <CardContent className="p-4 flex justify-center">
        <Calendar
          mode="range"
          selected={schedule}
          defaultMonth={schedule.from}
          modifiers={{
            // This is a bit of a trick to highlight the range
            // without allowing selection.
            highlighted: { from: schedule.from, to: schedule.to },
          }}
          modifiersClassNames={{
            highlighted: 'bg-primary/20',
          }}
          // The calendar is for display only
          onSelect={() => {}}
        />
      </CardContent>
    </Card>
  );
}
