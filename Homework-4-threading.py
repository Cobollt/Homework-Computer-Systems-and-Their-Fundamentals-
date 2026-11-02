from pathlib import Path
from threading import Thread, Lock
from time import perf_counter


def split_files(files, workers):
    return [
        files[index::workers]
        for index in range(workers)
        if files[index::workers]
    ]


def search_in_files(files, keywords, result, lock):
    local_result = {
        keyword: []
        for keyword in keywords
    }

    for file_path in files:
        try:
            text = file_path.read_text(
                encoding="utf-8"
            ).lower()

            for keyword in keywords:
                if keyword.lower() in text:
                    local_result[keyword].append(
                        str(file_path)
                    )

        except (OSError, UnicodeError) as error:
            print(
                f"Помилка читання "
                f"{file_path}: {error}"
            )

    with lock:
        for keyword, paths in local_result.items():
            result[keyword].extend(paths)


def search_with_threads(
    files,
    keywords,
    thread_count=4
):
    result = {
        keyword: []
        for keyword in keywords
    }

    if not files:
        return result

    thread_count = min(
        thread_count,
        len(files)
    )

    groups = split_files(
        files,
        thread_count
    )

    lock = Lock()
    threads = []

    start = perf_counter()

    for group in groups:
        thread = Thread(
            target=search_in_files,
            args=(
                group,
                keywords,
                result,
                lock
            )
        )

        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    elapsed = perf_counter() - start

    print(
        f"Час виконання threading: "
        f"{elapsed:.6f} секунд"
    )

    return result


def print_results(result):
    for keyword, files in result.items():
        print(f"\nКлючове слово: {keyword}")

        if files:
            for file_path in files:
                print(file_path)
        else:
            print("Не знайдено")


def main():
    directory = Path("text_files")

    keywords = [
        "python",
        "thread",
        "process",
        "database"
    ]

    try:
        files = list(
            directory.glob("*.txt")
        )

        if not files:
            print(
                "Текстові файли не знайдено"
            )
            return

        result = search_with_threads(
            files,
            keywords,
            thread_count=4
        )

        print_results(result)

    except OSError as error:
        print(
            f"Помилка файлової системи: "
            f"{error}"
        )


if __name__ == "__main__":
    main()