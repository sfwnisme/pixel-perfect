"use client";

import { ChatArea } from "@/components/chat/ChatArea";
import { Sidebar } from "@/components/chat/Sidebar";

export default function Home() {
  return (
    <div className="flex h-screen w-full">
      <Sidebar />
      <ChatArea />
    </div>
  );
}