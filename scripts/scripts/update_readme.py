import json
from datetime import datetime, timezone

with open(
    "data/github_stats.json",
    encoding="utf-8"
) as file:
    data = json.load(file)


updated = datetime.now(
    timezone.utc
).strftime("%d %b %Y • %H:%M UTC")


stats = f"""
### 📊 GitHub Statistics

| Metric | Value |
|---|---:|
| Repositories | {data["public_repositories"]} |
| Stars | {data["stars"]} |
| Forks | {data["forks"]} |
| Followers | {data["followers"]} |
| Following | {data["following"]} |

**Last automated update:** {updated}
"""


with open(
    "README.md",
    encoding="utf-8"
) as file:
    readme = file.read()


start_marker = "<!-- AUTO_STATS_START -->"
end_marker = "<!-- AUTO_STATS_END -->"


start = readme.index(start_marker)
end = readme.index(end_marker)


new_readme = (
    readme[:start]
    + start_marker
    + "\n\n"
    + stats
    + "\n"
    + readme[end:]
)


with open(
    "README.md",
    "w",
    encoding="utf-8"
) as file:
    file.write(new_readme)


print("README updated.")
