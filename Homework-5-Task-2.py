import re
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from functools import reduce

import matplotlib.pyplot as plt
import requests


def download_text(url):
    try:
        response = requests.get(
            url,
            timeout=15
        )

        response.raise_for_status()

        return response.text

    except requests.RequestException as error:
        print(
            f"Помилка завантаження тексту: "
            f"{error}"
        )

        return None


def split_text(text, parts):
    words = re.findall(
        r"[A-Za-zА-Яа-яІіЇїЄєҐґ']+",
        text.lower()
    )

    chunk_size = max(
        1,
        len(words) // parts
    )

    chunks = []

    for index in range(
        0,
        len(words),
        chunk_size
    ):
        chunks.append(
            words[index:index + chunk_size]
        )

    return chunks


def mapper(words):
    return [
        (word, 1)
        for word in words
    ]


def shuffle(mapped_data):
    grouped = defaultdict(list)

    for mapped_part in mapped_data:
        for word, count in mapped_part:
            grouped[word].append(count)

    return grouped


def reducer(item):
    word, counts = item

    return (
        word,
        reduce(
            lambda x, y: x + y,
            counts
        )
    )


def map_reduce(
    text,
    workers=4
):
    chunks = split_text(
        text,
        workers
    )

    with ThreadPoolExecutor(
        max_workers=workers
    ) as executor:
        mapped_data = list(
            executor.map(
                mapper,
                chunks
            )
        )

    grouped_data = shuffle(
        mapped_data
    )

    with ThreadPoolExecutor(
        max_workers=workers
    ) as executor:
        reduced_data = list(
            executor.map(
                reducer,
                grouped_data.items()
            )
        )

    return dict(reduced_data)


def visualize_top_words(
    word_counts,
    top_n=10
):
    top_words = sorted(
        word_counts.items(),
        key=lambda item: item[1],
        reverse=True
    )[:top_n]

    words = [
        word
        for word, count in top_words
    ]

    counts = [
        count
        for word, count in top_words
    ]

    plt.figure(
        figsize=(10, 6)
    )

    plt.barh(
        words[::-1],
        counts[::-1]
    )

    plt.xlabel(
        "Частота"
    )

    plt.ylabel(
        "Слова"
    )

    plt.title(
        f"Топ-{top_n} найчастіше "
        f"вживаних слів"
    )

    plt.tight_layout()
    plt.show()


def print_top_words(
    word_counts,
    top_n=10
):
    top_words = sorted(
        word_counts.items(),
        key=lambda item: item[1],
        reverse=True
    )[:top_n]

    print(
        f"\nТоп-{top_n} слів:"
    )

    for word, count in top_words:
        print(
            f"{word}: {count}"
        )


def main():
    url = input(
        "Введіть URL тексту: "
    ).strip()

    text = download_text(url)

    if not text:
        return

    word_counts = map_reduce(
        text,
        workers=4
    )

    print_top_words(
        word_counts,
        top_n=10
    )

    visualize_top_words(
        word_counts,
        top_n=10
    )


if __name__ == "__main__":
    main()