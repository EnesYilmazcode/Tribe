import { describe, it, expect } from "vitest";
import { usd, hostname, formatName, formatRole, scoreColor } from "./format";

describe("usd", () => {
  it("formats with thousands separators", () => {
    expect(usd(45200)).toBe("$45,200");
    expect(usd(0)).toBe("$0");
  });
});

describe("hostname", () => {
  it("strips www and path", () => {
    expect(hostname("https://www.fec.gov/data/receipts/?x=1")).toBe("fec.gov");
  });
  it("falls back on garbage", () => {
    expect(hostname("not a url")).toBe("source");
  });
});

describe("formatName (FEC LAST, FIRST)", () => {
  it("flips last, first to natural order", () => {
    expect(formatName("Holloway, Margaret")).toBe("Margaret Holloway");
    expect(formatName("SMITH, JOHN A")).toBe("JOHN A SMITH");
  });
  it("leaves already-natural names alone", () => {
    expect(formatName("Margaret Holloway")).toBe("Margaret Holloway");
  });
  it("does not break on extra commas or empty halves", () => {
    expect(formatName("Doe, Jane, Jr")).toBe("Doe, Jane, Jr");
    expect(formatName(", Margaret")).toBe(", Margaret");
  });
});

describe("formatRole (messy employer/occupation)", () => {
  it("joins occupation and employer", () => {
    expect(formatRole("Attorney", "Cascade Law")).toBe("Attorney at Cascade Law");
  });
  it("drops non-informative values", () => {
    expect(formatRole("RETIRED", "RETIRED")).toBe("RETIRED"); // keeps the single value
    expect(formatRole("Engineer", "")).toBe("Engineer");
    expect(formatRole("", "Microsoft")).toBe("Microsoft");
    expect(formatRole("Self-Employed", "Self-Employed")).toBe("Self-Employed");
  });
  it("returns empty when nothing useful", () => {
    expect(formatRole("", "")).toBe("");
    expect(formatRole(undefined, undefined)).toBe("");
  });
  it("collapses duplicate occupation/employer", () => {
    expect(formatRole("Founder", "Founder")).toBe("Founder");
  });
});

describe("scoreColor", () => {
  it("maps score bands to color vars", () => {
    expect(scoreColor(91)).toBe("var(--color-accent)");
    expect(scoreColor(80)).toBe("var(--color-accent)");
    expect(scoreColor(72)).toBe("var(--color-amber)");
    expect(scoreColor(50)).toBe("var(--color-faint)");
  });
});
