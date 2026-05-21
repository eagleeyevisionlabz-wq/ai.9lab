import { getClaudeCodeSnapshot } from "@/adapters/claudeCode";
import { ClaudeCodeCard } from "@/components/cards/ClaudeCodeCard";

export const dynamic = "force-dynamic";

export default async function ClaudeCodePage() {
  const snap = await getClaudeCodeSnapshot();
  return (
    <div className="space-y-6">
      <ClaudeCodeCard snap={snap} />
    </div>
  );
}
