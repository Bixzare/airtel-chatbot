"use client";
import { useState, useEffect } from "react";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import { AirtelSymbol, AirtelText } from "../title/svg";

export default function Header() {
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    return (
        <header className="flex justify-between items-center w-full px-4 min-h-10">
            <div className="flex justify-center items-center">
                {/* Show logo components only when mounted to prevent hydration mismatch */}
                {mounted ? (
                    <>
                        <AirtelSymbol className="w-auto h-[15px]" />
                        <AirtelText className="w-auto h-[15px]" />
                    </>
                ) : (
                    <>
                        {/* Neutral placeholder for logos during loading */}
                        <div className="w-[15px] h-[15px] bg-transparent" />
                        <div className="w-[60px] h-[15px] bg-transparent" />
                    </>
                )}
            </div>
            <div>
                <ThemeToggle />
            </div>
        </header>
    );
}