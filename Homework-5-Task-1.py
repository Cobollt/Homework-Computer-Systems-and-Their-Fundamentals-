import argparse
import asyncio
import logging
import shutil
from pathlib import Path


logging.basicConfig(
    filename="file_sorter.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


async def copy_file(file_path, output_folder):
    try:
        extension = (
            file_path.suffix[1:].lower()
            if file_path.suffix
            else "no_extension"
        )

        destination_folder = output_folder / extension

        await asyncio.to_thread(
            destination_folder.mkdir,
            parents=True,
            exist_ok=True
        )

        destination = destination_folder / file_path.name

        await asyncio.to_thread(
            shutil.copy2,
            file_path,
            destination
        )

        print(
            f"{file_path} -> {destination}"
        )

    except Exception as error:
        logging.error(
            "Помилка копіювання %s: %s",
            file_path,
            error
        )


async def read_folder(
    source_folder,
    output_folder
):
    tasks = []

    try:
        items = await asyncio.to_thread(
            lambda: list(source_folder.iterdir())
        )

        for item in items:
            if item.is_dir():
                await read_folder(
                    item,
                    output_folder
                )

            elif item.is_file():
                tasks.append(
                    asyncio.create_task(
                        copy_file(
                            item,
                            output_folder
                        )
                    )
                )

        if tasks:
            await asyncio.gather(*tasks)

    except Exception as error:
        logging.error(
            "Помилка читання папки %s: %s",
            source_folder,
            error
        )


async def main():
    parser = argparse.ArgumentParser(
        description=(
            "Асинхронне сортування файлів "
            "за розширеннями"
        )
    )

    parser.add_argument(
        "-s",
        "--source",
        required=True,
        help="Вихідна папка"
    )

    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Цільова папка"
    )

    args = parser.parse_args()

    source_folder = Path(args.source)
    output_folder = Path(args.output)

    if not source_folder.exists():
        print(
            f"Папка {source_folder} не існує"
        )
        return

    if not source_folder.is_dir():
        print(
            f"{source_folder} не є папкою"
        )
        return

    try:
        await asyncio.to_thread(
            output_folder.mkdir,
            parents=True,
            exist_ok=True
        )

        await read_folder(
            source_folder,
            output_folder
        )

        print(
            "Сортування завершено"
        )

    except Exception as error:
        logging.error(
            "Помилка програми: %s",
            error
        )


if __name__ == "__main__":
    asyncio.run(main())