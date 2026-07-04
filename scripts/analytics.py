#!/usr/bin/env python3
"""
Agent Analytics Script
Generates reports: token usage, response times, resolution rates, top issues.
Output: JSON report to stdout or file.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime

import asyncpg

POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://helpdesk:***@postgres:5432/helpdesk")


async def get_token_usage(pool, hours: int = 24) -> dict:
    """Get token usage statistics."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT
                COALESCE(SUM(tokens_input), 0) as total_input,
                COALESCE(SUM(tokens_output), 0) as total_output,
                COALESCE(SUM(tokens_total), 0) as total,
                COALESCE(SUM(estimated_cost_usd), 0) as cost,
                COUNT(*) as requests
            FROM cost_tracking
            WHERE created_at >= NOW() - INTERVAL '%s hours'
            """,
            hours,
        )
        return {
            "input_tokens": row["total_input"],
            "output_tokens": row["total_output"],
            "total_tokens": row["total"],
            "estimated_cost_usd": float(row["cost"]),
            "requests": row["requests"],
        }


async def get_ticket_stats(pool, hours: int = 24) -> dict:
    """Get ticket statistics."""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT status, COUNT(*) as count
            FROM tickets
            WHERE created_at >= NOW() - INTERVAL '%s hours'
            GROUP BY status
            """,
            hours,
        )
        stats = {row["status"]: row["count"] for row in rows}

        total = sum(stats.values())
        resolved = stats.get("closed", 0) + stats.get("resolved", 0)
        resolution_rate = (resolved / total * 100) if total > 0 else 0

        return {
            "total": total,
            "by_status": stats,
            "resolution_rate": round(resolution_rate, 1),
        }


async def get_session_stats(pool, hours: int = 24) -> dict:
    """Get session statistics."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE active) as active,
                AVG(message_count) as avg_messages,
                AVG(EXTRACT(EPOCH FROM (expires_at - started_at))) as avg_duration_seconds
            FROM sessions
            WHERE started_at >= NOW() - INTERVAL '%s hours'
            """,
            hours,
        )
        return {
            "total_sessions": row["total"],
            "active_sessions": row["active"],
            "avg_messages_per_session": round(float(row["avg_messages"] or 0), 1),
            "avg_duration_minutes": round(float(row["avg_duration_seconds"] or 0) / 60, 1),
        }


async def get_rate_limit_stats(pool, hours: int = 24) -> dict:
    """Get rate limit hit statistics."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT COUNT(*) as hits
            FROM audit_log
            WHERE action = 'rate_limit_exceeded'
            AND created_at >= NOW() - INTERVAL '%s hours'
            """,
            hours,
        )
        return {"rate_limit_hits": row["hits"]}


async def get_top_issues(pool, hours: int = 168, limit: int = 10) -> list:
    """Get most common issue categories from audit log."""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT details->>'category' as category, COUNT(*) as count
            FROM audit_log
            WHERE action = 'ticket_created'
            AND created_at >= NOW() - INTERVAL '%s hours'
            AND details->>'category' IS NOT NULL
            GROUP BY category
            ORDER BY count DESC
            LIMIT %s
            """,
            hours,
            limit,
        )
        return [{"category": row["category"], "count": row["count"]} for row in rows]


async def generate_report(hours: int = 24) -> dict:
    """Generate full analytics report."""
    pool = await asyncpg.create_pool(POSTGRES_URL, min_size=1, max_size=5)
    if not pool:
        print("ERROR: Cannot connect to PostgreSQL", file=sys.stderr)
        sys.exit(1)

    try:
        tokens = await get_token_usage(pool, hours)
        tickets = await get_ticket_stats(pool, hours)
        sessions = await get_session_stats(pool, hours)
        rate_limits = await get_rate_limit_stats(pool, hours)
        top_issues = await get_top_issues(pool, hours)

        report = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "period_hours": hours,
            "tokens": tokens,
            "tickets": tickets,
            "sessions": sessions,
            "rate_limits": rate_limits,
            "top_issues": top_issues,
        }
        return report
    finally:
        await pool.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Helpdesk Agent Analytics")
    parser.add_argument("--hours", type=int, default=24, help="Report period in hours")
    parser.add_argument("--output", type=str, default=None, help="Output file (default: stdout)")
    parser.add_argument("--format", choices=["json", "text", "markdown"], default="text")
    args = parser.parse_args()

    report = asyncio.run(generate_report(args.hours))

    if args.format == "json":
        output = json.dumps(report, indent=2)
    elif args.format == "markdown":
        output = format_markdown(report)
    else:
        output = format_text(report)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report saved to {args.output}")
    else:
        print(output)


def format_text(report: dict) -> str:
    """Format report as colored text."""
    lines = [
        "═══════════════════════════════════════════",
        f"  Helpdesk Analytics ({report['period_hours']}h)",
        "═══════════════════════════════════════════",
        "",
        f"📊 Tokens: {report['tokens']['total_tokens']:,} ({report['tokens']['requests']} requests)",
        f"   Input:  {report['tokens']['input_tokens']:,}",
        f"   Output: {report['tokens']['output_tokens']:,}",
        f"   Cost:   ${report['tokens']['estimated_cost_usd']:.4f}",
        "",
        f"🎫 Tickets: {report['tickets']['total']} total",
    ]
    for status, count in report["tickets"].get("by_status", {}).items():
        lines.append(f"   {status}: {count}")
    lines.append(f"   Resolution rate: {report['tickets']['resolution_rate']}%")
    lines.extend([
        "",
        f"💬 Sessions: {report['sessions']['total_sessions']} ({report['sessions']['active_sessions']} active)",
        f"   Avg messages: {report['sessions']['avg_messages_per_session']}",
        f"   Avg duration: {report['sessions']['avg_duration_minutes']} min",
        "",
        f"🛡️ Rate limit hits: {report['rate_limits']['rate_limit_hits']}",
        "",
    ])
    if report.get("top_issues"):
        lines.append("🔥 Top Issues:")
        for issue in report["top_issues"][:5]:
            lines.append(f"   {issue['category']}: {issue['count']}")
    lines.append("")
    return "\n".join(lines)


def format_markdown(report: dict) -> str:
    """Format report as markdown."""
    lines = [
        f"# Helpdesk Analytics Report ({report['period_hours']}h)",
        "",
        f"Generated: {report['generated_at']}",
        "",
        "## Token Usage",
        f"- **Total tokens:** {report['tokens']['total_tokens']:,}",
        f"- **Input:** {report['tokens']['input_tokens']:,}",
        f"- **Output:** {report['tokens']['output_tokens']:,}",
        f"- **Estimated cost:** ${report['tokens']['estimated_cost_usd']:.4f}",
        f"- **Requests:** {report['tokens']['requests']}",
        "",
        "## Tickets",
        f"- **Total:** {report['tickets']['total']}",
        f"- **Resolution rate:** {report['tickets']['resolution_rate']}%",
    ]
    for status, count in report["tickets"].get("by_status", {}).items():
        lines.append(f"- **{status.capitalize()}:** {count}")
    lines.extend([
        "",
        "## Sessions",
        f"- **Total:** {report['sessions']['total_sessions']}",
        f"- **Active:** {report['sessions']['active_sessions']}",
        f"- **Avg messages:** {report['sessions']['avg_messages_per_session']}",
        f"- **Avg duration:** {report['sessions']['avg_duration_minutes']} min",
        "",
        "## Rate Limiting",
        f"- **Hits:** {report['rate_limits']['rate_limit_hits']}",
    ])
    if report.get("top_issues"):
        lines.extend(["", "## Top Issues"])
        for issue in report["top_issues"][:5]:
            lines.append(f"- {issue['category']}: {issue['count']}")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
