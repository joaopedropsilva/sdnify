class TestLogger:
    @staticmethod
    def title(title: str) -> None:
        print(f"\n{120 * '='}\n")
        print(f"\t{title.upper()}")
        print(f"\n{120 * '='}")

    @staticmethod
    def message(message: str) -> None:
        print(f"[test:message] {message}")

    @staticmethod
    def command(command: str) -> None:
        print(f"[test:command] {command}")

