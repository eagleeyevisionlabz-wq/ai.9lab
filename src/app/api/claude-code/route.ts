import { NextResponse } from "next/server";
import { getClaudeCodeSnapshot } from "@/adapters/claudeCode";

export const dynamic = "force-dynamic";

export async function GET() {
  const snap = await getClaudeCodeSnapshot();
  return NextResponse.json(snap);
}
