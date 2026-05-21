import { NextResponse } from "next/server";
import { getPaperclipSnapshot } from "@/adapters/paperclip";

export const dynamic = "force-dynamic";

export async function GET() {
  const snap = await getPaperclipSnapshot();
  return NextResponse.json(snap);
}
