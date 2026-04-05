import { mountApp } from "./repo-review-app";

mountApp({
  header: true,
  deps: [
    "repo-review~=1.0.0",
    "sp-repo-review==2026.04.04",
    "validate-pyproject[all]~=0.25.0",
    "validate-pyproject-schema-store==2026.03.29",
  ],
});
