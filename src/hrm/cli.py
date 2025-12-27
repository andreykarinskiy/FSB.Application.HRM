"""CLI приложение для управления кандидатами в HR системе"""
import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Prompt

from hrm.core.application import UseCases
from hrm.core.model import Candidate, CandidateSex, CandidateStatus


def _parse_birth_date(birth_date: Optional[str], console: Console) -> Optional[datetime.datetime]:
    """Парсит дату рождения из строки"""
    if not birth_date:
        return None
    try:
        return datetime.datetime.strptime(birth_date, "%Y-%m-%d")
    except ValueError:
        console.print(f"[red]Ошибка: Неверный формат даты. Используйте YYYY-MM-DD[/red]")
        raise typer.Exit(1)


def _parse_sex(sex: Optional[str], console: Console) -> Optional[CandidateSex]:
    """Парсит пол из строки"""
    if not sex:
        return None
    sex_upper = sex.upper()
    if sex_upper == "M":
        return CandidateSex.MALE
    elif sex_upper == "F":
        return CandidateSex.FEMALE
    else:
        console.print(f"[red]Ошибка: Неверное значение пола. Используйте M или F[/red]")
        raise typer.Exit(1)


def _format_candidate(candidate: Candidate, console: Console) -> None:
    """Форматирует и выводит информацию о кандидате"""
    console.print(f"[bold cyan]Информация о кандидате[/bold cyan]")
    console.print()
    console.print(f"ID: {candidate.id}")
    console.print(f"Имя: {candidate.first_name}")
    console.print(f"Фамилия: {candidate.last_name}")
    if candidate.phone:
        console.print(f"Телефон: {candidate.phone}")
    if candidate.birth_date:
        console.print(f"Дата рождения: {candidate.birth_date.strftime('%Y-%m-%d')}")
    if candidate.sex:
        sex_name = "Мужской" if candidate.sex == CandidateSex.MALE else "Женский"
        console.print(f"Пол: {sex_name}")
    console.print(f"Статус: {candidate.status.name}")
    if candidate.comments:
        console.print(f"Комментарии: {candidate.comments}")


def _register_candidate(
    use_cases: UseCases,
    console: Console,
    first_name: str,
    last_name: str,
    phone: Optional[str] = None,
    birth_date: Optional[str] = None,
    sex: Optional[str] = None,
    comments: Optional[str] = None,
) -> None:
    """Регистрирует кандидата с валидацией и обработкой ошибок"""
    try:
        parsed_birth_date = _parse_birth_date(birth_date, console)
        parsed_sex = _parse_sex(sex, console)

        candidate = Candidate(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            birth_date=parsed_birth_date,
            sex=parsed_sex,
            status=CandidateStatus.REGISTERED,
            comments=comments,
        )

        candidate_id = use_cases.register_candidate(candidate)
        console.print(f"[green]Кандидат [gray]{first_name} {last_name}[/gray] успешно зарегистрирован с ID: {candidate_id}[/green]")

    except Exception as e:
        console.print(f"[red]Ошибка при регистрации кандидата: {str(e)}[/red]")
        raise typer.Exit(1)


def create_cli_app(use_cases: UseCases) -> typer.Typer:
    """Создает CLI приложение с инжектированными зависимостями"""
    app = typer.Typer(help="HR Management System - CLI для управления кандидатами")
    console = Console()

    @app.callback()
    def main_callback():
        """
        HR Management System - CLI для управления кандидатами
        """
        pass

    @app.command()
    def add(
        first_name: str = typer.Option(..., "--first-name", "-f", help="Имя кандидата"),
        last_name: str = typer.Option(..., "--last-name", "-l", help="Фамилия кандидата"),
        phone: Optional[str] = typer.Option(None, "--phone", "-p", help="Контактный телефон"),
        birth_date: Optional[str] = typer.Option(None, "--birth-date", "-b", help="Дата рождения (YYYY-MM-DD)"),
        sex: Optional[str] = typer.Option(None, "--sex", "-s", help="Пол (M/F)"),
        comments: Optional[str] = typer.Option(None, "--comments", "-c", help="Комментарии"),
    ):
        """
        Регистрирует нового кандидата в системе.
        """
        _register_candidate(
            use_cases=use_cases,
            console=console,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            birth_date=birth_date,
            sex=sex,
            comments=comments,
        )

    @app.command()
    def add_interactive():
        """
        Регистрирует нового кандидата в интерактивном режиме.
        """
        console.print("[bold cyan]Регистрация нового кандидата[/bold cyan]")
        console.print()

        # Обязательные поля
        first_name = Prompt.ask("Имя", default="").strip()
        while not first_name:
            console.print("[red]Имя не может быть пустым[/red]")
            first_name = Prompt.ask("Имя", default="").strip()

        last_name = Prompt.ask("Фамилия", default="").strip()
        while not last_name:
            console.print("[red]Фамилия не может быть пустой[/red]")
            last_name = Prompt.ask("Фамилия", default="").strip()

        # Опциональные поля
        phone_input = Prompt.ask("Телефон (необязательно, Enter для пропуска)", default="").strip()
        phone = phone_input if phone_input else None

        birth_date = None
        while True:
            date_str = Prompt.ask("Дата рождения (YYYY-MM-DD, Enter для пропуска)", default="").strip()
            if not date_str:
                break
            try:
                birth_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                break
            except ValueError:
                console.print("[red]Неверный формат даты. Используйте YYYY-MM-DD[/red]")

        sex = None
        while True:
            sex_input = Prompt.ask("Пол (M/F, Enter для пропуска)", default="").strip().upper()
            if not sex_input:
                break
            if sex_input in ("M", "F"):
                sex = sex_input
                break
            else:
                console.print("[red]Используйте M для мужского или F для женского пола[/red]")

        comments_input = Prompt.ask("Комментарии (Enter для пропуска)", default="").strip()
        comments = comments_input if comments_input else None

        console.print()
        _register_candidate(
            use_cases=use_cases,
            console=console,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            birth_date=birth_date.strftime("%Y-%m-%d") if birth_date else None,
            sex=sex,
            comments=comments,
        )

    @app.command()
    def get(
        candidate_id: int = typer.Option(..., "--id", "-i", help="ID кандидата"),
    ):
        """
        Получает информацию о кандидате по ID.
        """
        try:
            candidate = use_cases.get_candidate(candidate_id)
            _format_candidate(candidate, console)
        except Exception as e:
            console.print(f"[red]Ошибка при получении кандидата:\n{str(e)}[/red]")
            raise typer.Exit(1)

    return app


def main():
    """Точка входа в CLI приложение - Composition Root"""
    use_cases = UseCases()
    app = create_cli_app(use_cases)
    app()


if __name__ == "__main__":
    main()

