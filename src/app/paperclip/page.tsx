import { getPaperclipSnapshot } from "@/adapters/paperclip";
import { PaperclipCard } from "@/components/cards/PaperclipCard";

export const dynamic = "force-dynamic";

export default async function PaperclipPage() {
  const snap = await getPaperclipSnapshot();
  return (
    <div className="space-y-6">
      <PaperclipCard initial={snap} />
    </div>
  );
}
