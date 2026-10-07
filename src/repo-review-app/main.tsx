import { mountApp } from "./repo-review-app";

mountApp({
  header: true,
  deps: [
    "repo-review~=1.2.1",
    "sp-repo-review==2026.08.14",
    "validate-pyproject[all]~=0.26.0",
    "validate-pyproject-schema-store==2026.10.06",
  ],
});
