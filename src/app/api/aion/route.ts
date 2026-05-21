import { NextResponse } from "next/server";
import { getAionSnapshot } from "@/adapters/aion";

export const dynamic = "force-dynamic";

export async function GET() {
  const snap = await getAionSnapshot();
  return NextResponse.json(snap);
}
