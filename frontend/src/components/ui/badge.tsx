import { cn } from "@/lib/utils";

export function Badge({ className, ...props }: React.HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md border border-amd-border bg-slate-900 px-2 py-0.5 text-xs font-medium text-slate-200",
        className,
      )}
      {...props}
    />
  );
}
