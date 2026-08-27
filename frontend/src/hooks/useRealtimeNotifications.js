import { useEffect } from "react";
import { supabase } from "../services/supabase";


export function useRealtimeNotifications(
  onNotification
) {

  useEffect(() => {

    const channel = supabase
      .channel("emergency-notifications")
      .on(
        "postgres_changes",
        {
          event: "INSERT",
          schema: "public",
          table: "notifications",
        },
        (payload) => {

          console.log(
            "Realtime notification:",
            payload.new
          );

          onNotification?.(
            payload.new
          );
        }
      )
      .subscribe();


    return () => {

      supabase.removeChannel(
        channel
      );

    };

  }, [onNotification]);
}