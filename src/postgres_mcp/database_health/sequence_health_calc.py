from dataclasses import dataclass

from ..sql import SqlDriver


@dataclass
class SequenceMetrics:
    schema: str
    table: str
    column: str
    sequence: str
    column_type: str
    last_value: int
    max_value: int
    is_healthy: bool
    readable: bool = True

    @property
    def percent_used(self) -> float:
        """Calculate what percentage of the sequence has been used."""
        return (self.last_value / self.max_value) * 100 if self.max_value else 0


class SequenceHealthCalc:
    def __init__(self, sql_driver: SqlDriver, threshold: float = 0.9):
        """Initialize sequence health calculator.

        Args:
            sql_driver: SQL driver for database access
            threshold: Percentage (as decimal) of sequence usage that triggers warning
        """
        self.sql_driver = sql_driver
        self.threshold = threshold

    async def sequence_danger_check(self) -> str:
        """Check if any sequences are approaching their maximum values."""
        metrics = await self._get_sequence_metrics()

        if not metrics:
            return "No sequences found in the database."

        # Sort by remaining values ascending to show most critical first
        metrics.sort(key=lambda x: x.max_value - x.last_value)

        unhealthy = [m for m in metrics if not m.is_healthy]
        if not unhealthy:
            return "All sequences have healthy usage levels."

        result = ["Sequences approaching maximum value:"]
        for metric in unhealthy:
            remaining = metric.max_value - metric.last_value
            result.append(
                f"Sequence '{metric.schema}.{metric.sequence}' used for {metric.table}.{metric.column} "
                f"has used {metric.percent_used:.1f}% of available values "
                f"({metric.last_value:,} of {metric.max_value:,}, {remaining:,} remaining)"
            )
        return "\n".join(result)

    async def _get_sequence_metrics(self) -> list[SequenceMetrics]:
        """Get metrics for sequences in the database."""
        # Use a single robust query to get all sequences and their usage via pg_depend
        query = """
            WITH sequence_usage AS (
                -- Sequences owned by columns (SERIAL, IDENTITY)
                SELECT
                    s.oid AS sequence_oid,
                    n.nspname AS table_schema,
                    c.relname AS table_name,
                    a.attname AS column_name,
                    format_type(a.atttypid, a.atttypmod) AS column_type
                FROM pg_class s
                JOIN pg_depend d ON d.objid = s.oid AND d.deptype IN ('a', 'i')
                JOIN pg_class c ON c.oid = d.refobjid
                JOIN pg_namespace n ON n.oid = c.relnamespace
                JOIN pg_attribute a ON a.attrelid = c.oid AND a.attnum = d.refobjsubid
                WHERE s.relkind = 'S'

                UNION

                -- Sequences used in DEFAULT expressions
                SELECT
                    s.oid AS sequence_oid,
                    n.nspname AS table_schema,
                    c.relname AS table_name,
                    a.attname AS column_name,
                    format_type(a.atttypid, a.atttypmod) AS column_type
                FROM pg_attrdef ad
                JOIN pg_attribute a ON a.attrelid = ad.adrelid AND a.attnum = ad.adnum
                JOIN pg_class c ON c.oid = a.attrelid
                JOIN pg_namespace n ON n.oid = c.relnamespace
                JOIN pg_depend d ON d.objid = ad.oid AND d.classid = 'pg_attrdef'::regclass AND d.refclassid = 'pg_class'::regclass
                JOIN pg_class s ON s.oid = d.refobjid AND s.relkind = 'S'
            )
            SELECT
                ps.schemaname AS schema,
                ps.sequencename AS sequence,
                ps.last_value,
                ps.max_value,
                COALESCE(u.column_type, ps.data_type::text) AS column_type,
                COALESCE(u.table_name, '') AS table_name,
                COALESCE(u.column_name, '') AS column_name,
                has_sequence_privilege(quote_ident(ps.schemaname) || '.' || quote_ident(ps.sequencename), 'SELECT') as readable
            FROM pg_sequences ps
            JOIN pg_class s ON s.relname = ps.sequencename
                AND s.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = ps.schemaname)
            LEFT JOIN sequence_usage u ON u.sequence_oid = s.oid
            WHERE ps.schemaname NOT IN ('information_schema', 'pg_catalog')
            AND ps.schemaname NOT LIKE 'pg\\_temp\\_%'
        """

        sequences = await self.sql_driver.execute_query(query)

        if not sequences:
            return []

        # Process each sequence
        sequence_metrics = []
        for seq_row in sequences:
            seq = dict(seq_row.cells)

            # If we can't read it, we skip health check for it
            if not seq["readable"]:
                continue

            # Handle sequences that haven't been used yet (last_value is None)
            last_val = seq["last_value"] if seq["last_value"] is not None else 0
            max_val = seq["max_value"]

            # Avoid division by zero
            if not max_val:
                continue

            sequence_metrics.append(
                SequenceMetrics(
                    schema=seq["schema"],
                    table=seq["table_name"],
                    column=seq["column_name"],
                    sequence=seq["sequence"],
                    column_type=seq["column_type"],
                    last_value=last_val,
                    max_value=max_val,
                    readable=seq["readable"],
                    is_healthy=(last_val / max_val) <= self.threshold,
                )
            )

        return sequence_metrics
