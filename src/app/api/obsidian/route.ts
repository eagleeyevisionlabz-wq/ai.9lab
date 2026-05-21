import { NextResponse } from "next/server";
import { getObsidianSnapshot } from "@/adapters/obsidian";

export const dynamic = "force-dynamic";

export async function GET() {
  const snap = await getObsidianSnapshot();
  return NextResponse.json(snap);
}
