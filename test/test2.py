from simplesqlite import SimpleSQLite
import json


table_name = "rank"
con = SimpleSQLite(r"database/database.sqlite", "w")

# create table -----
data_matrix = [[0, 0, 0, 0]]

"""with open("levels.json", "r") as f:
    data = json.load(f)

    for i in data:
        temp = []
        temp.append(i)
        for val in data[i].values():
            temp.append(val)

        data_matrix.append(temp)

print(data_matrix)"""

con.create_table_from_data_matrix(
    table_name,
    ["userid", "xp", "rank", "total_xp"],
    data_matrix,
)

# display values in the table -----
print("records:")
result = con.select(select="*", table_name=table_name)
for record in result.fetchall():
    print(record)
    print(*record)
    print(type(record))
