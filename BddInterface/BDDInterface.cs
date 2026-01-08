using System.Net;
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.AspNetCore.Mvc;
using Npgsql;
using NpgsqlTypes;

namespace BddInterface;

internal static class BddInterface
{
    private static NpgsqlDataSource dataSource;
    private static ILogger _logger;
    
    public static async Task Main(string[] args) {
        using ILoggerFactory factory = LoggerFactory.Create(builder => builder.AddConsole());
        _logger = factory.CreateLogger(nameof(BddInterface));
        
        WebApplicationBuilder builder = WebApplication.CreateBuilder(args);
        
        builder.Services.AddEndpointsApiExplorer();
        builder.Services.AddSwaggerGen();
        
        WebApplication app = builder.Build();
        
        // Configure the HTTP request pipeline.
        if (app.Environment.IsDevelopment()) {
            app.UseSwagger();
            app.UseSwaggerUI();
        }

        app.UseHttpsRedirection();

        const string host = "bdd";
        const string username = "api";
        const string password = "apisecretpassword";
        const string database = "logsdb";
        
        const string connectionString = $"Host={host};Username={username};Password={password};Database={database}";
        
        dataSource = NpgsqlDataSource.Create(connectionString);

        await using (NpgsqlCommand cmd = dataSource.CreateCommand("""
                                                                  CREATE TABLE IF NOT EXISTS logs (
                                                                    row_id bigserial not null,
                                                                    row_hash varchar(255) not null,
                                                                    row JSONB not null,
                                                                    inserted_at timestamp DEFAULT current_timestamp,
                                                                    PRIMARY KEY (row_id),
                                                                    CONSTRAINT row_unique UNIQUE(row_hash, row)
                                                                  )
                                                                  """))
        {
            await cmd.ExecuteNonQueryAsync();
        }
        
        app.MapPost("/logsreceive", async ([FromBody] string str) => await InsertLogs(str))
            .WithName("Receiving Logs")
            .WithOpenApi();
        
        app.MapGet("/search/{field}/{query:minlength(4)}/{orderby}/{limit:int?}/{offset:int?}", async (string field, string query, string orderby, int? limit, int? offset) =>
            {
                return await SearchLogs(field, query, orderby, limit, offset);
            }).WithName("Searching Logs")
            .WithOpenApi();

        app.Run();
        
    }


    private static async Task<string> SearchLogs(string field, string query, string orderby, int? limit, int? offset)
    {
        await using NpgsqlCommand cmd = dataSource.CreateCommand(
            "SELECT row FROM logs WHERE row->> $1 LIKE $2 ORDER BY row->> $3 LIMIT $4 OFFSET $5");
        cmd.Parameters.AddWithValue(field);
        cmd.Parameters.AddWithValue(query);
        cmd.Parameters.AddWithValue(orderby);
        cmd.Parameters.AddWithValue(limit.GetValueOrDefault(10));
        cmd.Parameters.AddWithValue(offset.GetValueOrDefault(0));
        NpgsqlDataReader reader = await cmd.ExecuteReaderAsync();
        List<JsonElement> data = [];
                
        while (await reader.ReadAsync())
        {
            data.Add(reader.GetFieldValue<JsonElement>(0));
        }

        return JsonSerializer.Serialize(data);
    }
    
    private static async Task<HttpStatusCode> InsertLogs(string str)
    {
        
        List<LogLine>? logLines;
        try {
            logLines = JsonSerializer.Deserialize<List<LogLine>>(str);
        } catch (JsonException e) {
            _logger.LogWarning(e, "An exception occured parsing the JSON content");
            return HttpStatusCode.BadRequest;
        }
        if (logLines == null) return HttpStatusCode.BadRequest;
                
        await using NpgsqlConnection conn = await dataSource.OpenConnectionAsync();

        _logger.LogInformation("Start inserting {RowCount} rows", logLines.Count);

        Guid id = Guid.NewGuid();
        
        // Créer une table temporaire
        await new NpgsqlCommand("""
                                BEGIN;
                                CREATE TEMPORARY TABLE logs_temp
                                ON COMMIT DROP
                                AS
                                SELECT * 
                                FROM logs
                                WITH NO DATA;
                                """, conn).ExecuteNonQueryAsync();
        
        // On copie vers notre table temporaire
        await using NpgsqlBinaryImporter writer = await conn.
            BeginBinaryImportAsync("COPY logs_temp (row_hash, row) FROM STDIN (FORMAT BINARY)");

        foreach (LogLine logLine in logLines)
        {
            await writer.StartRowAsync();
            await writer.WriteAsync(logLine.RowHash, NpgsqlDbType.Varchar);
            await writer.WriteAsync(logLine.RowContent, NpgsqlDbType.Jsonb);
        }
        await writer.CompleteAsync();
        await writer.CloseAsync();
        
        // Copier depuis table temporaire vers table principale
        await new NpgsqlCommand("""
                                 INSERT INTO logs (row_hash, row)
                                 SELECT row_hash, row
                                 FROM logs_temp
                                 ON CONFLICT DO NOTHING;
                                 COMMIT;
                                 """, conn).ExecuteNonQueryAsync();

        await conn.CloseAsync();
                
        _logger.LogInformation("Successfully inserted {RowCount} rows", logLines.Count);
                
        return HttpStatusCode.OK;
    }
}

internal record LogLine(
    [property: JsonPropertyName("rowHash")] string RowHash,
    [property: JsonPropertyName("rowContent")] JsonElement RowContent
);