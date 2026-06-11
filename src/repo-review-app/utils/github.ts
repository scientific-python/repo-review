export async function fetchRepoRefs(repo: string) {
  if (!repo) return { branches: [], tags: [] };
  try {
    // Default page size is 30; request the maximum to avoid truncating refs.
    const [branchesResponse, tagsResponse] = await Promise.all([
      fetch(`https://api.github.com/repos/${repo}/branches?per_page=100`),
      fetch(`https://api.github.com/repos/${repo}/tags?per_page=100`),
    ]);

    if (!branchesResponse.ok || !tagsResponse.ok) {
      console.error("Error fetching repo data");
      return { branches: [], tags: [] };
    }

    const branches = (await branchesResponse.json()) as Array<{
      name: string;
    }>;
    const tags = (await tagsResponse.json()) as Array<{ name: string }>;

    return {
      branches: branches.map((branch) => ({
        name: branch.name,
        type: "branch",
      })),
      tags: tags.map((tag) => ({ name: tag.name, type: "tag" })),
    };
  } catch (error) {
    console.error("Error fetching repo references:", error);
    return { branches: [], tags: [] };
  }
}
