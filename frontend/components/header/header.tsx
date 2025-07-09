import { ThemeToggle } from "@/components/theme/theme-toggle";
import { AirtelSymbol, AirtelText } from "../title/svg";
export default function Header() {
    return (
        <header className = "flex justify-between items-center w-full px-4 min-h-10">
            <div className = "flex justfiy-center items-center"><AirtelSymbol className ="w-auto h-[15px]" /><AirtelText className="w-auto h-[15px]"/></div>
            <div><ThemeToggle/></div>
        </header>
    )
}