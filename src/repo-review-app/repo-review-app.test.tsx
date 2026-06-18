// DOM-capable tests: these mount the real component tree with react-dom/client
// so effects and refs run, catching ref/effect regressions that the SSR-string
// tests cannot. Worker is stubbed inert in test-setup.ts, so the Pyodide
// runtime never loads here.
import { describe, it, expect, afterEach, spyOn } from "bun:test";
import {
  render,
  screen,
  fireEvent,
  cleanup,
  within,
} from "@testing-library/react";
import { App } from "./repo-review-app";

afterEach(cleanup);

describe("App (DOM)", () => {
  it("smoke-mounts the app shell without crashing", () => {
    render(<App deps={[]} disableUrlSync />);
    expect(screen.getByLabelText("Org/Repo")).toBeDefined();
    expect(screen.getByLabelText("Branch/Tag")).toBeDefined();
    expect(screen.getByRole("combobox", { name: "Show" })).toBeDefined();
  });

  it("wires the Branch/Tag Autocomplete input ref (regression guard for #407)", async () => {
    const errorSpy = spyOn(console, "error");
    render(<App deps={[]} disableUrlSync />);
    const input = screen.getByLabelText("Branch/Tag") as HTMLInputElement;

    // Opening the listbox makes MUI focus the input through its inputRef. When
    // the ref isn't wired (the #407 slotProps regression), inputRef.current is
    // null: MUI logs "Unable to find the input element" and interaction throws.
    fireEvent.focus(input);
    fireEvent.keyDown(input, { key: "ArrowDown" });

    const listbox = await screen.findByRole("listbox");
    const options = within(listbox).getAllByRole("option");
    expect(options.length).toBeGreaterThanOrEqual(5);
    expect(options.map((o) => o.textContent)).toContain(
      "HEAD (default branch)",
    );

    const muiInputError = errorSpy.mock.calls.find((call) =>
      String(call[0]).includes("Unable to find the input element"),
    );
    expect(muiInputError).toBeUndefined();
    errorSpy.mockRestore();
  });

  it("opens the Show select and updates the value and URL on change", async () => {
    // URL sync left on (the docs webapp default): the menu portals to body, so
    // it stays in the accessibility tree, and the change is mirrored to the URL.
    window.history.replaceState(null, "", "/");
    render(<App deps={[]} />);
    const combo = screen.getByRole("combobox", { name: "Show" });
    expect(combo.textContent).toBe("All");

    fireEvent.mouseDown(combo);
    const listbox = await screen.findByRole("listbox");
    expect(
      within(listbox)
        .getAllByRole("option")
        .map((o) => o.textContent),
    ).toEqual(["All", "Errors & Skips", "Errors only"]);

    fireEvent.click(within(listbox).getByText("Errors only"));
    expect(
      screen.getByRole("combobox", { name: "Show" }).textContent,
    ).toContain("Errors only");
    expect(window.location.search).toContain("show=err");
  });
});
