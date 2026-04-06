import { describe, it, expect } from "bun:test";
import { sanitizePackageDir, parseRefType } from "./url";

describe("sanitizePackageDir", () => {
  it("returns empty string for empty input", () => {
    expect(sanitizePackageDir("")).toBe("");
  });

  it("strips leading slashes", () => {
    expect(sanitizePackageDir("/foo/bar")).toBe("foo/bar");
    expect(sanitizePackageDir("///foo")).toBe("foo");
  });

  it("returns empty string for path traversal segments", () => {
    expect(sanitizePackageDir("../etc/passwd")).toBe("");
    expect(sanitizePackageDir("foo/../bar")).toBe("");
    expect(sanitizePackageDir("../../secret")).toBe("");
  });

  it("returns valid nested path unchanged", () => {
    expect(sanitizePackageDir("src/mypackage")).toBe("src/mypackage");
    expect(sanitizePackageDir("packages/core")).toBe("packages/core");
  });

  it("trims surrounding whitespace", () => {
    expect(sanitizePackageDir("  foo  ")).toBe("foo");
    expect(sanitizePackageDir("  /foo/bar  ")).toBe("foo/bar");
  });

  it("allows a path that contains '...' (not '..')", () => {
    expect(sanitizePackageDir("my...package")).toBe("my...package");
  });
});

describe("parseRefType", () => {
  it("returns 'tag' for the string 'tag'", () => {
    expect(parseRefType("tag")).toBe("tag");
  });

  it("returns 'branch' for null", () => {
    expect(parseRefType(null)).toBe("branch");
  });

  it("returns 'branch' for empty string", () => {
    expect(parseRefType("")).toBe("branch");
  });

  it("returns 'branch' for any other string", () => {
    expect(parseRefType("branch")).toBe("branch");
    expect(parseRefType("HEAD")).toBe("branch");
    expect(parseRefType("main")).toBe("branch");
    expect(parseRefType("TAG")).toBe("branch"); // case-sensitive
  });
});
