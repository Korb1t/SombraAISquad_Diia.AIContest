import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * Поєднує Tailwind класи і вирішує конфлікти
 * Приклад: cn("p-4", "p-6") => "p-6" (залишає останній)
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}




