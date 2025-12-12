from __future__ import annotations


def main() -> None:
    try:
        from battleship.ui import run
    except ModuleNotFoundError as e:
        raise SystemExit(
            "pygame не установлен. Установите зависимости: pip install -r requirements.txt"
        ) from e

    run()


if __name__ == "__main__":
    main()
