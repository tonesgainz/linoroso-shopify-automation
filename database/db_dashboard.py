"""
Database Dashboard
Simple CLI dashboard to view database statistics and data
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_helper import db
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich import box
import json
from datetime import datetime

console = Console()


def show_database_stats():
    """Show overall database statistics"""
    console.print("\n[bold cyan]📊 Database Statistics[/bold cyan]\n")

    try:
        # Content stats
        content_query = """
            SELECT
                content_type,
                status,
                COUNT(*) as count
            FROM generated_content
            GROUP BY content_type, status
        """
        content_stats = db.execute_query(content_query)

        if content_stats:
            table = Table(title="Content Statistics", box=box.ROUNDED)
            table.add_column("Type", style="cyan")
            table.add_column("Status", style="magenta")
            table.add_column("Count", style="green", justify="right")

            for stat in content_stats:
                table.add_row(
                    stat['content_type'],
                    stat['status'],
                    str(stat['count'])
                )

            console.print(table)
        else:
            console.print("[yellow]No content data yet[/yellow]")

        # Keywords stats
        keyword_query = "SELECT COUNT(*) as total FROM keywords"
        keyword_stats = db.execute_query(keyword_query)
        console.print(f"\n[cyan]Keywords tracked:[/cyan] {keyword_stats[0]['total']}")

        # Products stats
        product_query = "SELECT COUNT(*) as total FROM products"
        product_stats = db.execute_query(product_query)
        console.print(f"[cyan]Products:[/cyan] {product_stats[0]['total']}")

        # Task executions
        task_query = """
            SELECT status, COUNT(*) as count
            FROM task_execution_log
            GROUP BY status
        """
        task_stats = db.execute_query(task_query)

        if task_stats:
            console.print("\n[bold cyan]Task Executions:[/bold cyan]")
            for stat in task_stats:
                console.print(f"  {stat['status']}: {stat['count']}")

    except Exception as e:
        console.print(f"[red]Error fetching stats: {e}[/red]")


def show_recent_content(limit=10):
    """Show recently generated content"""
    console.print(f"\n[bold cyan]📝 Recent Content (Last {limit})[/bold cyan]\n")

    try:
        content = db.get_recent_content(limit=limit)

        if not content:
            console.print("[yellow]No content found[/yellow]")
            return

        table = Table(box=box.ROUNDED)
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Type", style="magenta", width=15)
        table.add_column("Title", style="white", width=40)
        table.add_column("Status", style="green", width=10)
        table.add_column("Words", style="yellow", justify="right", width=8)
        table.add_column("Created", style="blue", width=12)

        for item in content:
            # Handle datetime objects
            created = item['created_at']
            if isinstance(created, datetime):
                created_str = created.strftime("%Y-%m-%d")
            else:
                created_str = str(created)[:10]

            table.add_row(
                str(item['id']),
                item['content_type'] or 'N/A',
                (item['title'] or 'Untitled')[:40],
                item['status'] or 'draft',
                str(item['word_count'] or 0),
                created_str
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error fetching content: {e}[/red]")


def show_top_keywords(limit=20):
    """Show top keywords by search volume"""
    console.print(f"\n[bold cyan]🔍 Top Keywords (Top {limit})[/bold cyan]\n")

    try:
        keywords = db.get_top_keywords(limit=limit)

        if not keywords:
            console.print("[yellow]No keywords found[/yellow]")
            return

        table = Table(box=box.ROUNDED)
        table.add_column("Keyword", style="cyan", width=30)
        table.add_column("Volume", style="green", justify="right", width=10)
        table.add_column("Difficulty", style="yellow", justify="right", width=12)
        table.add_column("Status", style="magenta", width=12)
        table.add_column("Category", style="blue", width=20)

        for kw in keywords:
            table.add_row(
                kw['keyword'][:30],
                str(kw['search_volume'] or 0),
                str(kw['difficulty_score'] or 0),
                kw['status'] or 'researching',
                (kw['category'] or 'N/A')[:20]
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error fetching keywords: {e}[/red]")


def show_recent_tasks(limit=10):
    """Show recent task executions"""
    console.print(f"\n[bold cyan]⚙️  Recent Task Executions (Last {limit})[/bold cyan]\n")

    try:
        tasks = db.get_recent_task_executions(limit=limit)

        if not tasks:
            console.print("[yellow]No task executions found[/yellow]")
            return

        table = Table(box=box.ROUNDED)
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Task Name", style="white", width=30)
        table.add_column("Type", style="magenta", width=20)
        table.add_column("Status", style="green", width=10)
        table.add_column("Items", style="yellow", justify="right", width=8)
        table.add_column("Duration", style="blue", justify="right", width=10)
        table.add_column("Started", style="dim", width=20)

        for task in tasks:
            # Format start time
            start_time = task['start_time']
            if isinstance(start_time, datetime):
                start_str = start_time.strftime("%Y-%m-%d %H:%M")
            else:
                start_str = str(start_time)[:16]

            # Status color
            status = task['status']
            if status == 'completed':
                status_str = f"[green]{status}[/green]"
            elif status == 'failed':
                status_str = f"[red]{status}[/red]"
            elif status == 'running':
                status_str = f"[yellow]{status}[/yellow]"
            else:
                status_str = status

            duration = task['duration_seconds']
            duration_str = f"{duration}s" if duration else "N/A"

            table.add_row(
                str(task['id']),
                task['task_name'][:30],
                task['task_type'],
                status_str,
                str(task['items_processed'] or 0),
                duration_str,
                start_str
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error fetching tasks: {e}[/red]")


def show_api_usage(days=30):
    """Show API usage summary"""
    console.print(f"\n[bold cyan]🔌 API Usage (Last {days} days)[/bold cyan]\n")

    try:
        usage = db.get_api_usage_summary(days=days)

        if not usage:
            console.print("[yellow]No API usage data[/yellow]")
            return

        table = Table(box=box.ROUNDED)
        table.add_column("API", style="cyan", width=20)
        table.add_column("Requests", style="green", justify="right", width=12)
        table.add_column("Tokens", style="yellow", justify="right", width=12)
        table.add_column("Cost ($)", style="magenta", justify="right", width=12)

        total_requests = 0
        total_tokens = 0
        total_cost = 0.0

        for api in usage:
            requests = api['total_requests'] or 0
            tokens = api['total_tokens'] or 0
            cost = float(api['total_cost'] or 0)

            total_requests += requests
            total_tokens += tokens
            total_cost += cost

            table.add_row(
                api['api_name'],
                f"{requests:,}",
                f"{tokens:,}" if tokens else "N/A",
                f"{cost:.2f}" if cost else "0.00"
            )

        # Add totals row
        table.add_section()
        table.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold]{total_requests:,}[/bold]",
            f"[bold]{total_tokens:,}[/bold]" if total_tokens else "[bold]N/A[/bold]",
            f"[bold]${total_cost:.2f}[/bold]"
        )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error fetching API usage: {e}[/red]")


def show_content_performance(days=30):
    """Show content performance summary"""
    console.print(f"\n[bold cyan]📈 Content Performance (Last {days} days)[/bold cyan]\n")

    try:
        summary = db.get_content_performance_summary(days=days)

        if not summary:
            console.print("[yellow]No performance data[/yellow]")
            return

        # Create info panel
        info = f"""
[cyan]Total Content:[/cyan] {summary.get('total_content', 0)}
[cyan]Published:[/cyan] {summary.get('published_content', 0)}
[cyan]Total Views:[/cyan] {summary.get('total_views', 0):,}
[cyan]Total Clicks:[/cyan] {summary.get('total_clicks', 0):,}
[cyan]Total Conversions:[/cyan] {summary.get('total_conversions', 0):,}
[cyan]Total Revenue:[/cyan] ${summary.get('total_revenue', 0):,.2f}
        """

        panel = Panel(info, title="Performance Summary", border_style="cyan")
        console.print(panel)

        # Top performing content
        console.print("\n[bold]Top Performing Content:[/bold]\n")
        top_content = db.get_top_performing_content(limit=5)

        if top_content:
            table = Table(box=box.ROUNDED)
            table.add_column("Title", style="cyan", width=40)
            table.add_column("Type", style="magenta", width=15)
            table.add_column("Views", style="green", justify="right", width=10)
            table.add_column("Clicks", style="yellow", justify="right", width=10)
            table.add_column("Conv.", style="blue", justify="right", width=8)
            table.add_column("Revenue", style="green", justify="right", width=12)

            for content in top_content:
                table.add_row(
                    (content['title'] or 'Untitled')[:40],
                    content['content_type'] or 'N/A',
                    f"{content['total_views'] or 0:,}",
                    f"{content['total_clicks'] or 0:,}",
                    str(content['total_conversions'] or 0),
                    f"${content['total_revenue'] or 0:,.2f}"
                )

            console.print(table)

    except Exception as e:
        console.print(f"[red]Error fetching performance: {e}[/red]")


def show_system_settings():
    """Show system settings"""
    console.print("\n[bold cyan]⚙️  System Settings[/bold cyan]\n")

    try:
        query = "SELECT * FROM system_settings ORDER BY setting_key"
        settings = db.execute_query(query)

        if not settings:
            console.print("[yellow]No settings found[/yellow]")
            return

        table = Table(box=box.ROUNDED)
        table.add_column("Setting", style="cyan", width=30)
        table.add_column("Value", style="green", width=20)
        table.add_column("Type", style="magenta", width=10)
        table.add_column("Description", style="dim", width=40)

        for setting in settings:
            table.add_row(
                setting['setting_key'],
                str(setting['setting_value']),
                setting['setting_type'],
                (setting['description'] or 'N/A')[:40]
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error fetching settings: {e}[/red]")


def show_menu():
    """Show interactive menu"""
    console.clear()
    console.print("\n[bold magenta]═══════════════════════════════════════[/bold magenta]")
    console.print("[bold magenta]   Linoroso Database Dashboard   [/bold magenta]")
    console.print("[bold magenta]═══════════════════════════════════════[/bold magenta]\n")

    console.print("[cyan]1.[/cyan] Database Statistics")
    console.print("[cyan]2.[/cyan] Recent Content")
    console.print("[cyan]3.[/cyan] Top Keywords")
    console.print("[cyan]4.[/cyan] Recent Tasks")
    console.print("[cyan]5.[/cyan] API Usage")
    console.print("[cyan]6.[/cyan] Content Performance")
    console.print("[cyan]7.[/cyan] System Settings")
    console.print("[cyan]8.[/cyan] Show All")
    console.print("[cyan]0.[/cyan] Exit\n")


def main():
    """Main interactive dashboard"""
    while True:
        show_menu()
        choice = console.input("[bold cyan]Select option:[/bold cyan] ")

        console.clear()

        if choice == '1':
            show_database_stats()
        elif choice == '2':
            show_recent_content()
        elif choice == '3':
            show_top_keywords()
        elif choice == '4':
            show_recent_tasks()
        elif choice == '5':
            show_api_usage()
        elif choice == '6':
            show_content_performance()
        elif choice == '7':
            show_system_settings()
        elif choice == '8':
            show_database_stats()
            show_recent_content()
            show_top_keywords()
            show_recent_tasks()
            show_api_usage()
            show_content_performance()
            show_system_settings()
        elif choice == '0':
            console.print("\n[bold green]Goodbye! 👋[/bold green]\n")
            break
        else:
            console.print("[red]Invalid option![/red]")

        console.input("\n[dim]Press Enter to continue...[/dim]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[bold green]Goodbye! 👋[/bold green]\n")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        import traceback
        traceback.print_exc()
