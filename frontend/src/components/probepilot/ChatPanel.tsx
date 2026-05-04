"use client";

import { FormEvent, useState } from "react";
import { motion } from "framer-motion";
import { Send, Mic } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

type Props = {
  connected: boolean;
  onSend: (text: string) => void;
  onVoice: () => void;
  listening: boolean;
  voiceSupported: boolean;
  lastReply?: string;
};

export function ChatPanel({ connected, onSend, onVoice, listening, voiceSupported, lastReply }: Props) {
  const [text, setText] = useState("The LED does not turn on.");

  function submit(e: FormEvent) {
    e.preventDefault();
    if (!text.trim()) return;
    onSend(text.trim());
  }

  return (
    <Card className="flex flex-col min-h-[320px]">
      <CardHeader className="flex-row items-center justify-between gap-2">
        <CardTitle>Lab chat</CardTitle>
        <Badge>{connected ? "Live WS" : "WS down"}</Badge>
      </CardHeader>
      <CardContent className="flex flex-1 flex-col gap-3">
        {lastReply ? (
          <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-lg border border-amd-border bg-slate-900/80 p-3 text-sm text-slate-200"
          >
            {lastReply}
          </motion.div>
        ) : (
          <p className="text-sm text-slate-500">Send a symptom — the agent will simulate, retrieve, and plan tools.</p>
        )}
        <form onSubmit={submit} className="mt-auto flex gap-2">
          <textarea
            className="min-h-[72px] flex-1 resize-none rounded-md border border-amd-border bg-slate-950 px-3 py-2 text-sm outline-none ring-amd/40 focus:ring-2"
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
          <div className="flex flex-col gap-2">
            <Button type="submit" className="h-10 w-10 p-0" title="Send">
              <Send className="h-4 w-4" />
            </Button>
            <Button
              type="button"
              variant="secondary"
              className="h-10 w-10 p-0"
              title="Voice"
              disabled={!voiceSupported}
              onClick={onVoice}
            >
              <Mic className={`h-4 w-4 ${listening ? "text-amd animate-pulse" : ""}`} />
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
