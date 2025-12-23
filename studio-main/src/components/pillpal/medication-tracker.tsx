"use client";

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Check, Sunrise, Sun, Moon, Save } from 'lucide-react';
import { cn } from '@/lib/utils';

type Dose = 'morning' | 'noon' | 'evening';

export function MedicationTracker({ onSave }: { onSave: () => void }) {
  const [takenDoses, setTakenDoses] = useState<Record<Dose, boolean>>({
    morning: false,
    noon: false,
    evening: false,
  });

  const handleTakeDose = (dose: Dose) => {
    setTakenDoses(prev => ({ ...prev, [dose]: !prev[dose] }));
  };

  const allTaken = Object.values(takenDoses).every(Boolean);

  const handleTakeAll = () => {
    setTakenDoses({
      morning: !allTaken,
      noon: !allTaken,
      evening: !allTaken,
    });
  };

  return (
    <Card className="shadow-md mt-4">
      <CardContent className="p-4 space-y-4">
        <div className="grid grid-cols-3 gap-2">
          <DoseButton
            dose="morning"
            icon={<Sunrise />}
            isTaken={takenDoses.morning}
            onToggle={handleTakeDose}
          />
          <DoseButton
            dose="noon"
            icon={<Sun />}
            isTaken={takenDoses.noon}
            onToggle={handleTakeDose}
          />
          <DoseButton
            dose="evening"
            icon={<Moon />}
            isTaken={takenDoses.evening}
            onToggle={handleTakeDose}
          />
        </div>
        <Button
          onClick={handleTakeAll}
          variant={allTaken ? "secondary" : "default"}
          className="w-full transition-colors text-base font-bold"
          style={allTaken ? { backgroundColor: 'hsl(var(--accent))', color: 'hsl(var(--accent-foreground))', borderColor: 'hsl(var(--accent))' } : {}}
        >
          <Check className="mr-2 h-4 w-4" />
          {allTaken ? '전체가 선택되었습니다.' : '전체를 선택합니다.'}
        </Button>
        <Button onClick={onSave} className="w-full text-base font-bold" variant="default">
          <Save className="mr-2 h-4 w-4" />
          복약 일정을 저장합니다.
        </Button>
      </CardContent>
    </Card>
  );
}

interface DoseButtonProps {
  dose: Dose;
  icon: React.ReactNode;
  isTaken: boolean;
  onToggle: (dose: Dose) => void;
}


const DOSE_LABELS: Record<Dose, string> = {
  morning: '아침',
  noon: '점심',
  evening: '저녁',
};

function DoseButton({ dose, icon, isTaken, onToggle }: DoseButtonProps) {
  return (
    <Button
      variant="outline"
      className={cn(
        "h-20 flex-col gap-1 transition-all duration-300 transform active:scale-95 font-bold",
        isTaken && "border-transparent"
      )}
      style={isTaken ? { backgroundColor: 'hsl(var(--accent))', color: 'hsl(var(--accent-foreground))' } : {}}
      onClick={() => onToggle(dose)}
    >
      <div className="transition-transform duration-300" style={{ transform: isTaken ? 'scale(1.2)' : 'scale(1)' }}>
        {isTaken ? <Check className="w-6 h-6" /> : icon}
      </div>
      <span className="text-sm">{DOSE_LABELS[dose]}</span>
    </Button>
  );
}

