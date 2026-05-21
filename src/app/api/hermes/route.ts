import { NextResponse } from "next/server";
import { getHermesSnapshot } from "@/adapters/hermes";

export const dynamic = "force-dynamic";

export async function GET() {
  const snap = await getHermesSnapshot();
  return NextResponse.json(snap);
}
