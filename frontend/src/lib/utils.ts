import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function apiBase(): string {
  return process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
}

export function wsDiagnosticsUrl(): string {
  const u = new URL(apiBase());
  u.protocol = u.protocol === "https:" ? "wss:" : "ws:";
  u.pathname = "/ws/diagnostics";
  u.search = "";
  u.hash = "";
  return u.toString();
}
