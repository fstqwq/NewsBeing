#include "sqlite3.h"
#include "json/json.h"
#include <cassert>

using namespace std;

#include "sorted_index.h"

int worker_id, doc_count;
sqlite3* db_connection;

void count_doc() {
    sqlite3_stmt *stmt;
    sqlite3_prepare_v2(db_connection, "SELECT COUNT(*) FROM documents", -1, &stmt, NULL);
    sqlite3_step(stmt);
    doc_count = sqlite3_column_int(stmt, 0);
    fprintf(stderr, "count = %d\n", doc_count);
    sqlite3_finalize(stmt);
}

int init(int id, const char* dbfile) {
    fprintf(stderr, "init %d %s\n", id, dbfile);
    sqlite3 *db;
    char *zErrMsg = 0;
    int rc;
    rc = sqlite3_open(dbfile, &db);
    if (rc) {
        fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(db));
        return 1;
    }
    worker_id = id;
    fprintf(stderr, "Opened database successfully\n");
    sqlite3_exec(db, "PRAGMA cache_size = 65536", NULL, NULL, NULL);
    sqlite3_exec(db, "PRAGMA page_size = 4096", NULL, NULL, NULL);
    sqlite3_exec(db, "PRAGMA temp_store = MEMORY", NULL, NULL, NULL);
    sqlite3_exec(db, "PRAGMA journal_mode = OFF", NULL, NULL, NULL);
    sqlite3_exec(db, "PRAGMA synchronous = OFF", NULL, NULL, NULL);
    db_connection = db;
    fprintf(stderr, "Pragma finished\n");
    count_doc();
    return 0;
}

void finalize() {
    sqlite3_close(db_connection);
}

SortedIndex get_sorted_index(const string& token) {
/*
    if token == '$':
        return SortedIndex([], tot, True)
    c, tot = cc
    c.execute("SELECT doc_id FROM inverted_index WHERE token=?", (token,))
    return SortedIndex(c.fetchall(), tot, False)
*/
    if (token == "$") {
        return SortedIndex(vector<int>(), doc_count, true);
    }

    sqlite3_stmt *stmt;
    
    int rc = sqlite3_prepare_v2(db_connection, "SELECT doc_id FROM inverted_index WHERE token=?", -1, &stmt, 0);
    if (rc != SQLITE_OK) {
        if (worker_id == 0) fprintf(stderr, "prepare error: %s\n", sqlite3_errmsg(db_connection));
        throw sqlite3_errmsg(db_connection);
    }
    rc = sqlite3_bind_text(stmt, 1, token.c_str(), -1, SQLITE_STATIC);
    if (rc != SQLITE_OK) {
        if (worker_id == 0) fprintf(stderr, "bind error: %s\n", sqlite3_errmsg(db_connection));
        throw sqlite3_errmsg(db_connection);
    }
    vector <int> result;
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        int doc_id = sqlite3_column_int(stmt, 0);
        result.push_back(doc_id);
    }
    sqlite3_finalize(stmt);
    if (worker_id == 0) fprintf(stderr, "query = %s result.size() = %d\n", token.c_str(), result.size());
    return SortedIndex(std::move(result), doc_count, false);
}

int* boolean_solve(const char* expr) {
    // suffix expression solve
    // parse space splited expression
    // expression = "a b c AND OR"

    vector < SortedIndex > stack;
    
    string s = expr;
    stringstream ss(s);
    string token;
    int pg_first, pg_last;
    ss >> pg_first >> pg_last;
    while (ss >> token) {
        if (worker_id == 0) fprintf(stderr, "token = %s\n", token.c_str());
        if (token == "AND") {
            auto a = std::move(stack.back());
            stack.pop_back();
            stack.back() &= a;
        } else if (token == "OR") {
            auto a = std::move(stack.back());
            stack.pop_back();
            stack.back() |= a;
        } else if (token == "NOT") {
            stack.back().negation();
        } else {
            stack.push_back(std::move(get_sorted_index(token)));
        }
    }
    // process for ['AND', [a, b, c]]
    while (stack.size() > 1) {
        auto a = std::move(stack.back());
        stack.pop_back();
        stack.back() &= a;
    }

    assert (stack.size() == 1);
    
    auto &a = stack.back();

    static int return_buffer[16][102];

    fprintf(stderr, "a.size() = %d\n", (int) a.size());
    return_buffer[worker_id][0] = a.size();
    int l = pg_first;
    int r = min(return_buffer[worker_id][0], pg_last);
    int len = max(r - l + 1, 0);
    return_buffer[worker_id][1] = len;
    assert(r - l <= 100);
    auto ret = a.extract(r);
    for (int i = 0; i < len; i++) {
        return_buffer[worker_id][i + 2] = ret[l + i - 1];
    }
    return return_buffer[worker_id];
}

#if defined(WIN32) || defined(_WIN32) || defined(__WIN32) && !defined(__CYGWIN__)
#define EXPORT extern "C" __declspec(dllexport)
#else
#define EXPORT extern "C"
#endif

EXPORT int init_cpp(int id, const char *dbfile) {
    return init(id, dbfile);
}

EXPORT int *boolean_solve_cpp(const char *expr) {
    return boolean_solve(expr);
}

EXPORT void finalize_cpp() {
    finalize();
}