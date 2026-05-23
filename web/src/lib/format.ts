// Pure display/formatting helpers — kept separate so they're unit-testable.

export function usd(n: number): string {
  return "$" + n.toLocaleString("en-US");
}

export function hostname(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return "source";
  }
}

// FEC names arrive as "LASTNAME, FIRSTNAME" — flip to natural order.
export function formatName(raw: string): string {
  const parts = raw.split(",");
  if (parts.length === 2) {
    const last = parts[0].trim();
    const first = parts[1].trim();
    if (last && first) return `${first} ${last}`;
  }
  return raw.trim();
}

// Employer/occupation are often blank or non-informative ("RETIRED", "SELF").
export const NONINFO = new Set([
  "", "retired", "none", "n/a", "na", "not employed", "self", "self-employed",
  "self employed", "information requested", "requested", "homemaker",
]);

// Backend title-cases names, lowercasing business suffixes ("Fahr, LLC" -> "Fahr, Llc").
// Re-uppercase the unambiguous ones for clean display.
const ACRONYMS = new Set(["llc", "lp", "llp", "pac", "inc", "pllc"]);
export function tidyOrg(s: string): string {
  return s.replace(/[A-Za-z]+/g, (w) => (ACRONYMS.has(w.toLowerCase()) ? w.toUpperCase() : w));
}

export function formatRole(occupation?: string, employer?: string): string {
  const occ = (occupation || "").trim();
  const emp = tidyOrg((employer || "").trim());
  const occOk = occ.length > 0 && !NONINFO.has(occ.toLowerCase());
  const empOk = emp.length > 0 && !NONINFO.has(emp.toLowerCase());
  if (occOk && empOk && occ.toLowerCase() !== emp.toLowerCase()) return `${occ} at ${emp}`;
  if (occOk) return occ;
  if (empOk) return emp;
  return occ || emp || ""; // keep a single value like "Retired" if that's all we have
}

// Affinity score → CSS color var. >=80 strong, >=70 medium, else faint.
export function scoreColor(n: number): string {
  if (n >= 80) return "var(--color-accent)";
  if (n >= 70) return "var(--color-amber)";
  return "var(--color-faint)";
}
