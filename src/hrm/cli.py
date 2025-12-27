"""CLI приложение для управления кандидатами в HR системе"""
import typer
from rich.console import Console
from rich.table import Table

from hrm.core.application import AppController, CandidateNotFoundError, CandidateAlreadyExistsError
from hrm.core.models import CandidateCreate, CandidateStatus

app = typer.Typer(help="HR Management System - управление кандидатами")
console = Console()

# Initialize application controller
controller = AppController()


@app.command()
def register(
    first_name: str = typer.Option(None, "--first-name", "-f", help="Имя кандидата"),
    last_name: str = typer.Option(None, "--last-name", "-l", help="Фамилия кандидата"),
    email: str = typer.Option(None, "--email", "-e", help="Email кандидата"),
    phone: str = typer.Option(None, "--phone", "-p", help="Телефон кандидата"),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        "-i",
        help="Запустить в интерактивном (диалоговом) режиме",
    ),
):
    """
    Зарегистрировать нового кандидата.
    
    Можно использовать как с параметрами командной строки, так и в интерактивном режиме.
    Если параметры не указаны и флаг --interactive не указан, автоматически запускается интерактивный режим.
    """
    # Определяем, нужен ли интерактивный режим
    use_interactive = interactive or (first_name is None and last_name is None and email is None)
    
    if use_interactive:
        console.print("[bold cyan]Регистрация нового кандидата (интерактивный режим)[/bold cyan]\n")
        
        if first_name is None:
            first_name = typer.prompt("Введите имя кандидата")
        
        if last_name is None:
            last_name = typer.prompt("Введите фамилию кандидата")
        
        if email is None:
            email = typer.prompt("Введите email кандидата")
        
        if phone is None:
            phone = typer.prompt(
                "Введите телефон кандидата (необязательно)",
                default="",
                show_default=False,
            )
            phone = phone if phone else None
    
    # Валидация обязательных полей
    if not first_name:
        console.print("[red]Ошибка: Имя кандидата обязательно[/red]")
        raise typer.Exit(1)
    
    if not last_name:
        console.print("[red]Ошибка: Фамилия кандидата обязательна[/red]")
        raise typer.Exit(1)
    
    if not email:
        console.print("[red]Ошибка: Email кандидата обязателен[/red]")
        raise typer.Exit(1)
    
    # Register candidate through controller
    try:
        candidate_data = CandidateCreate(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
        )
        candidate = controller.register_candidate(candidate_data)
        console.print(f"[green]Кандидат успешно зарегистрирован![/green]")
        console.print(f"ID: {candidate.id}")
        console.print(f"Имя: {candidate.first_name} {candidate.last_name}")
        console.print(f"Email: {candidate.email}")
        if candidate.phone:
            console.print(f"Телефон: {candidate.phone}")
        console.print(f"Статус: {candidate.status.value}")
    except CandidateAlreadyExistsError:
        console.print(f"[red]Ошибка: Кандидат с email {email} уже существует[/red]")
        raise typer.Exit(1)


@app.command()
def approve(
    candidate_id: int = typer.Argument(..., help="ID кандидата для утверждения"),
):
    """
    Утвердить кандидата
    """
    try:
        candidate = controller.approve_candidate(candidate_id)
        console.print(f"[green]Кандидат с ID {candidate_id} успешно утвержден![/green]")
        console.print(f"Имя: {candidate.first_name} {candidate.last_name}")
        console.print(f"Email: {candidate.email}")
        console.print(f"Статус: {candidate.status.value}")
    except CandidateNotFoundError:
        console.print(f"[red]Ошибка: Кандидат с ID {candidate_id} не найден[/red]")
        raise typer.Exit(1)


@app.command()
def reject(
    candidate_id: int = typer.Argument(..., help="ID кандидата для отклонения"),
):
    """
    Отклонить кандидата
    """
    try:
        candidate = controller.reject_candidate(candidate_id)
        console.print(f"[yellow]Кандидат с ID {candidate_id} отклонен[/yellow]")
        console.print(f"Имя: {candidate.first_name} {candidate.last_name}")
        console.print(f"Email: {candidate.email}")
        console.print(f"Статус: {candidate.status.value}")
    except CandidateNotFoundError:
        console.print(f"[red]Ошибка: Кандидат с ID {candidate_id} не найден[/red]")
        raise typer.Exit(1)


@app.command()
def list(
    status: str = typer.Option(
        None,
        "--status",
        "-s",
        help="Фильтр по статусу (registered, approved, rejected)",
    ),
):
    """
    Показать список кандидатов
    """
    # Parse status filter
    status_filter = None
    if status:
        try:
            status_filter = CandidateStatus(status.lower())
        except ValueError:
            console.print(f"[red]Ошибка: Неверный статус '{status}'. Используйте: registered, approved, rejected[/red]")
            raise typer.Exit(1)
    
    # Get candidates through controller
    candidates = controller.list_candidates(status=status_filter)
    
    if not candidates:
        console.print("[yellow]Кандидаты не найдены[/yellow]")
        return
    
    # Display candidates in a table
    table = Table(title="Список кандидатов")
    table.add_column("ID", style="cyan")
    table.add_column("Имя", style="magenta")
    table.add_column("Фамилия", style="magenta")
    table.add_column("Email", style="green")
    table.add_column("Телефон", style="yellow")
    table.add_column("Статус", style="blue")
    
    for candidate in candidates:
        table.add_row(
            str(candidate.id),
            candidate.first_name,
            candidate.last_name,
            candidate.email,
            candidate.phone or "-",
            candidate.status.value,
        )
    
    console.print(table)


@app.command()
def show(
    candidate_id: int = typer.Argument(..., help="ID кандидата"),
):
    """
    Показать информацию о кандидате
    """
    try:
        candidate = controller.get_candidate(candidate_id)
        console.print(f"[bold cyan]Информация о кандидате[/bold cyan]\n")
        console.print(f"ID: {candidate.id}")
        console.print(f"Имя: {candidate.first_name}")
        console.print(f"Фамилия: {candidate.last_name}")
        console.print(f"Email: {candidate.email}")
        console.print(f"Телефон: {candidate.phone or 'не указан'}")
        console.print(f"Статус: {candidate.status.value}")
        console.print(f"Дата создания: {candidate.created_at}")
        console.print(f"Дата обновления: {candidate.updated_at}")
    except CandidateNotFoundError:
        console.print(f"[red]Ошибка: Кандидат с ID {candidate_id} не найден[/red]")
        raise typer.Exit(1)


def main():
    """Точка входа в CLI приложение"""
    app()


if __name__ == "__main__":
    main()

