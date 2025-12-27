"""CLI приложение для управления кандидатами в HR системе"""
import datetime
from typing import Optional

import typer
from rich.console import Console

from hrm.core.application import UseCases
from hrm.core.model import Candidate, CandidateSex, CandidateStatus


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
        try:
            parsed_birth_date = None
            if birth_date:
                try:
                    parsed_birth_date = datetime.datetime.strptime(birth_date, "%Y-%m-%d")
                except ValueError:
                    console.print(f"[red]Ошибка: Неверный формат даты. Используйте YYYY-MM-DD[/red]")
                    raise typer.Exit(1)

            parsed_sex = None
            if sex:
                sex_upper = sex.upper()
                if sex_upper == "M":
                    parsed_sex = CandidateSex.MALE
                elif sex_upper == "F":
                    parsed_sex = CandidateSex.FEMALE
                else:
                    console.print(f"[red]Ошибка: Неверное значение пола. Используйте M или F[/red]")
                    raise typer.Exit(1)

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

    return app


def main():
    """Точка входа в CLI приложение - Composition Root"""
    use_cases = UseCases()
    app = create_cli_app(use_cases)
    app()


if __name__ == "__main__":
    main()

