"""CLI приложение для управления кандидатами в HR системе"""
import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table

from hrm.core.application import UseCases
from hrm.core.model import Candidate, CandidateSex, CandidateStatus
from hrm.core.persistence import SqliteCandidateRepository


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

    @app.command()
    def list():
        """
        Выводит список всех кандидатов.
        """
        try:
            candidates = use_cases.get_all_candidates()
            
            if not candidates:
                console.print("[yellow]Кандидаты не найдены[/yellow]")
                return
            
            table = Table(title="Список кандидатов", show_header=True, header_style="bold cyan")
            table.add_column("ID", style="dim", width=6)
            table.add_column("Имя", width=20)
            table.add_column("Фамилия", width=20)
            table.add_column("Телефон", width=15)
            table.add_column("Дата рождения", width=12)
            table.add_column("Пол", width=8)
            table.add_column("Статус", width=12)
            
            for candidate in candidates:
                phone = candidate.phone or "-"
                birth_date = candidate.birth_date.strftime("%Y-%m-%d") if candidate.birth_date else "-"
                sex = "М" if candidate.sex == CandidateSex.MALE else ("Ж" if candidate.sex == CandidateSex.FEMALE else "-")
                status = candidate.status.name
                
                table.add_row(
                    str(candidate.id),
                    candidate.first_name,
                    candidate.last_name,
                    phone,
                    birth_date,
                    sex,
                    status
                )
            
            console.print(table)
            console.print(f"\n[dim]Всего кандидатов: {len(candidates)}[/dim]")
            
        except Exception as e:
            console.print(f"[red]Ошибка при получении списка кандидатов:\n{str(e)}[/red]")
            raise typer.Exit(1)

    @app.command()
    def delete(
        candidate_id: int = typer.Option(..., "--id", "-i", help="ID кандидата"),
        force: bool = typer.Option(False, "--force", "-f", help="Удалить без подтверждения"),
    ):
        """
        Удаляет кандидата по ID.
        """
        try:
            # Получаем информацию о кандидате для отображения
            candidate = use_cases.get_candidate(candidate_id)
            
            # Показываем информацию о кандидате
            console.print(f"[yellow]Кандидат для удаления:[/yellow]")
            console.print(f"ID: {candidate.id}")
            console.print(f"Имя: {candidate.first_name} {candidate.last_name}")
            console.print()
            
            # Запрашиваем подтверждение, если не указан флаг --force
            if not force:
                if not Confirm.ask("[red]Вы уверены, что хотите удалить этого кандидата?[/red]", default=False):
                    console.print("[yellow]Удаление отменено[/yellow]")
                    return
            
            # Удаляем кандидата
            use_cases.delete_candidate(candidate_id)
            console.print(f"[green]Кандидат [gray]{candidate.first_name} {candidate.last_name}[/gray] успешно удален[/green]")
            
        except ValueError as e:
            console.print(f"[red]Ошибка: {str(e)}[/red]")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]Ошибка при удалении кандидата:\n{str(e)}[/red]")
            raise typer.Exit(1)

    @app.command()
    def edit(
        candidate_id: int = typer.Option(..., "--id", "-i", help="ID кандидата"),
        first_name: Optional[str] = typer.Option(None, "--first-name", "-f", help="Имя кандидата"),
        last_name: Optional[str] = typer.Option(None, "--last-name", "-l", help="Фамилия кандидата"),
        phone: Optional[str] = typer.Option(None, "--phone", "-p", help="Контактный телефон"),
        birth_date: Optional[str] = typer.Option(None, "--birth-date", "-b", help="Дата рождения (YYYY-MM-DD)"),
        sex: Optional[str] = typer.Option(None, "--sex", "-s", help="Пол (M/F)"),
        comments: Optional[str] = typer.Option(None, "--comments", "-c", help="Комментарии"),
    ):
        """
        Редактирует существующего кандидата.
        Статус и ID кандидата изменить нельзя.
        """
        try:
            # Получаем существующего кандидата
            existing_candidate = use_cases.get_candidate(candidate_id)
            
            # Парсим опциональные параметры
            parsed_birth_date = None
            if birth_date:
                parsed_birth_date = _parse_birth_date(birth_date, console)
            
            parsed_sex = None
            if sex:
                parsed_sex = _parse_sex(sex, console)
            
            # Создаем обновленный кандидат, сохраняя существующие значения для не указанных полей
            updated_candidate = existing_candidate.model_copy(update={
                "first_name": first_name if first_name is not None else existing_candidate.first_name,
                "last_name": last_name if last_name is not None else existing_candidate.last_name,
                "phone": phone if phone is not None else existing_candidate.phone,
                "birth_date": parsed_birth_date if parsed_birth_date is not None else existing_candidate.birth_date,
                "sex": parsed_sex if parsed_sex is not None else existing_candidate.sex,
                "comments": comments if comments is not None else existing_candidate.comments,
                # ID и статус не изменяются - они сохраняются в методе edit_candidate
            })
            
            # Редактируем кандидата
            edited_candidate = use_cases.edit_candidate(updated_candidate)
            
            console.print(f"[green]Кандидат [gray]{edited_candidate.first_name} {edited_candidate.last_name}[/gray] успешно обновлен[/green]")
            _format_candidate(edited_candidate, console)
            
        except ValueError as e:
            console.print(f"[red]Ошибка: {str(e)}[/red]")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]Ошибка при редактировании кандидата:\n{str(e)}[/red]")
            raise typer.Exit(1)

    @app.command()
    def edit_interactive():
        """
        Редактирует существующего кандидата в интерактивном режиме.
        Статус и ID кандидата изменить нельзя.
        """
        try:
            console.print("[bold cyan]Редактирование кандидата[/bold cyan]")
            console.print()
            
            # Запрашиваем ID кандидата
            candidate_id_input = Prompt.ask("ID кандидата", default="").strip()
            if not candidate_id_input:
                console.print("[red]ID кандидата не может быть пустым[/red]")
                raise typer.Exit(1)
            
            try:
                candidate_id = int(candidate_id_input)
            except ValueError:
                console.print("[red]ID должен быть числом[/red]")
                raise typer.Exit(1)
            
            # Получаем существующего кандидата
            existing_candidate = use_cases.get_candidate(candidate_id)
            
            console.print()
            console.print("[dim]Текущие данные кандидата:[/dim]")
            _format_candidate(existing_candidate, console)
            console.print()
            console.print("[yellow]Введите новые значения (Enter для сохранения текущего значения):[/yellow]")
            console.print()
            
            # Редактируем обязательные поля
            first_name_input = Prompt.ask(
                "Имя",
                default=existing_candidate.first_name
            ).strip()
            while not first_name_input:
                console.print("[red]Имя не может быть пустым[/red]")
                first_name_input = Prompt.ask(
                    "Имя",
                    default=existing_candidate.first_name
                ).strip()
            
            last_name_input = Prompt.ask(
                "Фамилия",
                default=existing_candidate.last_name
            ).strip()
            while not last_name_input:
                console.print("[red]Фамилия не может быть пустой[/red]")
                last_name_input = Prompt.ask(
                    "Фамилия",
                    default=existing_candidate.last_name
                ).strip()
            
            # Редактируем опциональные поля
            phone_default = existing_candidate.phone or ""
            phone_input = Prompt.ask("Телефон (Enter для сохранения текущего)", default=phone_default).strip()
            phone = phone_input if phone_input else existing_candidate.phone
            
            birth_date = existing_candidate.birth_date
            while True:
                date_default = existing_candidate.birth_date.strftime("%Y-%m-%d") if existing_candidate.birth_date else ""
                date_str = Prompt.ask("Дата рождения (YYYY-MM-DD, Enter для сохранения текущего)", default=date_default).strip()
                if not date_str:
                    break
                try:
                    birth_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                    break
                except ValueError:
                    console.print("[red]Неверный формат даты. Используйте YYYY-MM-DD[/red]")
            
            sex = existing_candidate.sex
            while True:
                sex_default = ""
                if existing_candidate.sex == CandidateSex.MALE:
                    sex_default = "M"
                elif existing_candidate.sex == CandidateSex.FEMALE:
                    sex_default = "F"
                
                sex_input = Prompt.ask("Пол (M/F, Enter для сохранения текущего)", default=sex_default).strip().upper()
                if not sex_input:
                    break
                if sex_input in ("M", "F"):
                    sex = CandidateSex.MALE if sex_input == "M" else CandidateSex.FEMALE
                    break
                else:
                    console.print("[red]Используйте M для мужского или F для женского пола[/red]")
            
            comments_default = existing_candidate.comments or ""
            comments_input = Prompt.ask("Комментарии (Enter для сохранения текущего)", default=comments_default).strip()
            comments = comments_input if comments_input else existing_candidate.comments
            
            # Создаем обновленного кандидата
            updated_candidate = existing_candidate.model_copy(update={
                "first_name": first_name_input,
                "last_name": last_name_input,
                "phone": phone,
                "birth_date": birth_date,
                "sex": sex,
                "comments": comments,
            })
            
            # Редактируем кандидата
            console.print()
            edited_candidate = use_cases.edit_candidate(updated_candidate)
            
            console.print(f"[green]Кандидат [gray]{edited_candidate.first_name} {edited_candidate.last_name}[/gray] успешно обновлен[/green]")
            console.print()
            _format_candidate(edited_candidate, console)
            
        except ValueError as e:
            console.print(f"[red]Ошибка: {str(e)}[/red]")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]Ошибка при редактировании кандидата:\n{str(e)}[/red]")
            raise typer.Exit(1)

    @app.command()
    def clear(
        force: bool = typer.Option(False, "--force", "-f", help="Очистить без подтверждения"),
    ):
        """
        Очищает репозиторий от всех данных.
        Используется для приемочных тестов.
        """
        try:
            # Запрашиваем подтверждение, если не указан флаг --force
            if not force:
                if not Confirm.ask("[red]Вы уверены, что хотите удалить всех кандидатов?[/red]", default=False):
                    console.print("[yellow]Очистка отменена[/yellow]")
                    return
            
            # Очищаем репозиторий
            use_cases.clear_all_candidates()
            console.print("[green]Репозиторий успешно очищен[/green]")
            
        except Exception as e:
            console.print(f"[red]Ошибка при очистке репозитория:\n{str(e)}[/red]")
            raise typer.Exit(1)

    @app.command()
    def count():
        """
        Выводит общее количество кандидатов в системе.
        """
        try:
            total = use_cases.get_total_candidates()
            console.print(f"[bold cyan]Общее количество кандидатов: {total}[/bold cyan]")
        except Exception as e:
            console.print(f"[red]Ошибка при получении количества кандидатов:\n{str(e)}[/red]")
            raise typer.Exit(1)

    return app


def main():
    """Точка входа в CLI приложение - Composition Root"""
    repository = SqliteCandidateRepository()
    use_cases = UseCases(repository)
    app = create_cli_app(use_cases)
    app()


if __name__ == "__main__":
    main()

