from string import Template

APPLICATION_NAME: str = "joss"
GITHUB_REPO_OWNER: str = "openjournals"
GITHUB_REPO_PROJECT: str = "joss-reviews"

JOSS_ACTIVE_PAPERS_TEMPLATE: Template = Template(
    template="https://joss.theoj.org/papers/active.atom?page=$page"
)
JOSS_PUBLISHED_PAPERS_TEMPLATE: Template = Template(
    template="https://joss.theoj.org/papers/published.atom?page=$page"
)

HTTP_GET_TIMEOUT: int = 60
HTTP_HEAD_TIMEOUT: int = 60
HTTP_POST_TIMEOUT: int = 60
