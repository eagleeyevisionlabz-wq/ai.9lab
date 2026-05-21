import { getAionSnapshot } from "@/adapters/aion";
import { AionCard } from "@/components/cards/AionCard";

export const dynamic = "force-dynamic";

export default async function AionPage() {
  const snap = await getAionSnapshot();
  return (
    <div className="space-y-6">
      <AionCard snap={snap} />
    </div>
  );
}
