import { describe, it, expect, beforeEach, afterEach, spyOn } from "bun:test";
import { fetchRepoRefs } from "./github";

const BRANCHES_RESPONSE = [{ name: "main" }, { name: "dev" }];
const TAGS_RESPONSE = [{ name: "v1.0.0" }, { name: "v2.0.0" }];

function makeFetchMock(
  branchesData: unknown,
  tagsData: unknown,
  status = 200,
): typeof globalThis.fetch {
  return (async (input: string | URL | Request) => {
    const url = input.toString();
    const body = url.includes("/branches")
      ? JSON.stringify(branchesData)
      : JSON.stringify(tagsData);
    return new Response(body, { status });
  }) as unknown as typeof globalThis.fetch;
}

describe("fetchRepoRefs", () => {
  let savedFetch: typeof globalThis.fetch;

  beforeEach(() => {
    savedFetch = globalThis.fetch;
    spyOn(console, "error").mockImplementation(() => {});
  });

  afterEach(() => {
    globalThis.fetch = savedFetch;
  });

  it("returns empty arrays immediately for an empty repo string", async () => {
    // fetch should never be called
    globalThis.fetch = (() => {
      throw new Error("fetch should not be called");
    }) as unknown as typeof globalThis.fetch;
    const result = await fetchRepoRefs("");
    expect(result).toEqual({ branches: [], tags: [] });
  });

  it("maps branch names and adds type='branch'", async () => {
    globalThis.fetch = makeFetchMock(BRANCHES_RESPONSE, []);
    const result = await fetchRepoRefs("owner/repo");
    expect(result.branches).toEqual([
      { name: "main", type: "branch" },
      { name: "dev", type: "branch" },
    ]);
    expect(result.tags).toEqual([]);
  });

  it("maps tag names and adds type='tag'", async () => {
    globalThis.fetch = makeFetchMock([], TAGS_RESPONSE);
    const result = await fetchRepoRefs("owner/repo");
    expect(result.branches).toEqual([]);
    expect(result.tags).toEqual([
      { name: "v1.0.0", type: "tag" },
      { name: "v2.0.0", type: "tag" },
    ]);
  });

  it("returns both branches and tags together", async () => {
    globalThis.fetch = makeFetchMock(BRANCHES_RESPONSE, TAGS_RESPONSE);
    const result = await fetchRepoRefs("owner/repo");
    expect(result.branches).toHaveLength(2);
    expect(result.tags).toHaveLength(2);
  });

  it("returns empty arrays when the API responds with a non-OK status", async () => {
    globalThis.fetch = makeFetchMock(null, null, 404);
    const result = await fetchRepoRefs("owner/repo");
    expect(result).toEqual({ branches: [], tags: [] });
  });

  it("returns empty arrays on a network error", async () => {
    globalThis.fetch = (async () => {
      throw new Error("Network error");
    }) as unknown as typeof globalThis.fetch;
    const result = await fetchRepoRefs("owner/repo");
    expect(result).toEqual({ branches: [], tags: [] });
  });
});
