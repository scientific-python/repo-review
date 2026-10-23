import { describe, it, expect } from "bun:test";
import { ignoreToml } from "./ignore";

describe("ignoreToml", () => {
  it("returns empty string without failures", () => {
    expect(
      ignoreToml({
        a: [
          { name: "A100", state: true },
          { name: "A101", state: undefined },
        ],
      }),
    ).toBe("");
  });

  it("lists failed checks across families", () => {
    expect(
      ignoreToml({
        a: [
          { name: "A100", state: true },
          { name: "A101", state: false },
        ],
        b: [{ name: "B200", state: false }],
      }),
    ).toBe('[tool.repo-review]\nignore = ["A101", "B200"]');
  });
});
