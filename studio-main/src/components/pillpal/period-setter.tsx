"use client";

import * as React from "react";
import { format } from "date-fns";
import { Calendar as CalendarIcon } from "lucide-react";
import { DateRange } from "react-day-picker";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Label } from "../ui/label";

export function PeriodSetter({ onDateChange }: { onDateChange: (date: DateRange | undefined) => void }) {
  const [date, setDate] = React.useState<DateRange | undefined>({
    from: new Date(),
    to: undefined,
  });

  const handleFromDateSelect = (selectedDate: Date | undefined) => {
    setDate(prev => {
      const newFrom = selectedDate;
      const currentTo = prev?.to;
      // if 'from' date is after 'to' date, reset 'to' date
      if (newFrom && currentTo && newFrom > currentTo) {
        return { from: newFrom, to: undefined };
      }
      return { from: newFrom, to: currentTo };
    });
  }

  React.useEffect(() => {
    onDateChange(date);
  }, [date, onDateChange]);

  return (
    <>
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="grid gap-2">
          <Label htmlFor="date-from">시작일</Label>
          <Popover>
            <PopoverTrigger asChild>
              <Button
                id="date-from"
                variant={"outline"}
                className={cn(
                  "w-full justify-start text-left font-bold bg-card",
                  !date?.from && "text-muted-foreground"
                )}
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {date?.from ? (
                  format(date.from, "LLL dd, y")
                ) : (
                  <span>Pick a date</span>
                )}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar
                initialFocus
                mode="single"
                selected={date?.from}
                onSelect={handleFromDateSelect}
                disabled={{ before: new Date() }}
                numberOfMonths={1}
              />
            </PopoverContent>
          </Popover>
        </div>
        <div className="grid gap-2">
          <Label htmlFor="date-to">종료일</Label>
          <Popover>
            <PopoverTrigger asChild>
              <Button
                id="date-to"
                variant={"outline"}
                className={cn(
                  "w-full justify-start text-left font-bold bg-card",
                  !date?.to && "text-muted-foreground"
                )}
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {date?.to ? (
                  format(date.to, "LLL dd, y")
                ) : (
                  <span>날짜를 선택해주세요.</span>
                )}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar
                initialFocus
                mode="single"
                selected={date?.to}
                onSelect={(d) => setDate(prev => ({ from: prev?.from, to: d }))}
                disabled={{ before: date?.from || new Date() }}
                numberOfMonths={1}
              />
            </PopoverContent>
          </Popover>
        </div>
      </div>
    </>
  );
}
