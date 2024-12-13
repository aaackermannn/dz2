import os
import argparse
import datetime
from git import Repo, InvalidGitRepositoryError

class GitDependencyGraph:
    def __init__(self, repo_path, before_date):
        try:
            self.repo = Repo(repo_path)
        except InvalidGitRepositoryError:
            print(f"Ошибка: {repo_path} не является Git-репозиторием.")
            exit(1)

        try:
            self.before_date = datetime.datetime.strptime(before_date, "%Y-%m-%d")
        except ValueError:
            print(f"Ошибка: Некорректный формат даты {before_date}. Используйте формат YYYY-MM-DD.")
            exit(1)

        self.graph = {}

    def build_graph(self, max_commits=None):
        """Построение графа зависимостей по коммитам до заданной даты."""
        commit_count = 0
        for commit in self.repo.iter_commits():
            commit_date = datetime.datetime.fromtimestamp(commit.committed_date)
            if commit_date > self.before_date:
                continue
            files = commit.stats.files.keys()
            self.graph[commit.hexsha] = files
            commit_count += 1

            print(f"Обработан коммит {commit.hexsha[:7]} ({commit_date.strftime('%Y-%m-%d')})")

            if max_commits and commit_count >= max_commits:
                print("Достигнуто ограничение по количеству коммитов.")
                break

    def to_mermaid(self):
        """Генерация Mermaid кода графа зависимостей."""
        lines = ["graph TD"]
        for commit, files in self.graph.items():
            for file in files:
                lines.append(f'"{commit}" --> "{file}"')
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Визуализация графа зависимостей в Git репозитории.")
    parser.add_argument("--repo", default="Hello-World", help="Путь к анализируемому репозиторию.")
    parser.add_argument("--before-date", default="2023-01-01", help="Дата для фильтрации коммитов (YYYY-MM-DD).")
    parser.add_argument("--max-commits", type=int, default=100, help="Максимальное количество обрабатываемых коммитов.")
    args = parser.parse_args()

    if not os.path.exists(args.repo):
        print(f"Ошибка: Путь {args.repo} не существует. Убедитесь, что клонировали репозиторий.")
        return

    graph = GitDependencyGraph(repo_path=args.repo, before_date=args.before_date)
    graph.build_graph(max_commits=args.max_commits)
    mermaid_code = graph.to_mermaid()

    print(mermaid_code)


if __name__ == "__main__":
    main()




