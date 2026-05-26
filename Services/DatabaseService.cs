using System.Data;
using System.IO;
using Dapper;
using Microsoft.Data.Sqlite;
using Serilog;
using SmartSecurityIoT.Models;
using SmartSecurityIoT.Services.Interfaces;

namespace SmartSecurityIoT.Services;

public class DatabaseService : IDatabaseService
{
    private readonly string _connectionString;
    private readonly ILogger _logger = Log.ForContext<DatabaseService>();

    public DatabaseService()
    {
        var dbPath = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "SmartSecurityIoT",
            "security.db");

        Directory.CreateDirectory(Path.GetDirectoryName(dbPath)!);

        var password = Security.SecureConfig.DatabasePassword;
        _connectionString = $"Data Source={dbPath};Password={password}";
    }

    private IDbConnection CreateConnection()
    {
        return new SqliteConnection(_connectionString);
    }

    public async Task InitializeAsync()
    {
        using var connection = CreateConnection();
        connection.Open();

        const string createTables = """
            CREATE TABLE IF NOT EXISTS Users
            (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                FullName TEXT NOT NULL,
                Embedding BLOB NOT NULL,
                CreatedAt TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS IntrusionEvents
            (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                Snapshot BLOB NOT NULL,
                EventDate TEXT NOT NULL,
                LivenessPassed INTEGER NOT NULL
            );
            """;

        await connection.ExecuteAsync(createTables);
        _logger.Information("Database initialized at {ConnectionString}", _connectionString);
    }

    public async Task<int> AddUserAsync(User user)
    {
        using var connection = CreateConnection();
        const string sql = """
            INSERT INTO Users (FullName, Embedding, CreatedAt)
            VALUES (@FullName, @Embedding, @CreatedAt);
            SELECT last_insert_rowid();
            """;

        var id = await connection.ExecuteScalarAsync<int>(sql, new
        {
            user.FullName,
            user.Embedding,
            CreatedAt = user.CreatedAt.ToString("o")
        });

        _logger.Information("User added: {FullName} (ID: {Id})", user.FullName, id);
        return id;
    }

    public async Task<IEnumerable<User>> GetAllUsersAsync()
    {
        using var connection = CreateConnection();
        const string sql = "SELECT * FROM Users ORDER BY FullName";
        return await connection.QueryAsync<User>(sql);
    }

    public async Task<User?> GetUserByIdAsync(int id)
    {
        using var connection = CreateConnection();
        const string sql = "SELECT * FROM Users WHERE Id = @Id";
        return await connection.QueryFirstOrDefaultAsync<User>(sql, new { Id = id });
    }

    public async Task DeleteUserAsync(int id)
    {
        using var connection = CreateConnection();
        const string sql = "DELETE FROM Users WHERE Id = @Id";
        await connection.ExecuteAsync(sql, new { Id = id });
        _logger.Information("User deleted (ID: {Id})", id);
    }

    public async Task<int> LogIntrusionEventAsync(IntrusionEvent intrusionEvent)
    {
        using var connection = CreateConnection();
        const string sql = """
            INSERT INTO IntrusionEvents (Snapshot, EventDate, LivenessPassed)
            VALUES (@Snapshot, @EventDate, @LivenessPassed);
            SELECT last_insert_rowid();
            """;

        var id = await connection.ExecuteScalarAsync<int>(sql, new
        {
            intrusionEvent.Snapshot,
            EventDate = intrusionEvent.EventDate.ToString("o"),
            LivenessPassed = intrusionEvent.LivenessPassed ? 1 : 0
        });

        _logger.Warning("Intrusion event logged (ID: {Id}, Liveness: {Liveness})",
            id, intrusionEvent.LivenessPassed);
        return id;
    }

    public async Task<IEnumerable<IntrusionEvent>> GetRecentIntrusionEventsAsync(int count = 20)
    {
        using var connection = CreateConnection();
        const string sql = "SELECT * FROM IntrusionEvents ORDER BY EventDate DESC LIMIT @Count";
        return await connection.QueryAsync<IntrusionEvent>(sql, new { Count = count });
    }
}
