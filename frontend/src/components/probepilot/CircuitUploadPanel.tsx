"use client";

import { useCallback, useRef, useState } from "react";
import { motion } from "framer-motion";
import { UploadCloud } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type Props = {
  onNetlistText?: (text: string) => void;
};

export function CircuitUploadPanel({ onNetlistText }: Props) {
  const [name, setName] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const onFiles = useCallback(
    (files: FileList | null) => {
      if (!files?.length) return;
      const f = files[0];
      setName(f.name);
      if (f.name.endsWith(".cir") || f.name.endsWith(".sp") || f.name.endsWith(".net")) {
        f.text().then((t) => onNetlistText?.(t));
      }
    },
    [onNetlistText],
  );

  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <UploadCloud className="h-4 w-4 text-amd" />
          Circuit intake
        </CardTitle>
        <p className="text-xs text-slate-400">
          Use the KiCad pcbnew plugin for live board snapshots. Here you can still attach SPICE, BOM CSV, scope CSV, or images for the standalone lab console.
        </p>
      </CardHeader>
      <CardContent>
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept=".kicad_sch,.cir,.sp,.net,.csv,image/*"
          onChange={(e) => onFiles(e.target.files)}
        />
        <motion.div whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.99 }}>
          <Button type="button" variant="secondary" className="w-full" onClick={() => inputRef.current?.click()}>
            Choose files
          </Button>
        </motion.div>
        {name ? <p className="mt-3 text-xs text-slate-400">Last file: {name}</p> : null}
      </CardContent>
    </Card>
  );
}
