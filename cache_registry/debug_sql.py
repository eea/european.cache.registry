from flask_sqlalchemy import get_debug_queries
from instance.settings import DEBUG


def sql_debug(response):
    queries = list(get_debug_queries())
    query_str = ""
    total_duration = 0.0
    for q in queries:
        total_duration += q.duration
        stmt = str(q.statement % q.parameters).replace("\n", "\n       ")
        query_str += "Query: {0}\nDuration: {1}ms\n\n".format(
            stmt, round(q.duration * 1000, 2)
        )

    print("=" * 80)
    print(
        " SQL Queries - {number} Queries Executed in {period}ms".format(
            number=len(queries), period=round(total_duration * 1000, 2)
        )
    )
    print("=" * 80)
    print(query_str.rstrip("\n"))
    print("=" * 80 + "\n")

    return response
