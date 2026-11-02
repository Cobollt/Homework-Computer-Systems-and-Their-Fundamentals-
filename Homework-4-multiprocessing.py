from multiprocessing import Process, Queue
from pathlib import Path
from time import perf_counter


def split_files(files, workers):
    return [
        files[index::workers]
        for index in range(workers)
        if files[index::workers]
    ]


def search_in_files(
    files,
    keywords,
    queue
):
    result = {
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
                    result[keyword].append(
                        str(file_path)
                    )

        except (OSError, UnicodeError) as error:
            print(
                f"Помилка читання "
                f"{file_path}: {error}"
            )

    queue.put(result)


def search_with_processes(
    files,
    keywords,
    process_count=4
):
    result = {
        keyword: []
        for keyword in keywords
    }

    if not files:
        return result

    process_count = min(
        process_count,
        len(files)
    )

    groups = split_files(
        files,
        process_count
    )

    queue = Queue()
    processes = []

    start = perf_counter()

    for group in groups:
        process = Process(
            target=search_in_files,
            args=(
                group,
                keywords,
                queue
            )
        )

        processes.append(process)
        process.start()

    partial_results = []

    for _ in processes:
        partial_results.append(
            queue.get()
        )

    for process in processes:
        process.join()

    for partial_result in partial_results:
        for keyword, paths in partial_result.items():
            result[keyword].extend(paths)

    elapsed = perf_counter() - start

    print(
        f"Час виконання multiprocessing: "
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

        result = search_with_processes(
            files,
            keywords,
            process_count=4
        )

        print_results(result)

    except OSError as error:
        print(
            f"Помилка файлової системи: "
            f"{error}"
        )


if __name__ == "__main__":
    main()