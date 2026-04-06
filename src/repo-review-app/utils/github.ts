export async function fetchRepoRefs(repo: string) {
  if (!repo) return { branches: [], tags: [] };
  try {
    const [branchesResponse, tagsResponse] = await Promise.all([
      fetch(`https://api.github.com/repos/${repo}/branches`),
      fetch(`https://api.github.com/repos/${repo}/tags`),
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
      branches: branches.map((branch: any) => ({
        name: branch.name,
        type: "branch",
      })),
      tags: tags.map((tag: any) => ({ name: tag.name, type: "tag" })),
    };
  } catch (error) {
    console.error("Error fetching repo references:", error);
    return { branches: [], tags: [] };
  }
}
