"use client";

import { useEffect } from 'react';
import { useToast } from '@/hooks/use-toast';

import { Button } from '@/components/ui/button';
import { playNotificationSound } from '@/utils/audio';
import { BellRing } from 'lucide-react';


const REMINDER_TIMES: Record<string, number> = {
  morning: 8,  // 8 AM
  noon: 12,    // 12 PM
  evening: 18, // 6 PM
};

const TIME_NAMES: Record<string, string> = {
  morning: '아침',
  noon: '점심',
  evening: '저녁',
};

interface ReminderHandlerProps {
  onReminder?: () => void;
}

export function ReminderHandler({ onReminder }: ReminderHandlerProps) {
  const { toast } = useToast();

  useEffect(() => {
    // Ensure this only runs on the client
    if (typeof window === 'undefined') return;

    const timers: NodeJS.Timeout[] = [];

    const scheduleReminders = () => {
      const now = new Date();

      for (const [name, hour] of Object.entries(REMINDER_TIMES)) {
        const reminderTime = new Date();
        reminderTime.setHours(hour, 0, 0, 0);

        let timeoutMs = reminderTime.getTime() - now.getTime();

        // If the time has already passed for today, don't schedule it.
        // This is a simple implementation that doesn't handle app reloads well.
        // A more robust solution would use service workers.
        if (timeoutMs > 0) {
          const timer = setTimeout(() => {
            const timeName = TIME_NAMES[name] || name;
            toast({
              title: "복용 알림",
              description: `${timeName} 약을 복용할 시간입니다!`,
              duration: 10000,
              icon: <BellRing className="h-10 w-10 text-blue-500" />,
            });
            playNotificationSound();
            if (onReminder) {
              onReminder();
            }
          }, timeoutMs);
          timers.push(timer);
        }
      }
    };

    scheduleReminders();

    return () => {
      // Cleanup timers on component unmount
      timers.forEach(clearTimeout);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const triggerTestReminder = () => {
    toast({
      title: "복용 알림 (테스트)",
      description: "약을 복용할 시간입니다!",
      duration: 10000,
      icon: <BellRing className="h-10 w-10 text-blue-500" />,
    });
    playNotificationSound();
    if (onReminder) {
      onReminder();
    }
  };

  return (
    <Button
      onClick={triggerTestReminder}
      className="w-full mb-4"
      variant="secondary"
    >
      알림 테스트
    </Button>
  );
}

