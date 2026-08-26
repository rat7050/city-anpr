import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { format } from "date-fns";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date, formatStr: string = "yyyy-MM-dd HH:mm:ss") {
  return format(new Date(date), formatStr);
}

export function formatSpeed(speed: number) {
  return `${Math.round(speed)} km/h`;
}

export function formatDistance(km: number) {
  return `${km.toFixed(2)} km`;
}

export function getCongestionColor(level: string) {
  switch (level.toUpperCase()) {
    case 'LOW': return 'text-emerald-500';
    case 'MODERATE': return 'text-amber-500';
    case 'HIGH': return 'text-orange-500';
    case 'SEVERE': return 'text-red-500';
    default: return 'text-slate-400';
  }
}

export function getAlertColor(severity: string) {
  switch (severity.toUpperCase()) {
    case 'CRITICAL': return 'text-red-600 bg-red-600/10 border-red-600/20';
    case 'HIGH': return 'text-orange-500 bg-orange-500/10 border-orange-500/20';
    case 'MEDIUM': return 'text-amber-400 bg-amber-400/10 border-amber-400/20';
    case 'LOW': return 'text-blue-400 bg-blue-400/10 border-blue-400/20';
    default: return 'text-slate-400 bg-slate-400/10 border-slate-400/20';
  }
}
