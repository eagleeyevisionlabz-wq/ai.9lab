import { NextResponse } from "next/server";
import { addCapture } from "@/adapters/paperclip";
import type { CaptureKind, PaperclipCapture } from "@/adapters/types";

export const dynamic = "force-dynamic";

const ALLOWED_KINDS: CaptureKind[] = ["clip", "doc", "snippet", "research", "link"];
const ALLOWED_ROUTES: PaperclipCapture["routedTo"][number][] = ["obsidian", "hermes-memory"];

type Body = {
  kind?: string;
  title?: unknown;
  source?: unknown;
  body?: unknown;
  tags?: unknown;
  routedTo?: unknown;
};

function asString(v: unknown, max = 4096): string | null {
  if (typeof v !== "string") return null;
  const s = v.trim();
  if (!s) return null;
  return s.slice(0, max);
}

export async function POST(req: Request) {
  let payload: Body;
  try {
    payload = (await req.json()) as Body;
  } catch {
    return NextResponse.json({ error: "invalid json" }, { status: 400 });
  }

  const kind = (payload.kind ?? "clip") as CaptureKind;
  if (!ALLOWED_KINDS.includes(kind)) {
    return NextResponse.json({ error: `invalid kind: ${kind}` }, { status: 400 });
  }

  const title = asString(payload.title, 256);
  const body = asString(payload.body, 100_000);
  if (!title || !body) {
    return NextResponse.json({ error: "title and body required" }, { status: 400 });
  }
  const source = asString(payload.source, 1024) ?? undefined;

  const rawTags = Array.isArray(payload.tags) ? payload.tags : [];
  const tags = rawTags
    .map((t) => asString(t, 64))
    .filter((t): t is string => Boolean(t))
    .slice(0, 32);

  const rawRoutes = Array.isArray(payload.routedTo) ? payload.routedTo : ["hermes-memory"];
  const routedTo = rawRoutes.filter(
    (r): r is PaperclipCapture["routedTo"][number] =>
      typeof r === "string" && (ALLOWED_ROUTES as string[]).includes(r),
  );

  const created = await addCapture({ kind, title, source, body, tags, routedTo });
  return NextResponse.json(created, { status: 201 });
}
