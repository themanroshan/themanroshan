import json
import os
import requests

USERNAME = "themanroshan"

TOKEN = os.getenv("GITHUB_TOKEN")

headers = {
    "Accept": "application/vnd.github+json"
}

if TOKEN:
    headers["Authorization"] = f"Bearer {TOKEN}"


def github_get(url):
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


# User information
user = github_get(
    f"https://api.github.com/users/{USERNAME}"
)

# Public repositories
repos = github_get(
    f"https://api.github.com/users/{USERNAME}/repos?per_page=100"
)


total_stars = sum(
    repo["stargazers_count"]
    for repo in repos
)

total_forks = sum(
    repo["forks_count"]
    for repo in repos
)

languages = {}

for repo in repos:
    language = repo.get("language")

    if language:
        languages[language] = languages.get(language, 0) + 1


data = {
    "username": USERNAME,
    "name": user.get("name"),
    "public_repositories": user.get("public_repos"),
    "followers": user.get("followers"),
    "following": user.get("following"),
    "stars": total_stars,
    "forks": total_forks,
    "languages": languages,
}


os.makedirs("data", exist_ok=True)

with open(
    "data/github_stats.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        data,
        file,
        indent=2
    )

print(json.dumps(data, indent=2))
