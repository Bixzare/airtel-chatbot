"use client";

import * as React from "react";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import { motion, AnimatePresence } from "framer-motion";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);
  const [ripple, setRipple] = React.useState<{ x: number; y: number } | null>(null);
  const buttonRef = React.useRef<HTMLButtonElement>(null);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  const toggleTheme = () => {
    if (!buttonRef.current) return;

    // Get center position of the button for the ripple origin
    const rect = buttonRef.current.getBoundingClientRect();
    const x = rect.left + rect.width / 2;
    const y = rect.top + rect.height / 2;

    // Set ripple origin
    setRipple({ x, y });

    // Delay theme change to allow ripple to start
    setTimeout(() => {
      setTheme(theme === "dark" ? "light" : "dark");
    }, 200);

    // Clear ripple after full transition
    setTimeout(() => {
      setRipple(null);
    }, 500);
  };

  return (
    <>
      <Button
        ref={buttonRef}
        variant="ghost"
        size="icon"
        onClick={toggleTheme}
        className="p-0 focus:ring-0 focus:outline-none transition-colors
          hover:bg-[#E31F26] hover:text-white
          dark:hover:bg-white dark:hover:text-[#E31F26]
          hover:cursor-pointer"
      >
        {theme === "dark" ? (
          <Sun className="h-5 w-5 transition-colors" />
        ) : (
          <Moon className="h-5 w-5 transition-colors" />
        )}
      </Button>

      {/* Ripple overlay */}
      <AnimatePresence>
        {ripple && (
          <motion.div
            className="fixed top-0 left-0 w-screen h-screen z-50 pointer-events-none"
            initial={{
              clipPath: `circle(0px at ${ripple.x}px ${ripple.y}px)`,
              backgroundColor: theme === "dark" ? "#ffffff" : "#E31F26",
            }}
            animate={{
              clipPath: `circle(150% at ${ripple.x}px ${ripple.y}px)`,
            }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
          />
        )}
      </AnimatePresence>
    </>
  );
}
