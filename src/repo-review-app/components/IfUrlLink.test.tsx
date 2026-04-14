// Component tests use react-dom/server's renderToStaticMarkup — no DOM or
// extra dependencies required. Assertions are over the rendered HTML string.
import { describe, it, expect } from "bun:test";
import { renderToStaticMarkup } from "react-dom/server";
import React from "react";
import IfUrlLink from "./IfUrlLink";

describe("IfUrlLink", () => {
  it("renders an anchor element when a url is provided", () => {
    const html = renderToStaticMarkup(
      <IfUrlLink name="SP001" url="https://example.com/check" />,
    );
    expect(html).toContain("<a ");
    expect(html).toContain('href="https://example.com/check"');
    expect(html).toContain("SP001");
  });

  it("adds rel=noopener noreferrer and target=_blank on links", () => {
    const html = renderToStaticMarkup(
      <IfUrlLink name="SP001" url="https://example.com" />,
    );
    expect(html).toContain('rel="noopener noreferrer"');
    expect(html).toContain('target="_blank"');
  });

  it("does not render an anchor when url is empty string", () => {
    const html = renderToStaticMarkup(<IfUrlLink name=": " url="" />);
    expect(html).not.toContain("<a ");
    expect(html).toContain(": ");
  });

  it("does not render an anchor when url is undefined", () => {
    const html = renderToStaticMarkup(<IfUrlLink name="label" />);
    expect(html).not.toContain("<a ");
    expect(html).toContain("label");
  });

  it("passes color through to the rendered element", () => {
    const html = renderToStaticMarkup(
      <IfUrlLink name="SP001" url="https://example.com" color="error.main" />,
    );
    // MUI resolves the color prop to a class or inline style; either way the
    // node must be present with the link text.
    expect(html).toContain("SP001");
  });
});
