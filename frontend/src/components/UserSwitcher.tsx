import { SandboxUser } from "@/lib/types";

export function UserSwitcher({
  users,
  selected,
  onSelect,
}: {
  users: SandboxUser[];
  selected: string | null;
  onSelect: (username: string) => void;
}) {
  return (
    <select
      className="rounded border px-3 py-2 text-sm"
      value={selected ?? ""}
      onChange={(e) => onSelect(e.target.value)}
    >
      <option value="" disabled>
        Select a sandbox user
      </option>
      {users.map((u) => (
        <option key={u.username} value={u.username}>
          {u.username} ({u.profile})
        </option>
      ))}
    </select>
  );
}
