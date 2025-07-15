import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
 
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Gets the initial theme based on localStorage or system preference
 * Can be used in useEffect to set initial theme before hydration
 */
export function getInitialTheme(): 'light' | 'dark' {
  // Check if we're in the browser
  if (typeof window !== 'undefined') {
    // First check localStorage
    const storedTheme = localStorage.getItem('theme')
    if (storedTheme === 'light' || storedTheme === 'dark') {
      return storedTheme
    }
    
    // Then check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark'
    }
  }
  
  // Default to light
  return 'light'
}
