from flask_sqlalchemy.record_queries import get_recorded_queries


def sql_debug(response):
    queries = list(get_recorded_queries())
    query_str = ""
    total_duration = 0.0
    for q in queries:
        total_duration += q.duration
        stmt = str(q.statement % q.parameters).replace("\n", "\n       ")
        query_str += f"Query: {stmt}\nDuration: {round(q.duration * 1000, 2)}ms\n\n"

    print("=" * 80)
    number = len(queries)
    period = round(total_duration * 1000, 2)
    print(f" SQL Queries - {number} Queries Executed in {period}ms")
    print("=" * 80)
    print(query_str.rstrip("\n"))
    print("=" * 80 + "\n")

    return response
