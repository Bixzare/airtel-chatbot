import Chat from "@/components/chat/chat";
import Header from "@/components/header/header";
import Title from "@/components/title/title";
import Image from "next/image";

export default function Home() {
  return (
    <div className="flex flex-col w-screen items-center p-1 text-foreground">
      <Header/>
      <Title/>
      <Chat/>
    </div>
  );
}
