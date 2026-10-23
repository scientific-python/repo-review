import { describe, it, expect, afterEach } from "bun:test";
import { render, screen, cleanup } from "@testing-library/react";
import IgnoreHint from "./IgnoreHint";

afterEach(cleanup);

describe("IgnoreHint", () => {
  it("shows the TOML for failed checks", () => {
    render(
      <IgnoreHint
        results={{ a: [{ name: "A101", state: false }] }}
        onCopy={() => {}}
      />,
    );
    expect(screen.getByText(/ignore = \["A101"\]/)).toBeDefined();
    expect(screen.getByLabelText("Copy ignore config")).toBeDefined();
  });

  it("renders nothing without failures", () => {
    const { container } = render(
      <IgnoreHint
        results={{ a: [{ name: "A100", state: true }] }}
        onCopy={() => {}}
      />,
    );
    expect(container.innerHTML).toBe("");
  });
});
